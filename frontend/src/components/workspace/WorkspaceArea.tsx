'use client';

import React, { useState } from 'react';
import { BarChart3, Download, RefreshCw, Maximize2, FileText } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { DynamicWorkspace } from './DynamicWorkspace';

export function WorkspaceArea() {
  const { state } = useApp();
  const { isGenerating, currentChart, uploadedInvoices, workspaceContent } = state;
  
  // Flag to determine whether to show dynamic content
  // This can be controlled by the chat/AI system
  const [useDynamicContent, setUseDynamicContent] = useState(false);
  
  // Expose the setter function globally for the AI agent to use
  React.useEffect(() => {
    (window as any).setUseDynamicContent = setUseDynamicContent;
    return () => {
      delete (window as any).setUseDynamicContent;
    };
  }, []);

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Workspace Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100">
              <BarChart3 className="h-4 w-4 text-gray-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Generated Visualization
              </h2>
              <p className="text-sm text-gray-500">
                Real-time charts and data visualizations
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Invoice Icons - shown when invoices are uploaded */}
            {uploadedInvoices.length > 0 && (
              <InvoiceIcons invoices={uploadedInvoices} />
            )}
            
            {/* Action Buttons */}
            <div className="flex items-center gap-1">
              <Button variant="outline" size="sm" disabled={!currentChart} className="px-2">
                <RefreshCw className="h-4 w-4" />
                <span className="ml-1 hidden lg:inline">Regenerate</span>
              </Button>
              <Button variant="outline" size="sm" disabled={!currentChart} className="px-2">
                <Download className="h-4 w-4" />
                <span className="ml-1 hidden lg:inline">Export</span>
              </Button>
              <Button variant="outline" size="sm" disabled={!currentChart} className="px-2">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Workspace Content */}
      <div className="flex-1 p-6 bg-gray-50">
        {(useDynamicContent || workspaceContent) ? (
          <DynamicWorkspace />
        ) : isGenerating ? (
          <GeneratingView />
        ) : currentChart ? (
          <ChartView chart={currentChart} />
        ) : (
          <EmptyWorkspaceView />
        )}
      </div>
    </div>
  );
}

function EmptyWorkspaceView() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center space-y-4 max-w-md">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
          <BarChart3 className="h-8 w-8 text-gray-400" />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-gray-900">
            Ready to Generate
          </h3>
          <p className="text-gray-500">
            Your charts, tables, and visualizations will appear here in real-time. 
            Start by asking me to create visualizations in the chat.
          </p>
        </div>
        
        <div className="space-y-3 text-sm text-gray-500">
          <p className="font-medium">What I can create:</p>
          <div className="grid grid-cols-1 gap-2 text-left">
            {[
              '📊 Interactive charts and graphs',
              '📋 Data tables with filtering',
              '📈 Trend analysis visualizations',
              '💾 Exportable chart summaries'
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

function GeneratingView() {
  return (
    <div className="flex h-full items-center justify-center">
      <Card className="w-full max-w-md p-8">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" />
                      <div className="space-y-2">
              <h3 className="text-lg font-medium text-gray-900">
                Generating Your Visualization
              </h3>
              <p className="text-gray-500">
                Processing your request and creating the chart...
              </p>
            </div>
            
            <div className="space-y-2 text-sm text-gray-400">
              <div className="flex items-center justify-center space-x-2">
                <div className="h-2 w-2 rounded-full bg-green-500"></div>
                <span>Processing data</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <div className="h-2 w-2 rounded-full bg-yellow-500 animate-pulse"></div>
                <span>Generating visualization</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <div className="h-2 w-2 rounded-full bg-gray-300"></div>
                <span>Preparing export options</span>
              </div>
            </div>
        </div>
      </Card>
    </div>
  );
}

function ChartView({ chart }: { chart: any }) {
  return (
    <div className="h-full space-y-4">
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{chart.title || 'Generated Chart'}</span>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <span className="capitalize">{chart.type} Chart</span>
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
            </div>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="h-[calc(100%-80px)]">
          {/* Placeholder for actual chart implementation */}
          <div className="flex h-full items-center justify-center border-2 border-dashed border-gray-200 rounded-lg">
            <div className="text-center space-y-2">
              <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
              <div className="space-y-1">
                <p className="font-medium text-gray-900">
                  {chart.type.charAt(0).toUpperCase() + chart.type.slice(1)} Chart
                </p>
                <p className="text-sm text-gray-500">
                  Chart implementation will be rendered here
                </p>
                <p className="text-xs text-gray-400">
                  Using Plotly.js or Chart.js for interactive visualizations
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Chart Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">Chart generated from:</span>
          <span className="text-sm font-medium text-gray-900">Sample data</span>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="flex-1 sm:flex-none">
            Edit Chart
          </Button>
          <Button variant="outline" size="sm" className="flex-1 sm:flex-none">
            Save to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}

function InvoiceIcons({ invoices }: { invoices: File[] }) {
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});

  // Create preview URLs for images
  React.useEffect(() => {
    const urls: Record<string, string> = {};
    
    invoices.forEach((file, index) => {
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file);
        urls[`${file.name}-${index}`] = url;
      }
    });
    
    setImageUrls(urls);
    
    // Cleanup
    return () => {
      Object.values(urls).forEach(url => URL.revokeObjectURL(url));
    };
  }, [invoices]);

  const getFileIcon = (file: File, index: number) => {
    const key = `${file.name}-${index}`;
    
    if (file.type.startsWith('image/') && imageUrls[key]) {
      return (
        <div className="w-6 h-6 rounded-sm overflow-hidden bg-gray-100 border border-gray-200">
          <img
            src={imageUrls[key]}
            alt={file.name}
            className="w-full h-full object-cover"
          />
        </div>
      );
    }
    
    // PDF or other file types
    return (
      <div className="w-6 h-6 rounded-sm bg-red-50 border border-red-200 flex items-center justify-center">
        <FileText className="h-3 w-3 text-red-500" />
      </div>
    );
  };

  if (invoices.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      {/* Invoice Icons Stack */}
      <div className="flex items-center -space-x-1">
        {invoices.slice(0, 3).map((file, index) => (
          <div
            key={`${file.name}-${index}`}
            className="relative z-10"
            style={{ zIndex: 3 - index }}
            title={file.name}
          >
            {getFileIcon(file, index)}
          </div>
        ))}
        
        {/* Show count if more than 3 files */}
        {invoices.length > 3 && (
          <div className="w-6 h-6 rounded-sm bg-gray-100 border border-gray-300 flex items-center justify-center">
            <span className="text-xs font-medium text-gray-600">
              +{invoices.length - 3}
            </span>
          </div>
        )}
      </div>
      
      {/* Counter */}
      <div className="text-sm text-gray-500">
        {invoices.length} invoice{invoices.length !== 1 ? 's' : ''} uploaded
      </div>
    </div>
  );
}