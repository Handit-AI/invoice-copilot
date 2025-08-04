'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, Calendar, Download, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface ExpenseCategory {
  category: string;
  amount: number;
  percentage: number;
  change: number;
  color: string;
}

// Dummy data for Q1 2025 expenses
const expenseData: ExpenseCategory[] = [
  { category: 'Office Supplies', amount: 52300, percentage: 29.2, change: 18.5, color: 'bg-blue-500' },
  { category: 'Travel & Entertainment', amount: 41850, percentage: 23.4, change: 9.6, color: 'bg-green-500' },
  { category: 'Software & Licenses', amount: 34200, percentage: 19.1, change: 14.8, color: 'bg-purple-500' },
  { category: 'Marketing', amount: 28600, percentage: 16.0, change: 13.0, color: 'bg-orange-500' },
  { category: 'Utilities', amount: 13950, percentage: 7.8, change: 9.4, color: 'bg-red-500' },
  { category: 'Professional Services', amount: 8100, percentage: 4.5, change: -2.4, color: 'bg-yellow-500' }
];

const totalExpenses = expenseData.reduce((sum, item) => sum + item.amount, 0);

interface StreamingContentProps {
  isVisible: boolean;
  delay?: number;
  children: React.ReactNode;
}

function StreamingContent({ isVisible, delay = 0, children }: StreamingContentProps) {
  const [shouldShow, setShouldShow] = useState(false);

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => setShouldShow(true), delay);
      return () => clearTimeout(timer);
    } else {
      setShouldShow(false);
    }
  }, [isVisible, delay]);

  return (
    <div className={`transition-all duration-500 ${
      shouldShow ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
    }`}>
      {children}
    </div>
  );
}

interface TypewriterTextProps {
  text: string;
  speed?: number;
  startDelay?: number;
  isActive: boolean;
}

function TypewriterText({ text, speed = 50, startDelay = 0, isActive }: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!isActive) {
      setDisplayedText('');
      setCurrentIndex(0);
      return;
    }

    const startTimer = setTimeout(() => {
      if (currentIndex < text.length) {
        const timer = setTimeout(() => {
          setDisplayedText(text.slice(0, currentIndex + 1));
          setCurrentIndex(currentIndex + 1);
        }, speed);
        return () => clearTimeout(timer);
      }
    }, startDelay);

    return () => clearTimeout(startTimer);
  }, [text, speed, currentIndex, isActive, startDelay]);

  return <span>{displayedText}</span>;
}

export function ExpensesReport() {
  const [streamingStage, setStreamingStage] = useState(0);

  useEffect(() => {
    // Start streaming effect
    const stages = [
      { stage: 1, delay: 200 },  // Header
      { stage: 2, delay: 800 },  // Summary cards
      { stage: 3, delay: 1400 }, // Chart header
      { stage: 4, delay: 2000 }, // Chart content
      { stage: 5, delay: 2600 }, // Table header
      { stage: 6, delay: 3200 }, // Table rows (one by one)
    ];

    stages.forEach(({ stage, delay }) => {
      setTimeout(() => setStreamingStage(stage), delay);
    });
  }, []);

  return (
    <div className="h-full space-y-6">
      {/* Header */}
      <StreamingContent isVisible={streamingStage >= 1}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              <TypewriterText 
                text="Q1 2025 Expense Analysis by Category" 
                speed={60}
                isActive={streamingStage >= 1}
              />
            </h1>
            <p className="text-gray-600 mt-1">
              <StreamingContent isVisible={streamingStage >= 1} delay={1500}>
                Comprehensive breakdown of expenses from January to March 2025
              </StreamingContent>
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-1" />
              Refresh
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </div>
        </div>
      </StreamingContent>

      {/* Summary Cards */}
      <StreamingContent isVisible={streamingStage >= 2} delay={100}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <DollarSign className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Expenses</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${totalExpenses.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Monthly</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${Math.round(totalExpenses / 3).toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Calendar className="h-8 w-8 text-purple-600" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Reporting Period</p>
                  <p className="text-lg font-bold text-gray-900">Q1 2025</p>
                  <p className="text-sm text-gray-500">Jan - Mar</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </StreamingContent>

      {/* Chart Section */}
      <StreamingContent isVisible={streamingStage >= 3} delay={200}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              <TypewriterText 
                text="Expense Distribution by Category" 
                speed={40}
                isActive={streamingStage >= 3}
              />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StreamingContent isVisible={streamingStage >= 4} delay={100}>
              <div className="space-y-4">
                {expenseData.map((item, index) => (
                  <StreamingContent 
                    key={item.category} 
                    isVisible={streamingStage >= 4} 
                    delay={index * 200}
                  >
                    <div className="grid grid-cols-12 items-center gap-4">
                      <div className="col-span-5 flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded ${item.color}`}></div>
                        <span className="font-medium text-gray-900">{item.category}</span>
                      </div>
                      <div className="col-span-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${item.color} transition-all duration-1000 ease-out`}
                            style={{ 
                              width: streamingStage >= 4 ? `${item.percentage}%` : '0%',
                              transitionDelay: `${index * 200}ms`
                            }}
                          ></div>
                        </div>
                      </div>
                      <div className="col-span-2 text-center">
                        <span className="text-sm text-gray-600 tabular-nums">{item.percentage}%</span>
                      </div>
                      <div className="col-span-2 text-right">
                        <span className="font-semibold text-gray-900 tabular-nums">
                          ${item.amount.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </StreamingContent>
                ))}
              </div>
            </StreamingContent>
          </CardContent>
        </Card>
      </StreamingContent>



      {/* Generated timestamp */}
      <StreamingContent isVisible={streamingStage >= 6} delay={800}>
        <div className="text-center text-sm text-gray-500">
          <p>
            Report generated on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
          </p>
        </div>
      </StreamingContent>
    </div>
  );
}