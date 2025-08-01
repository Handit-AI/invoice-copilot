'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Lottie from 'lottie-react';
import { Upload, FileText, Check, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import animationData from '@/assets/animations/scanning-document.json';

interface DragDropOverlayProps {
  onFileDrop: (files: File[]) => void;
  isProcessing: boolean;
}

interface ProcessingStep {
  id: string;
  label: string;
  status: 'pending' | 'processing' | 'completed';
  icon: React.ComponentType<{ className?: string }>;
}

export function DragDropOverlay({ onFileDrop, isProcessing }: DragDropOverlayProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([]);

  const initializeSteps = useCallback((fileCount: number) => {
    const steps: ProcessingStep[] = [
      {
        id: 'upload',
        label: `Uploading ${fileCount} file${fileCount > 1 ? 's' : ''}...`,
        status: 'pending',
        icon: Upload
      },
      {
        id: 'process',
        label: 'Processing Invoices',
        status: 'pending',
        icon: FileText
      },
      {
        id: 'ocr',
        label: 'Extracting Data with Advanced OCR',
        status: 'pending',
        icon: FileText
      },
      {
        id: 'vector',
        label: 'Uploading Invoice to Vector Store',
        status: 'pending',
        icon: Upload
      }
    ];
    setProcessingSteps(steps);
  }, []);

  useEffect(() => {
    if (isProcessing && files.length > 0) {
      initializeSteps(files.length);
      setCurrentStep(0);

      // Simulate step progression
      const stepInterval = setInterval(() => {
        setCurrentStep(prev => {
          const nextStep = prev + 1;
          
          // Update step statuses
          setProcessingSteps(steps => 
            steps.map((step, index) => ({
              ...step,
              status: index < nextStep ? 'completed' : 
                     index === nextStep ? 'processing' : 'pending'
            }))
          );

          if (nextStep >= 4) {
            clearInterval(stepInterval);
            return nextStep;
          }
          return nextStep;
        });
      }, 1800); // 1.8 seconds per step

      return () => clearInterval(stepInterval);
    }
  }, [isProcessing, files.length, initializeSteps]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Only hide overlay if leaving the main container
    if (e.currentTarget.contains(e.relatedTarget as Node)) return;
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter(file => 
      file.type === 'application/pdf' || 
      file.type.startsWith('image/') ||
      file.name.toLowerCase().endsWith('.pdf') ||
      file.name.toLowerCase().endsWith('.png') ||
      file.name.toLowerCase().endsWith('.jpg') ||
      file.name.toLowerCase().endsWith('.jpeg')
    );

    if (droppedFiles.length > 0) {
      setFiles(droppedFiles);
      onFileDrop(droppedFiles);
    }
  }, [onFileDrop]);

  // Global drag event listeners
  useEffect(() => {
    const handleWindowDragEnter = (e: DragEvent) => {
      e.preventDefault();
      setIsDragOver(true);
    };

    const handleWindowDragLeave = (e: DragEvent) => {
      e.preventDefault();
      // Only hide if cursor leaves window completely
      if (e.clientX === 0 && e.clientY === 0) {
        setIsDragOver(false);
      }
    };

    const handleWindowDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleWindowDrop = (e: DragEvent) => {
      e.preventDefault();
    };

    window.addEventListener('dragenter', handleWindowDragEnter);
    window.addEventListener('dragleave', handleWindowDragLeave);
    window.addEventListener('dragover', handleWindowDragOver);
    window.addEventListener('drop', handleWindowDrop);

    return () => {
      window.removeEventListener('dragenter', handleWindowDragEnter);
      window.removeEventListener('dragleave', handleWindowDragLeave);
      window.removeEventListener('dragover', handleWindowDragOver);
      window.removeEventListener('drop', handleWindowDrop);
    };
  }, []);

  if (!isDragOver && !isProcessing) return null;

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 flex items-center justify-center",
        isProcessing ? "bg-white/30 backdrop-blur-md" : "bg-blue-500/20 backdrop-blur-sm"
      )}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {isProcessing ? (
        <ProcessingView 
          steps={processingSteps}
          currentFileIndex={0}
          totalFiles={files.length}
        />
      ) : (
        <DragDropView />
      )}
    </div>
  );
}

