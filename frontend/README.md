# InvoiceCopilot Frontend

A modern Next.js application for AI-powered data visualization and chart generation.

## 🚀 Features

- **Real-time Chat Interface**: Interact with AI to generate charts and visualizations
- **Dynamic Visualizations**: AI-generated charts, tables, and reports
- **Server-Side Rendering**: Optimized performance with Next.js 14
- **Clean Split Layout**: Chat on left, generated visualizations on right
- **Responsive Design**: Works on desktop, tablet, and mobile
- **TypeScript**: Full type safety throughout the application

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React Context API + useReducer
- **UI Components**: Custom component library with class-variance-authority
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Type Safety**: TypeScript

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/             # React components
│   │   ├── ui/                 # Base UI components
│   │   ├── layout/             # Layout components
│   │   ├── chat/               # Chat interface
│   │   └── workspace/          # Visualization area
│   ├── contexts/               # React contexts
│   │   └── AppContext.tsx      # Main app state
│   ├── lib/                    # Utilities and helpers
│   │   └── utils.ts            # Common utilities
│   └── types/                  # TypeScript type definitions
│       └── index.ts            # Main types
├── public/                     # Static assets
├── package.json               # Dependencies
├── tailwind.config.ts         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── next.config.js             # Next.js configuration
```

## 🚦 Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm, yarn, or pnpm

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd invoice-copilot/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Architecture

### Component Architecture

- **Server Components**: Used by default for better performance
- **Client Components**: Only when interactivity is needed (marked with 'use client')
- **Separation of Concerns**: Clear separation between UI, business logic, and state

### State Management

- **Global State**: React Context API with useReducer for complex state
- **Local State**: useState for component-specific state
- **No Redux**: Context API is sufficient for this application size

### Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Custom Design System**: Consistent colors, spacing, and typography
- **Component Variants**: Using class-variance-authority for component variations
- **Responsive Design**: Mobile-first approach

## 🎨 Design System

### Colors
- **Primary**: Blue-based theme
- **Background**: Light/white theme as requested
- **Text**: Gray scale for proper contrast
- **Status**: Green (success), Red (error), Yellow (warning)

### Components
- **Button**: Multiple variants (default, outline, ghost, etc.)
- **Card**: Container component with variants
- **Input/Textarea**: Form components with validation
- **Loading**: Spinners and skeleton loaders

## 🔄 Development Workflow

### Code Organization

1. **Components**: Small, focused, reusable
2. **Hooks**: Custom hooks for reusable logic
3. **Utils**: Pure utility functions
4. **Types**: Comprehensive TypeScript definitions

### Best Practices

- Use Server Components when possible
- Client Components only for interactivity
- Proper error boundaries
- Accessibility considerations
- Performance optimization

## 🔌 Backend Integration

The frontend is designed to integrate with a Python FastAPI backend:

- **REST API**: Standard HTTP requests for data operations
- **WebSocket**: Real-time updates for chart generation
- **File Upload**: Multipart form data for invoice uploads
- **Streaming**: Server-sent events for real-time AI responses

## 🎯 Key Features Implementation

### Chat Interface
- Real-time messaging with AI
- Typing indicators and loading states
- Message history and session management
- Quick action buttons for common chart types

### Dynamic Visualizations
- Chart generation from natural language
- Real-time updates during generation
- Export capabilities
- Interactive chart preview

## 🚀 Deployment

### Build for Production

```bash
npm run build
npm run start
```

### Deployment Options

- **Vercel**: Recommended for Next.js applications
- **Netlify**: Alternative static hosting
- **Docker**: Containerized deployment
- **Traditional Hosting**: Any Node.js hosting provider

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Tailwind Configuration

The design system can be customized in `tailwind.config.ts`:

- Colors
- Typography
- Spacing
- Breakpoints
- Custom components

## 📝 Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint
- `npm run type-check`: Run TypeScript compiler

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for all new code
3. Add proper error handling
4. Test components thoroughly
5. Update documentation as needed

## 📄 License

This project is part of the InvoiceCopilot application.