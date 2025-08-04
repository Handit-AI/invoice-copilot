// Core types for InvoiceCopilot
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  type?: 'text' | 'chart' | 'table' | 'code' | 'tsx';
  metadata?: Record<string, any>;
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'area' | 'scatter';
  data: any[];
  options: Record<string, any>;
  title?: string;
}

export interface AppState {
  // UI State
  isGenerating: boolean;
  
  // Data State
  messages: Message[];
  currentChart?: ChartConfig;
  uploadedInvoices: File[];
  
  // Dynamic Workspace State
  workspaceContent: 'default' | 'expenses-report' | null;
  
  // Session State
  sessionId: string;
}

// Component Props
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// API Response types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface GenerateChartRequest {
  query: string;
  invoiceIds?: string[];
  chartType?: ChartConfig['type'];
}

export interface UploadInvoiceResponse {
  invoiceId: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  message: string;
}