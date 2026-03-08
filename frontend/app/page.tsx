import EventForm from '../components/EventForm'

export default function Home() {
  return (
    <div className="h-full flex flex-col p-4 relative overflow-y-auto">
      <div className="scanline"></div>
      
      {/* VS Code Breadcrumbs */}
      <div className="text-xs text-gray-400 mb-4 flex items-center gap-2 border-b border-vscode-border pb-2 font-mono">
        <span>eventos-ai-swarm</span>
        <span>&gt;</span>
        <span>src</span>
        <span>&gt;</span>
        <span className="text-vscode-blue">setup.tsx</span>
      </div>

      <div className="mb-6 flex flex-col items-center justify-center mt-4">
        <h1 className="text-3xl font-bold text-vscode-blue tracking-widest font-sans">EventOS INIT</h1>
        <p className="text-gray-500 font-mono text-xs mt-2">Configure environment variables and data sources to boot the Swarm.</p>
      </div>
      
      <EventForm />
    </div>
  )
}