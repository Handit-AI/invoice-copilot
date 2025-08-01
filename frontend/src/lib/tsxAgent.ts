/**
 * TSX Agent Integration for Frontend
 * 
 * This module provides functions to communicate with the TSX Agent backend
 * and manage dynamic content in the workspace.
 */

const TSX_AGENT_BASE_URL = process.env.NEXT_PUBLIC_TSX_AGENT_URL || 'http://localhost:8000';

export interface ChatResponse {
  success: boolean;
  response: string;
  action: 'tsx_generated' | 'no_tsx_needed' | 'error';
  dynamic_content_enabled: boolean;
  message: string;
}

export interface DynamicContentResponse {
  success: boolean;
  content: string;
  file_path: string;
  exists: boolean;
  message?: string;
}

export interface AgentHistoryResponse {
  success: boolean;
  history: Array<{
    tool: string;
    reason: string;
    params: Record<string, any>;
    result: any;
    timestamp: string;
  }>;
  total_actions: number;
}

/**
 * Send a chat message to the TSX Agent and get a response.
 */
export async function sendChatToAgent(message: string): Promise<ChatResponse> {
  try {
    const response = await fetch(`${TSX_AGENT_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending chat to agent:', error);
    return {
      success: false,
      response: `Error communicating with TSX Agent: ${error}`,
      action: 'error',
      dynamic_content_enabled: false,
      message: `Error: ${error}`,
    };
  }
}

/**
 * Get the current dynamic workspace content.
 */
export async function getDynamicContent(): Promise<DynamicContentResponse> {
  try {
    const response = await fetch(`${TSX_AGENT_BASE_URL}/api/dynamic-content`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting dynamic content:', error);
    return {
      success: false,
      content: '',
      file_path: '',
      exists: false,
      message: `Error: ${error}`,
    };
  }
}

/**
 * Reset the dynamic content to the default template.
 */
export async function resetDynamicContent(): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${TSX_AGENT_BASE_URL}/api/dynamic-content/reset`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error resetting dynamic content:', error);
    return {
      success: false,
      message: `Error: ${error}`,
    };
  }
}

/**
 * Get the agent's action history.
 */
export async function getAgentHistory(): Promise<AgentHistoryResponse> {
  try {
    const response = await fetch(`${TSX_AGENT_BASE_URL}/api/agent/history`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting agent history:', error);
    return {
      success: false,
      history: [],
      total_actions: 0,
    };
  }
}

/**
 * Clear the agent's action history.
 */
export async function clearAgentHistory(): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${TSX_AGENT_BASE_URL}/api/agent/clear-history`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error clearing agent history:', error);
    return {
      success: false,
      message: `Error: ${error}`,
    };
  }
}

/**
 * Check if the TSX Agent service is healthy.
 */
export async function checkAgentHealth(): Promise<{ status: string; service: string; working_directory: string } | null> {
  try {
    const response = await fetch(`${TSX_AGENT_BASE_URL}/api/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking agent health:', error);
    return null;
  }
}

/**
 * Enable or disable dynamic content display.
 * This function uses the global function exposed by WorkspaceArea.tsx
 */
export function setDynamicContentEnabled(enabled: boolean): void {
  if (typeof window !== 'undefined' && (window as any).setUseDynamicContent) {
    (window as any).setUseDynamicContent(enabled);
  } else {
    console.warn('setUseDynamicContent function not available. Make sure WorkspaceArea is mounted.');
  }
}

/**
 * Process a UI request: send to agent and enable dynamic content if TSX was generated.
 */
export async function processUIRequest(message: string): Promise<ChatResponse> {
  const response = await sendChatToAgent(message);
  
  if (response.success && response.dynamic_content_enabled) {
    // Enable dynamic content display
    setDynamicContentEnabled(true);
  }
  
  return response;
}

/**
 * Utility function to determine if a message is likely a UI request.
 */
export function isUIRequest(message: string): boolean {
  const uiKeywords = [
    'hello world', 'landing page', 'component', 'button', 'form',
    'add text', 'create', 'design', 'ui', 'interface', 'layout',
    'card', 'modal', 'navbar', 'footer', 'sidebar', 'dashboard',
    'table', 'chart', 'graph', 'menu', 'header', 'content'
  ];
  
  return uiKeywords.some(keyword => message.toLowerCase().includes(keyword));
}