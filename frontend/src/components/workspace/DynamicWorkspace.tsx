import React from 'react';

export function DynamicWorkspace() {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center space-y-4">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
          <span className="text-2xl">🤖</span>
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-gray-900">
            Dynamic Content Area
          </h3>
          <p className="text-gray-500">
            This area will be dynamically updated by the AI agent based on your requests.
            Ask for UI components, layouts, or content to see them appear here!
          </p>
        </div>
        
        <div className="space-y-3 text-sm text-gray-500">
          <p className="font-medium">Try asking for:</p>
          <div className="grid grid-cols-1 gap-2 text-left max-w-sm mx-auto">
            {[
              '🎉 "Add Hello World text"',
              '🏠 "Create a landing page"',
              '📝 "Add a contact form"',
              '🎨 "Design a card component"'
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