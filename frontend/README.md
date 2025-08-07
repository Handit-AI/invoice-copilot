# Invoice Copilot Frontend

A modern React/Next.js frontend for the Invoice Copilot AI system that provides an intuitive interface for chatting with your invoices and generating interactive visualizations in real-time.

## 🚀 Features

- **Real-Time Chat Interface**: Conversational AI interface for invoice analysis
- **Dynamic Workspace**: Live generation of React components with charts and visualizations
- **Drag & Drop Upload**: Intuitive file upload with progress tracking
- **Interactive Visualizations**: Professional charts using Recharts library
- **Responsive Design**: Modern UI with Tailwind CSS and Framer Motion
- **TypeScript Support**: Full type safety and IntelliSense
- **Real-Time Updates**: Live workspace updates as AI generates content

## 🏗️ Architecture

```
User Interface → Chat Area → AI Backend → Dynamic Workspace
     ↓              ↓           ↓              ↓
  File Upload → Message Input → API Calls → React Components
```

### Core Components

- **MainLayout**: Main application layout with chat and workspace areas
- **ChatArea**: Conversational interface with message history
- **WorkspaceArea**: Dynamic content display with charts and visualizations
- **DragDropOverlay**: File upload interface with progress tracking
- **DynamicWorkspace**: Real-time React component generation

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend service running (Invoice Copilot Backend)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Handit-AI/invoice-copilot.git
cd invoice-copilot/frontend
```

### 2. Install Dependencies

```bash
# Using npm
npm install

# Using yarn
yarn install
```

### 3. Environment Configuration

```bash
# Copy environment example
cp .env.example .env.local

# Edit environment variables
nano .env.local
```

### 4. Configure Environment Variables

Edit the `.env.local` file:

```env
# Backend Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_TSX_AGENT_URL=http://localhost:8000

# Application Settings
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_APP_NAME=Invoice Copilot

# Feature Flags
NEXT_PUBLIC_ENABLE_DYNAMIC_CONTENT=true
NEXT_PUBLIC_ENABLE_REALTIME_UPDATES=true
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true
```

## 🚀 Running the Application

### Development Mode

```bash
# Start development server
npm run dev

