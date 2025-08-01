import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AppProvider } from '@/contexts/AppContext';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'InvoiceCopilot - AI-Powered Invoice Analysis',
  description: 'Generate charts, tables, and analysis from your invoices in real-time with AI assistance.',
  keywords: ['invoice', 'AI', 'analysis', 'charts', 'automation', 'finance'],
  authors: [{ name: 'InvoiceCopilot Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'InvoiceCopilot - AI Invoice Analysis',
    description: 'Transform your invoices into insights with AI-powered analysis and visualization.',
    type: 'website',
    locale: 'en_US',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>
        <AppProvider>
          {children}
        </AppProvider>
      </body>
    </html>
  );
}