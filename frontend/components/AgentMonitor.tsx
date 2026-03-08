export default function AgentMonitor() {
  return (
    <div className="bg-[#1e1e1e] border border-vscode-border rounded flex flex-col h-72 shadow-lg">
      <div className="flex bg-[#252526] text-[11px] uppercase tracking-wider font-mono">
        <div className="px-4 py-2 border-b-[1px] border-vscode-blue text-vscode-text bg-[#1e1e1e]">Terminal</div>
        <div className="px-4 py-2 text-gray-500 hover:text-gray-300 cursor-pointer">Debug Console</div>
        <div className="px-4 py-2 text-gray-500 hover:text-gray-300 cursor-pointer">Output</div>
      </div>
      <div className="p-4 font-mono text-xs overflow-y-auto flex-1 space-y-2 leading-relaxed">
        <div className="text-vscode-green">[10:04:21] INFO: Swarm network connected on port 8000.</div>
        <div className="text-vscode-text"><span className="text-vscode-blue">PlannerAgent</span>: Compiled base abstract syntax tree for event.</div>
        <div className="text-vscode-text"><span className="text-vscode-blue">SchedulerAgent</span>: Generating constraint logic...</div>
        <div className="text-vscode-yellow">[10:04:25] WARN: Memory bottleneck detected in VectorDB allocation.</div>
        <div className="text-vscode-text"><span className="text-vscode-blue">ResourceAgent</span>: Re-routing parameters to secondary nodes.</div>
        <div className="flex items-center gap-2 mt-4">
          <span className="text-vscode-green">admin@eventos ~/swarm $</span>
          <span className="w-2 h-4 bg-gray-400 animate-pulse"></span>
        </div>
      </div>
    </div>
  )
}