# Or with yarn
yarn dev
```

The application will start on `http://localhost:3000`

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📚 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js app directory
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/             # React components
│   │   ├── chat/              # Chat interface
│   │   │   ├── ChatArea.tsx   # Main chat component
│   │   │   └── NextStepsAnimation.tsx
│   │   ├── workspace/         # Workspace area
│   │   │   ├── WorkspaceArea.tsx
│   │   │   └── DynamicWorkspace.tsx
│   │   ├── upload/            # File upload
│   │   │   └── DragDropOverlay.tsx
│   │   ├── layout/            # Layout components
│   │   │   └── MainLayout.tsx
│   │   └── ui/                # UI components
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Input.tsx
│   │       ├── Textarea.tsx
│   │       └── LoadingSpinner.tsx
│   ├── contexts/              # React contexts
│   │   └── AppContext.tsx     # Global app state
│   ├── lib/                   # Utility libraries
│   │   ├── chatApi.ts         # Chat API integration
│   │   ├── documentApi.ts     # Document processing API
│   │   ├── tsxAgent.ts        # TSX Agent integration
│   │   └── utils.ts           # Utility functions
│   ├── types/                 # TypeScript types
│   │   └── index.ts           # Type definitions
│   ├── hooks/                 # Custom React hooks
│   └── assets/                # Static assets
│       └── animations/        # Lottie animations
├── public/                    # Public assets
├── package.json               # Dependencies
├── next.config.js             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── env.example                # Environment variables template
```

## 💬 Usage Examples

### 1. Chat with Your Invoices

```typescript
// Send a message to the AI
const response = await sendChatMessage(
  "Create a bar chart of monthly expenses",
  "frontend/src/components/workspace"
);
```

### 2. Upload and Process Documents

```typescript
// Upload invoice files
const result = await uploadAndProcessDocuments(
  files,
  'processed',
  (progress) => {
    console.log('Progress:', progress);
  }
);
```

### 3. Generate Dynamic Content

```typescript
// Enable dynamic workspace
setWorkspaceContent('expenses-report');
```

## 🎨 UI Components

### Chat Interface

The chat area provides:
- **Real-time messaging** with the AI agent
- **Message history** with user and assistant messages
- **Quick actions** for common requests
- **Loading states** with animated indicators
- **Auto-scroll** to latest messages

### Workspace Area

The workspace displays:
- **Dynamic React components** generated by the AI
- **Interactive charts** using Recharts library
- **Real-time updates** as content is generated
- **Export options** for charts and reports
- **Invoice icons** showing uploaded files

### File Upload

The upload system includes:
- **Drag & drop** interface for files
- **Progress tracking** with visual indicators
- **Multiple file support** for batch processing
- **Error handling** with user feedback
- **Processing stages** (upload, OCR, vector storage)

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | Yes | Backend API URL |
| `NEXT_PUBLIC_TSX_AGENT_URL` | No | TSX Agent URL |
| `NEXT_PUBLIC_APP_ENV` | No | Environment (dev/prod) |
| `NEXT_PUBLIC_DEBUG` | No | Debug mode |

### Feature Flags

```env
# Enable/disable features
NEXT_PUBLIC_ENABLE_DYNAMIC_CONTENT=true
NEXT_PUBLIC_ENABLE_REALTIME_UPDATES=true
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true
```

## 🎯 Key Features

### 1. Real-Time Chat
- **Conversational AI**: Natural language interface
- **Message History**: Persistent chat sessions
- **Quick Actions**: Predefined common requests
- **Loading States**: Visual feedback during processing

### 2. Dynamic Workspace
- **Live Generation**: Real-time React component creation
- **Interactive Charts**: Professional data visualizations
- **Responsive Design**: Works on all screen sizes
- **Export Options**: Download charts and reports

### 3. File Processing
- **Drag & Drop**: Intuitive file upload
- **Progress Tracking**: Visual progress indicators
- **Batch Processing**: Handle multiple files
- **Error Handling**: Graceful error recovery

### 4. Modern UI/UX
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Smooth animations
- **Lucide Icons**: Beautiful iconography
- **Responsive Design**: Mobile-first approach

## 🧪 Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Development Workflow

1. **Start Backend**: Ensure the backend is running on port 8000
2. **Start Frontend**: Run `npm run dev`
3. **Open Browser**: Navigate to `http://localhost:3000`
4. **Upload Files**: Drag and drop invoice files
5. **Chat with AI**: Ask questions about your invoices
6. **View Results**: See real-time visualizations

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   ```

2. **Environment Variables**
   ```bash
   # Verify .env.local exists
   ls -la .env.local
   ```

3. **Port Already in Use**
   ```bash
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```

4. **Build Errors**
   ```bash
   # Clear Next.js cache
   rm -rf .next
   npm run build
   ```

### Debug Mode

```bash
# Enable debug logging
NEXT_PUBLIC_DEBUG=true npm run dev
```

## 📈 Performance

### Optimization Features

- **Next.js 14**: Latest framework with optimizations
- **Static Generation**: Pre-built pages where possible
- **Image Optimization**: Automatic image optimization
- **Code Splitting**: Automatic code splitting
- **Bundle Analysis**: Built-in bundle analyzer

### Monitoring

- **Console Logging**: Detailed development logs
- **Error Boundaries**: Graceful error handling
- **Performance Metrics**: Built-in performance monitoring
- **TypeScript**: Compile-time error checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Handit-AI/invoice-copilot/issues)
- **Documentation**: [Project Wiki](https://github.com/Handit-AI/invoice-copilot/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Handit-AI/invoice-copilot/discussions)

## 🙏 Acknowledgments

- **Next.js**: React framework
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Chart library
- **Framer Motion**: Animation library
- **Lucide**: Icon library

---

**Built with ❤️ by the Invoice Copilot Team** 