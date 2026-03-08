import SimulationPanel from "../../components/SimulationPanel";

export default function SimulationPage() {
  return (
    <div className="h-full flex flex-col p-4 relative">
      <div className="scanline"></div>
      
      <div className="text-xs text-gray-400 mb-4 flex items-center gap-2 border-b border-vscode-border pb-2 font-mono">
        <span>eventos-ai-swarm</span>
        <span>&gt;</span>
        <span>src</span>
        <span>&gt;</span>
        <span className="text-vscode-blue">simulation_engine.tsx</span>
      </div>

      <div className="flex-1 flex flex-col">
        <h2 className="text-xl text-vscode-text font-sans mb-4">Full Screen Chaos Engine</h2>
        <SimulationPanel />
      </div>
    </div>
  )
}