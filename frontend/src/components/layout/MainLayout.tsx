'use client';

import React, { useState } from 'react';
import { ChatArea } from '@/components/chat/ChatArea';
import { WorkspaceArea } from '@/components/workspace/WorkspaceArea';
import { DragDropOverlay } from '@/components/upload/DragDropOverlay';

export function MainLayout() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedInvoices, setUploadedInvoices] = useState<File[]>([]);

  const handleFileDrop = async (files: File[]) => {
    setIsProcessing(true);
    
    // Simulate processing delay
    setTimeout(() => {
      setUploadedInvoices(prev => [...prev, ...files]);
      setIsProcessing(false);
    }, 8000); // 8 seconds for full simulation
  };

  return (
    <div className="flex h-screen bg-gray-50 relative">
      {/* Chat area - left side (even narrower) */}
      <div className="w-1/3 border-r border-gray-200">
        <ChatArea />
      </div>
      
      {/* Workspace area - right side (wider) */}
      <div className="w-2/3">
        <WorkspaceArea uploadedInvoices={uploadedInvoices} />
      </div>

      {/* Drag Drop Overlay */}
      <DragDropOverlay 
        onFileDrop={handleFileDrop}
        isProcessing={isProcessing}
      />
    </div>
  );
}