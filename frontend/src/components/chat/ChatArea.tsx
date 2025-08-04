'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Image, FileText, TrendingUp, BarChart } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Card } from '@/components/ui/Card';
import { LoadingDots } from '@/components/ui/LoadingSpinner';
import { NextStepsAnimation } from './NextStepsAnimation';
import { cn, formatDateTime } from '@/lib/utils';

export function ChatArea() {
  const { state, addMessage, setGenerating, setChart, setWorkspaceContent } = useApp();
  const { messages, isGenerating } = state;
  const [input, setInput] = useState('');
  const [showNextSteps, setShowNextSteps] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    // Add a small delay to ensure layout has stabilized before scrolling
    const scrollTimer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
    
    return () => clearTimeout(scrollTimer);
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isGenerating) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    addMessage({
      content: userMessage,
      role: 'user',
      type: 'text',
    });

    // Check if this is a request for expenses report
    const isExpensesRequest = /show me expenses by category for q1/i.test(userMessage.toLowerCase());

    // Start generating response
    setGenerating(true);

    try {
      // Handle expenses report request locally with visual streaming effect
      if (isExpensesRequest) {
        // Show next steps animation
        setShowNextSteps(true);
        
        // Complete after animation finishes (approximately 4 seconds)
        setTimeout(() => {
          setShowNextSteps(false);
          
          // Add final confirmation message first
          addMessage({
            content: 'I\'ve generated a comprehensive Q1 2025 expenses analysis by category. The report includes detailed breakdowns, performance metrics, and visual representations of your spending patterns from January to March 2025. You can see the full report with charts and data in the workspace area.',
            role: 'assistant',
            type: 'text',
          });
          
          // Enable dynamic workspace after a short delay to allow message rendering
          setTimeout(() => {
            if (typeof window !== 'undefined' && (window as any).setUseDynamicContent) {
              (window as any).setUseDynamicContent(true);
            }
            setWorkspaceContent('expenses-report');
          }, 300);
          
          setGenerating(false);
        }, 4500); // Allow time for all steps to complete
        
        return; // Exit early for expenses report
      }

      // Call backend API to process other chat messages
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Check if TSX was generated and dynamic content should be enabled
      if (data.success && data.dynamic_content_enabled) {
        // Enable dynamic workspace content
        if (typeof window !== 'undefined' && (window as any).setUseDynamicContent) {
          (window as any).setUseDynamicContent(true);
        }
      }
      
      // Add assistant response
      addMessage({
        content: data.response,
        role: 'assistant',
        type: (data.action === 'tsx_generated' ? 'tsx' : 'text') as 'text' | 'chart' | 'table' | 'code' | 'tsx',
        metadata: data.action === 'tsx_generated' ? { 
          action: data.action,
          dynamic_content_enabled: data.dynamic_content_enabled,
          error_check_results: data.error_check_results
        } : undefined
      });
      
    } catch (error) {
      console.error('Error calling backend:', error);
      
      // Fallback to default behavior if backend is not available
      const isUIKeyword = /\b(hello world|landing page|component|button|form|add text|create|design|ui|interface|layout|card|modal|navbar|footer|sidebar|dashboard)\b/i.test(userMessage.toLowerCase());
      
      if (isUIKeyword) {
        addMessage({
          content: 'I can generate TSX components and UI elements for you! However, the TSX Agent backend is not currently available. Please start the FastAPI server with `python start_server.py` in the backend directory.',
          role: 'assistant',
          type: 'text',
        });
      } else {
        addMessage({
          content: 'I can help you create React TSX components, UI layouts, and dynamic interfaces. Try asking me to "create a landing page" or "add Hello World text"! (Note: TSX Agent backend connection failed)',
          role: 'assistant',
          type: 'text',
        });
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Chat Header */}
      <div className="border-b border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              Data Visualization Chat
            </h2>
            <p className="text-sm text-gray-500">
              Ask me to create charts, analyze data, and generate visualizations
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-xs text-gray-500">AI Copilot Ready</span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto bg-gray-50/50 p-4">
        <div className="mx-auto max-w-2xl space-y-4">
          {messages.length === 0 ? (
            <WelcomeScreen />
          ) : (
            messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))
          )}
          
          {isGenerating && !showNextSteps && (
            <div className="flex justify-start">
              <Card className="chat-bubble-assistant bg-white border shadow-sm">
                <div className="flex items-center space-x-2">
                  <LoadingDots />
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              </Card>
            </div>
          )}
          
          {showNextSteps && (
            <div className="flex justify-start">
              <div className="max-w-[80%]">
                <NextStepsAnimation />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleSubmit} className="mx-auto max-w-2xl">
          <div className="flex items-end gap-2">
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me to create charts, analyze data, or generate visualizations..."
                className="min-h-[44px] max-h-32 resize-none pr-20"
                disabled={isGenerating}
              />
              
              {/* Attachment button - positioned inside textarea */}
              <div className="absolute bottom-2 right-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 p-0"
                  disabled={isGenerating}
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {/* Send button - outside textarea */}
            <Button
              type="submit"
              disabled={!input.trim() || isGenerating}
              size="icon"
              className="h-11 w-11 flex-shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="mt-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
            <div className="text-xs text-gray-500">
              <span>Press Enter to send, Shift+Enter for new line</span>
            </div>
            <div className="text-xs text-gray-500">
              {input.length}/2000
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

function ChatMessage({ message }: { message: any }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div className={cn(
        "max-w-[80%] space-y-2",
        isUser ? "order-2" : "order-1"
      )}>
        <Card className={cn(
          "p-4 shadow-sm",
          isUser 
            ? "bg-primary text-white ml-auto"
            : "bg-white border"
        )}>
          <div className="prose prose-sm max-w-none">
            <p className={cn("mb-0 whitespace-pre-wrap", isUser ? "text-white" : "text-gray-900")}>
              {message.content}
            </p>
          </div>
        </Card>
        
        <div className={cn(
          "flex items-center space-x-2 text-xs text-gray-500",
          isUser ? "justify-end" : "justify-start"
        )}>
          <span>{isUser ? 'You' : 'AI Assistant'}</span>
          <span>•</span>
          <span>{formatDateTime(message.timestamp)}</span>
        </div>
      </div>
    </div>
  );
}

