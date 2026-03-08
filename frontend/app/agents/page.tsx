import AgentGraph from "../../components/AgentGraph";

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

      <div className="flex-1 flex flex-col">
        {/* We actually render the AgentGraph component here now! */}
        <AgentGraph />
      </div>
    </div>
  )
}