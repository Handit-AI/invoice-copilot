'use client';

import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { AppState, Message, ChartConfig } from '@/types';

// Initial state
const initialState: AppState = {
  isGenerating: false,
  messages: [],
  sessionId: `session_${Date.now()}`,
};

// Action types
type AppAction = 
  | { type: 'SET_GENERATING'; payload: boolean }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'UPDATE_MESSAGES'; payload: Message[] }
  | { type: 'SET_CHART'; payload: ChartConfig | undefined }
  | { type: 'RESET_SESSION' };

// Reducer
function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_GENERATING':
      return { ...state, isGenerating: action.payload };
    
    case 'ADD_MESSAGE':
      return { 
        ...state, 
        messages: [...state.messages, action.payload] 
      };
    
    case 'UPDATE_MESSAGES':
      return { ...state, messages: action.payload };
    
    case 'SET_CHART':
      return { ...state, currentChart: action.payload };
    
    case 'RESET_SESSION':
      return {
        ...initialState,
        sessionId: `session_${Date.now()}`,
      };
    
    default:
      return state;
  }
}

// Context
interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  
  // Helper functions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setGenerating: (generating: boolean) => void;
  setChart: (chart: ChartConfig | undefined) => void;
  resetSession: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Provider component
export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Helper functions
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };
    dispatch({ type: 'ADD_MESSAGE', payload: newMessage });
  }, []);

  const setGenerating = useCallback((generating: boolean) => {
    dispatch({ type: 'SET_GENERATING', payload: generating });
  }, []);

  const setChart = useCallback((chart: ChartConfig | undefined) => {
    dispatch({ type: 'SET_CHART', payload: chart });
  }, []);

  const resetSession = useCallback(() => {
    dispatch({ type: 'RESET_SESSION' });
  }, []);

  const value: AppContextType = {
    state,
    dispatch,
    addMessage,
    setGenerating,
    setChart,
    resetSession,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// Hook para usar el contexto
export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}