function WelcomeScreen() {
  const { addMessage } = useApp();
  
  const quickActions = [
    {
      title: "Upload your Invoices",
      description: "Batch process, upload multiple invoices at once",
      icon: FileText,
      query: "Show me expenses by category for Q1"
    },
    {
      title: "Create a bar chart",
      description: "Generate a bar chart with sample data",
      icon: BarChart,
      query: "Create a bar chart showing quarterly sales data"
    },
    {
      title: "Monthly trend analysis",
      description: "Generate a line chart showing trends over time",
      icon: TrendingUp,
      query: "Create a line chart showing monthly revenue trends"
    }
   
  ];

  const handleQuickAction = (item: any) => {
    if (item.query) {
      addMessage({
        content: item.query,
        role: 'user',
        type: 'text',
      });
    }
  };

  return (
    <div className="text-center space-y-6 py-8">
      <div className="space-y-2">
        <h3 className="text-xl font-semibold text-gray-900">
          Welcome to InvoiceCopilot! 👋
        </h3>
        <p className="text-gray-600">
          I'm your AI assistant for data visualization. I can help you create charts, 
          analyze data patterns, and generate interactive visualizations in real-time, based on your invoices.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Card 
              key={index}
              className="p-4 cursor-pointer transition-all hover:shadow-md hover:scale-105"
              onClick={() => handleQuickAction(action)}
            >
              <div className="flex flex-col items-center text-center space-y-2">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h4 className="font-medium text-sm text-gray-900">
                    {action.title}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">
                    {action.description}
                  </p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="text-sm text-gray-500">
        <p>Try asking something like:</p>
        <div className="flex flex-wrap justify-center gap-2 mt-2">
          {[
            "Show me expenses by category for Q1",
            "Generate a quarterly revenue analysis",
            "Create a sales performance chart"
          ].map((example, index) => (
            <button
              key={index}
              onClick={() => addMessage({ content: example, role: 'user', type: 'text' })}
              className="px-3 py-1 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
            >
              "{example}"
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}