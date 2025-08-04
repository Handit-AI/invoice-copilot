import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { ExpensesReport } from './ExpensesReport';

export function DynamicWorkspace() {
  const { state } = useApp();
  const { workspaceContent } = state;

  // Render specific content based on workspaceContent state
  if (workspaceContent === 'expenses-report') {
    return <ExpensesReport />;
  }

  // Default content when no specific content is set
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center space-y-4">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
          <span className="text-2xl">🤖</span>
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-gray-900">
            AI-Generated Content Area
          </h3>
          <p className="text-gray-500">
            This area will display AI-generated reports, charts, and visualizations based on your requests.
            Try asking for specific reports or data analysis!
          </p>
        </div>
        
        <div className="space-y-3 text-sm text-gray-500">
          <p className="font-medium">Try asking for:</p>
          <div className="grid grid-cols-1 gap-2 text-left max-w-sm mx-auto">
            {[
              '📊 "Show me expenses by category for Q1"',
              '📈 "Generate revenue analysis"',
              '📋 "Create monthly report"',
              '💰 "Analyze profit margins"'
            ].map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}