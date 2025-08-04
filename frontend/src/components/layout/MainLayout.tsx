'use client';

import React, { useState } from 'react';
import { ChatArea } from '@/components/chat/ChatArea';
import { WorkspaceArea } from '@/components/workspace/WorkspaceArea';
import { DragDropOverlay } from '@/components/upload/DragDropOverlay';
import { useApp } from '@/contexts/AppContext';
import { uploadAndProcessDocuments, DocumentUploadProgress } from '@/lib/documentApi';

export function MainLayout() {
  const { addUploadedInvoices } = useApp();
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState<DocumentUploadProgress | null>(null);

  const handleFileDrop = async (files: File[]) => {
    setIsProcessing(true);
    setProcessingProgress(null);
    
    try {
      // Call real backend API
      const result = await uploadAndProcessDocuments(
        files,
        'processed', // output directory
        (progress) => {
          setProcessingProgress(progress);
        }
      );

      // Log successful result
      console.log('✅ Document processing completed:', result);
      
      // Add files to app state (for UI display)
      addUploadedInvoices(files);
      
      // Show completion message
      setProcessingProgress({
        stage: 'completed',
        progress: 100,
        message: `Successfully processed ${result.successful} of ${result.total_files} documents!`,
        details: result
      });

      // Auto-hide after showing success for a moment
      setTimeout(() => {
        setIsProcessing(false);
        setProcessingProgress(null);
      }, 2000);

    } catch (error) {
      console.error('❌ Document processing failed:', error);
      
      // Show error state
      setProcessingProgress({
        stage: 'error',
        progress: 0,
        message: `Failed to process documents: ${error}`,
        details: { error }
      });

      // Auto-hide error after 5 seconds
      setTimeout(() => {
        setIsProcessing(false);
        setProcessingProgress(null);
      }, 5000);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 relative">
      {/* Chat area - left side (even narrower) */}
      <div className="w-1/3 border-r border-gray-200">
        <ChatArea />
      </div>
      
      {/* Workspace area - right side (wider) */}
      <div className="w-2/3">
        <WorkspaceArea />
      </div>

      {/* Drag Drop Overlay */}
      <DragDropOverlay 
        onFileDrop={handleFileDrop}
        isProcessing={isProcessing}
        processingProgress={processingProgress}
      />
    </div>
  );
}