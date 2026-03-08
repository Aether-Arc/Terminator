"use client"
import { useState } from "react"

export default function SimulationPanel() {
  const [log, setLog] = useState<string[]>([])

  const triggerEvent = (type: string) => {
    setLog(prev => [...prev, `<span class="text-vscode-blue">admin@eventos</span>:~$ inject_anomaly --type <span class="text-vscode-orange">'${type}'</span>`])
    setTimeout(() => {
      setLog(prev => [...prev, `<span class="text-red-500 font-bold">[CRITICAL]</span> Anomaly injected. Triggering Orchestrator...`])
    }, 600)
  }

  return (
    <div className="bg-[#1e1e1e] border border-red-900/40 rounded flex-1 flex flex-col shadow-lg relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-red-600 via-orange-500 to-red-600"></div>
      
      <div className="p-3 border-b border-vscode-border bg-[#252526] flex justify-between items-center">
        <h2 className="text-vscode-text font-mono text-[11px] uppercase tracking-widest flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
          Chaos Injector
        </h2>
      </div>
      
      <div className="p-4 flex flex-col flex-1 gap-4">
        <div className="grid grid-cols-2 gap-3">
          <button onClick={() => triggerEvent("speaker_cancel")} className="border border-vscode-border bg-[#2d2d2d] hover:bg-red-900/40 text-vscode-text text-xs p-2 rounded transition-all text-left font-mono shadow-sm">
            <span className="text-vscode-purple">exec</span> kill_keynote()
          </button>
          <button onClick={() => triggerEvent("room_overflow")} className="border border-vscode-border bg-[#2d2d2d] hover:bg-orange-900/40 text-vscode-text text-xs p-2 rounded transition-all text-left font-mono shadow-sm">
            <span className="text-vscode-purple">exec</span> over_capacity()
          </button>
        </div>
        
        <div className="bg-black/60 p-3 rounded flex-1 overflow-y-auto font-mono text-xs border border-vscode-border/50 text-gray-300">
          {log.map((l, i) => <div key={i} dangerouslySetInnerHTML={{ __html: l }} className="mb-1"></div>)}
          {log.length === 0 && <span className="text-vscode-green opacity-50 italic">// Chaos engine idle. Awaiting command...</span>}
        </div>
      </div>
    </div>
  )
}