function DragDropView() {
  return (
    <div className="flex flex-col items-center justify-center space-y-6 p-8">
      <div className="relative">
        <div className="h-24 w-24 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
          <Upload className="h-12 w-12 text-blue-500" />
        </div>
        <div className="absolute -inset-2 rounded-full border-4 border-dashed border-white animate-pulse" />
      </div>
      
      <div className="text-center space-y-2">
        <h3 className="text-2xl font-bold text-white">
          Drop Your Invoices Here
        </h3>
        <p className="text-white/80 max-w-md">
          Support for PDF, PNG, JPG, and JPEG files. 
          Multiple files can be uploaded at once.
        </p>
      </div>
      
      <div className="flex items-center space-x-4 text-sm text-white/70">
        <div className="flex items-center space-x-1">
          <FileText className="h-4 w-4" />
          <span>PDF</span>
        </div>
        <div className="flex items-center space-x-1">
          <FileText className="h-4 w-4" />
          <span>PNG</span>
        </div>
        <div className="flex items-center space-x-1">
          <FileText className="h-4 w-4" />
          <span>JPG</span>
        </div>
      </div>
    </div>
  );
}

function ProcessingView({ 
  steps, 
  currentFileIndex, 
  totalFiles 
}: {
  steps: ProcessingStep[];
  currentFileIndex: number;
  totalFiles: number;
}) {
  // Calculate progress based on completed steps + partial progress for current step
  const completedSteps = steps.filter(step => step.status === 'completed').length;
  const processingSteps = steps.filter(step => step.status === 'processing').length;
  const totalSteps = steps.length;
  
  // Add 50% progress for currently processing step
  const progressValue = completedSteps + (processingSteps > 0 ? 0.5 : 0);
  const progress = totalSteps > 0 ? (progressValue / totalSteps) * 100 : 0;
  return (
    <div className="flex flex-col items-center justify-center space-y-8 p-8 max-w-md">
      {/* Lottie Animation */}
      <div className="w-32 h-32">
        <Lottie 
          animationData={animationData}
          loop={true}
          autoplay={true}
          className="w-full h-full"
        />
      </div>
      
      {/* Processing Title */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-gray-900">
          Processing Your Invoices
        </h2>
        <p className="text-gray-600">
          Please wait while we analyze your documents...
        </p>
      </div>
      
      {/* File Counter */}
      <div className="bg-blue-50 px-4 py-2 rounded-full">
        <span className="text-sm font-medium text-blue-700">
          Processing {totalFiles} file{totalFiles > 1 ? 's' : ''}
        </span>
      </div>
      
      {/* Processing Steps */}
      <div className="w-full space-y-3">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div
              key={step.id}
              className={cn(
                "flex items-center space-x-3 p-3 rounded-lg transition-colors",
                step.status === 'completed' && "bg-green-50",
                step.status === 'processing' && "bg-blue-50",
                step.status === 'pending' && "bg-gray-50"
              )}
            >
              <div className={cn(
                "flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center",
                step.status === 'completed' && "bg-green-500",
                step.status === 'processing' && "bg-blue-500",
                step.status === 'pending' && "bg-gray-300"
              )}>
                {step.status === 'completed' ? (
                  <Check className="h-3 w-3 text-white" />
                ) : step.status === 'processing' ? (
                  <Clock className="h-3 w-3 text-white animate-spin" />
                ) : (
                  <Icon className="h-3 w-3 text-white" />
                )}
              </div>
              
              <span className={cn(
                "text-sm font-medium",
                step.status === 'completed' && "text-green-700",
                step.status === 'processing' && "text-blue-700",
                step.status === 'pending' && "text-gray-500"
              )}>
                {step.label}
              </span>
              
              {step.status === 'processing' && (
                <div className="flex-1 ml-2">
                  <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full animate-pulse w-3/4" />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Progress Indicator */}
      <div className="w-full">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>Processing...</span>
          <span>{completedSteps} / {totalSteps} steps completed</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 rounded-full transition-all duration-500 ease-out"
            style={{ 
              width: `${progress}%` 
            }}
          />
        </div>
      </div>
    </div>
  );
}