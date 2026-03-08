"use client"
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    const saved = localStorage.getItem("swarmResult");
    if (saved) {
      setResults(JSON.parse(saved));
    }
  }, []);

  if (!results) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500 font-mono">
        <p>No active event data. Initialize a swarm first.</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col p-4 relative overflow-y-auto">
      <div className="text-xs text-gray-400 mb-4 flex items-center gap-2 border-b border-vscode-border pb-2 font-mono">
        <span>eventos-ai-swarm</span>
        <span>&gt;</span>
        <span>src</span>
        <span>&gt;</span>
        <span className="text-vscode-blue">output.json</span>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
        
        {/* Left Column: Stats & Schedule */}
        <div className="flex flex-col gap-6">
          <div className="bg-vscode-sidebar border border-vscode-border rounded p-4 shadow-lg">
            <h2 className="text-vscode-purple font-mono text-xs uppercase mb-4 border-b border-vscode-border pb-2">Swarm Diagnostics</h2>
            <div className="flex justify-between items-center bg-[#1e1e1e] p-3 rounded border border-vscode-border">
              <span className="text-gray-400 text-sm">Calculated Stability Score:</span>
              <span className="text-vscode-green font-bold text-xl">{results.stability_score} / 100</span>
            </div>
          </div>

          <div className="bg-vscode-sidebar border border-vscode-border rounded p-4 shadow-lg flex-1">
            <h2 className="text-vscode-blue font-mono text-xs uppercase mb-4 border-b border-vscode-border pb-2">Generated Schedule (OR-Tools)</h2>
            <div className="space-y-2">
              {results.schedule && results.schedule.map((item: any, i: number) => (
                <div key={i} className="flex items-center gap-4 bg-[#1e1e1e] p-3 rounded border border-vscode-border text-sm">
                  <span className="text-vscode-orange w-24 shrink-0 font-mono">{item.start}</span>
                  <span className="text-vscode-text flex-1">{item.session}</span>
                  <span className="text-gray-500 text-xs px-2 py-1 bg-[#2d2d2d] rounded border border-[#3c3c3c]">{item.track}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: AI Output */}
        <div className="flex flex-col gap-6">
          <div className="bg-vscode-sidebar border border-vscode-border rounded p-4 shadow-lg flex-1 flex flex-col">
            <h2 className="text-vscode-blue font-mono text-xs uppercase mb-4 border-b border-vscode-border pb-2">Marketing Assets (Gemini)</h2>
            <div className="bg-[#1e1e1e] p-4 rounded border border-vscode-border flex-1 overflow-y-auto font-sans text-sm text-gray-300 whitespace-pre-wrap">
              {results.marketing}
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}