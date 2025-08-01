# 🚀 InvoiceCopilot Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

### 3. Open Browser

Navigate to [http://localhost:3000](http://localhost:3000)

## ✅ What You'll See

- **Clean Interface**: Light background as requested
- **Simplified Layout**: Clean split-screen design
- **Two Main Sections**:
  - **Chat Area**: AI conversation interface (left side - 40% width)
  - **Workspace**: Generated visualizations (right side - 60% width)

## 🎯 Key Features Implemented

### ✅ Architecture
- **Next.js 14** with App Router
- **Server-Side Rendering** by default
- **TypeScript** for type safety
- **Tailwind CSS** for styling

### ✅ State Management
- **Context API + useReducer** (no Redux needed)
- **Clean separation** of concerns
- **Predictable state** updates

### ✅ Component Structure
- **Reusable UI components**
- **Server Components** where possible
- **Client Components** only for interactivity
- **Proper TypeScript** definitions

### ✅ Interface Features
- **Responsive design** (mobile, tablet, desktop)
- **Real-time chat** interface
- **Dynamic workspace** for visualizations
- **Loading states** and error handling
- **Clean split-screen** layout

## 🎨 Design System

### Colors & Theme
- **Light background** as requested
- **Professional blue** primary color
- **Consistent gray scale** for text
- **Status colors** (green, red, yellow)

### Components
- **Button**: Multiple variants and sizes
- **Card**: Clean container components
- **Input/Textarea**: Form elements with validation
- **Loading**: Spinners and progress indicators

## 🔌 Backend Integration Ready

The frontend is prepared to connect with your Python backend:

```typescript
// Example API integration points
const uploadInvoice = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/upload-invoice', {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
};

const generateChart = async (query: string) => {
  const response = await fetch('/api/generate-chart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  
  return response.json();
};
```

## 🛠️ Development Commands

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Check TypeScript
```

## 📁 Next Steps

1. **Connect Backend**: Update API calls in components
2. **Add Chart Library**: Integrate Plotly.js or Chart.js
3. **Implement WebSocket**: For real-time AI responses
4. **Add Authentication**: User login/session management
5. **Error Boundaries**: Better error handling
6. **Testing**: Add unit and integration tests

## 🔧 Configuration

### Environment Variables
Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Customization
- **Colors**: Edit `tailwind.config.ts`
- **Components**: Modify files in `src/components/`
- **Types**: Update `src/types/index.ts`
- **Utils**: Add helpers to `src/lib/utils.ts`

## 🎉 You're Ready!

The interface is ready to use with a clean, simplified design:

- ✅ **Light background** as requested
- ✅ **Next.js SSR** architecture
- ✅ **Clean split-screen** layout
- ✅ **TypeScript** throughout
- ✅ **Modern React patterns**
- ✅ **Responsive design**
- ✅ **Simplified interface** without sidebar/navigation

The next step is to implement the Python backend with PocketFlow and connect the two systems!