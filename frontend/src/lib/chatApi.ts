import { APIResponse } from '@/types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface ChatMessage {
  id: string;
  content: string;
  timestamp: Date;
  sender: 'user' | 'assistant';
  isLoading?: boolean;
}

export interface ChatRequest {
  message: string;
  workspace_dir?: string;
  max_iterations?: number;
}

export interface ChatResponse {
  success: boolean;
  message: string;
  response: string;
  workspace_dir: string;
  timestamp: string;
  error?: string;
}

export async function sendChatMessage(
  message: string,
  workspaceDir: string = 'frontend/src/components/workspace'
): Promise<ChatResponse> {
  try {
    console.log(`📤 Sending chat message to backend: "${message}"`);
    
    const requestBody: ChatRequest = {
      message,
      workspace_dir: workspaceDir,
      max_iterations: 10
    };

    const response = await fetch(`${BACKEND_URL}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const result: ChatResponse = await response.json();
    
    console.log(`✅ Received chat response:`, result);
    
    return result;

  } catch (error) {
    console.error('❌ Error sending chat message:', error);
    
    return {
      success: false,
      message,
      response: `Failed to send message: ${error}`,
      workspace_dir: workspaceDir,
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export function createChatMessage(
  content: string,
  sender: 'user' | 'assistant',
  isLoading: boolean = false
): ChatMessage {
  return {
    id: crypto.randomUUID(),
    content,
    timestamp: new Date(),
    sender,
    isLoading
  };
}

export function updateChatMessage(
  message: ChatMessage,
  updates: Partial<ChatMessage>
): ChatMessage {
  return {
    ...message,
    ...updates
  };
}