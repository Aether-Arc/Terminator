import AgentMonitor from "../../components/AgentMonitor";
import SimulationPanel from "../../components/SimulationPanel";

export default function Dashboard() {
  return (
    <div className="h-full flex flex-col p-4 relative">
      <div className="scanline"></div>
      
      {/* VS Code Breadcrumbs */}
      <div className="text-xs text-gray-400 mb-4 flex items-center gap-2 border-b border-vscode-border pb-2 font-mono">
        <span>eventos-ai- Skynet</span>
        <span>&gt;</span>
        <span>src</span>
        <span>&gt;</span>
        <span className="text-vscode-blue">dashboard.tsx</span>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        {/* Editor Area */}
        <div className="bg-vscode-sidebar rounded border border-vscode-border p-6 terminal-glow flex flex-col font-mono text-sm shadow-xl">
          <div className="flex gap-2 mb-4 border-b border-vscode-border pb-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          
          <h2 className="mb-4">
            <span className="text-vscode-purple">export const</span> <span className="text-vscode-blue">initEvent Skynet</span> = <span className="text-vscode-purple">async</span> () =&gt; {'{'}
          </h2>
          
          <div className="pl-6 text-vscode-text space-y-2">
            <p><span className="text-vscode-purple">await</span> <span className="text-vscode-blue">Orchestrator</span>.wake();</p>
            <p><span className="text-vscode-purple">const</span> target = <span className="text-vscode-orange">'Neurathon_2026'</span>;</p>
            <p><span className="text-vscode-purple">await</span> <span className="text-vscode-blue">Memory</span>.connect(target);</p>
            <p className="mt-4 text-vscode-green italic">// Awaiting execution command...</p>
          </div>
          
          <div className="mt-auto pt-8">
            <button className="bg-vscode-blue/10 border border-vscode-blue text-vscode-blue hover:bg-vscode-blue hover:text-white px-4 py-3 rounded transition-all uppercase tracking-widest text-xs font-bold w-full shadow-[0_0_15px_rgba(86,156,214,0.3)]">
              &gt; Execute  Skynet.sh
            </button>
          </div>
          <h2 className="mt-4">{'}'}</h2>
        </div>

        {/* Terminals & Output */}
        <div className="flex flex-col gap-6">
          <AgentMonitor />
          <SimulationPanel />
        </div>
      </div>
    </div>
  )
}