export default function AgentsPage() {
  return (
    <div className="h-full flex flex-col p-4 relative">
      <div className="scanline"></div>
      
      <div className="text-xs text-gray-400 mb-4 flex items-center gap-2 border-b border-vscode-border pb-2 font-mono">
        <span>eventos-ai-swarm</span>
        <span>&gt;</span>
        <span>src</span>
        <span>&gt;</span>
        <span className="text-vscode-blue">agents_network.tsx</span>
      </div>

      <div className="flex-1 flex items-center justify-center border border-vscode-border bg-vscode-sidebar rounded terminal-glow">
        <div className="text-center font-mono">
          <svg className="w-16 h-16 text-vscode-purple mx-auto mb-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
          <h2 className="text-vscode-text text-xl mb-2">Agent Network Visualizer</h2>
          <p className="text-vscode-green text-xs">// Connect the LangGraph backend to view live task handoffs.</p>
        </div>
      </div>
    </div>
  )
}