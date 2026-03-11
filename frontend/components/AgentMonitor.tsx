import { useEffect, useRef } from 'react'

export default function AgentMonitor({ logs }: { logs: any[] }) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // Map backend status to VS Code theme colors
  const getColor = (status: string) => {
    switch (status) {
      case 'thinking': return 'text-vscode-yellow'
      case 'simulating': return 'text-vscode-purple'
      case 'success': return 'text-vscode-green'
      case 'error': return 'text-red-400'
      default: return 'text-vscode-text'
    }
  }

  return (
    <div className="flex-1 p-4 font-mono text-[11px] overflow-y-auto space-y-2 leading-relaxed bg-[#1e1e1e]">
      <div className="text-vscode-green mb-4">
        [SYSTEM] Swarm Network Initialized. Listening on port 8000...
      </div>
      
      {logs.map((log, i) => (
        <div key={i} className="flex flex-col mb-1">
          <div>
            <span className="text-gray-500">[{new Date().toLocaleTimeString()}] </span>
            <span className="text-vscode-blue font-bold">{log.agent}</span>: 
          </div>
          <div className={`ml-4 ${getColor(log.status)}`}>
             {log.message}
          </div>
        </div>
      ))}
      
      <div className="flex items-center gap-2 mt-4 text-vscode-green">
        <span>admin@eventos ~/swarm $</span>
        <span className="w-2 h-3 bg-gray-400 animate-pulse"></span>
      </div>
      <div ref={bottomRef} />
    </div>
  )
}