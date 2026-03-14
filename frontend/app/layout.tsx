import type { Metadata } from 'next'
import { Orbitron, Fira_Code } from 'next/font/google'
import './globals.css'
import Navbar from '../components/Navbar'

const orbitron = Orbitron({ subsets: ['latin'], variable: '--font-orbitron' })
const firaCode = Fira_Code({ subsets: ['latin'], variable: '--font-fira-code' })

export const metadata: Metadata = {
  title: 'EventOS |  Skynet Control',
  description: 'Autonomous Event Logistics  Skynet',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${orbitron.variable} ${firaCode.variable} font-sans bg-vscode-bg text-vscode-text flex h-screen overflow-hidden`}suppressHydrationWarning>
        {/* VS Code style Activity Bar on the left */}
        <Navbar />
        {/* Main Editor Area */}
        <main className="flex-1 overflow-y-auto bg-vscode-bg relative">
          {children}
        </main>
      </body>
    </html>
  )
}