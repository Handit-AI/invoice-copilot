'use client';

import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, ArrowRight, Brain } from 'lucide-react';

interface ReasoningStep {
  id: string;
  text: string;
  status: 'pending' | 'processing' | 'completed';
  delay: number;
}

const reasoningSteps: ReasoningStep[] = [
  {
    id: 'analyze-request',
    text: 'First, I will analyze the uploaded invoice data from Q1 2025...',
    status: 'pending',
    delay: 0
  },
  {
    id: 'data-processing',
    text: 'Then, I need to categorize each expense by department and type...',
    status: 'pending',
    delay: 800
  },
  {
    id: 'calculations',
    text: 'Next, I must calculate totals and performance metrics for comparison...',
    status: 'pending',
    delay: 1600
  },
  {
    id: 'visualization',
    text: 'After that, I will generate the visual report with charts and tables...',
    status: 'pending',
    delay: 2400
  },
  {
    id: 'insights',
    text: 'Finally, I should compile actionable insights from the data patterns...',
    status: 'pending',
    delay: 3200
  }
];

export function NextStepsAnimation() {
  const [steps, setSteps] = useState<ReasoningStep[]>(reasoningSteps);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);

  useEffect(() => {
    let timeouts: NodeJS.Timeout[] = [];

    steps.forEach((step, index) => {
      // Start processing step
      const startTimeout = setTimeout(() => {
        setCurrentStepIndex(index);
        setSteps(prevSteps => 
          prevSteps.map((s, i) => 
            i === index ? { ...s, status: 'processing' } : s
          )
        );
      }, step.delay);

      // Complete step
      const completeTimeout = setTimeout(() => {
        setSteps(prevSteps => 
          prevSteps.map((s, i) => 
            i === index ? { ...s, status: 'completed' } : s
          )
        );
      }, step.delay + 600); // Complete 600ms after starting

      timeouts.push(startTimeout, completeTimeout);
    });

    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
  }, [steps.length]);

    return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
      <div className="space-y-2">
        {/* Header */}
        <div className="flex items-center space-x-2 pb-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-gray-700">Thinking...</span>
        </div>

        {/* Reasoning Steps */}
        <div className="space-y-1">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-start space-x-2 transition-all duration-200 ${
                step.status === 'pending' 
                  ? 'opacity-30' 
                  : step.status === 'processing'
                  ? 'opacity-100'
                  : 'opacity-60'
              }`}
            >
              <div className="flex-shrink-0 mt-1">
                {step.status === 'completed' ? (
                  <div className="w-1.5 h-1.5 bg-gray-600 rounded-full"></div>
                ) : step.status === 'processing' ? (
                  <div className="w-1.5 h-1.5 bg-gray-800 rounded-full animate-pulse"></div>
                ) : (
                  <div className="w-1.5 h-1.5 border border-gray-300 rounded-full"></div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className={`text-sm ${
                  step.status === 'processing' 
                    ? 'text-gray-900' 
                    : step.status === 'completed'
                    ? 'text-gray-700'
                    : 'text-gray-500'
                }`}>
                  {step.text}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Simple Progress */}
        <div className="pt-1">
          <div className="w-full bg-gray-200 rounded-full h-1">
            <div 
              className="bg-gray-600 h-1 rounded-full transition-all duration-300 ease-out"
              style={{ 
                width: `${(steps.filter(s => s.status === 'completed').length / steps.length) * 100}%` 
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}