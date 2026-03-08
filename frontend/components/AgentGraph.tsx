"use client"
import { useEffect, useState } from 'react'

interface SwarmMessage {
  agent: string;
  action: string;
  status: 'thinking' | 'simulating' | 'success' | 'idle';
}

export default function AgentGraph() {
  const [activeNode, setActiveNode] = useState<string | null>(null)
  const [logs, setLogs] = useState<SwarmMessage[]>([])

  useEffect(() => {
    // Connect to FastAPI WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/swarm')

    ws.onmessage = (event) => {
      const data: SwarmMessage = JSON.parse(event.data)
      setActiveNode(data.agent)
      setLogs((prev) => [...prev, data].slice(-6)) // Keep last 6 logs
      
      if (data.status === 'success') {
        setTimeout(() => setActiveNode(null), 2000)
      }
    }

    return () => ws.close()
  }, [])

  // Helper function to dynamically glow the active node
  const getNodeClass = (nodeName: string) => {
    const base = "p-4 rounded border font-mono text-center transition-all duration-300 relative overflow-hidden "
    if (activeNode === nodeName) {
      return base + "bg-cyber-cyan/20 border-cyber-cyan shadow-[0_0_30px_rgba(0,240,255,0.6)] text-white scale-105 z-10"
    }
    return base + "bg-[#0a0a0f] border-cyber-border text-gray-500"
  }

  return (
    <div className="hud-panel p-6 flex flex-col h-full relative">
      <h2 className="text-cyber-cyan uppercase tracking-widest text-xs font-bold mb-8 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-cyber-cyan animate-pulse"></div>
        Live Cognitive Network
      </h2>

      {/* Visual Agent Graph */}
      <div className="flex-1 flex items-center justify-center">
        <div className="grid grid-cols-3 gap-12 relative w-full max-w-2xl">
          
          {/* Top Level: Orchestrator */}
          <div className="col-span-3 flex justify-center mb-8">
            <div className={getNodeClass("Orchestrator")}>
              <div className="font-bold tracking-widest text-sm">Orchestrator</div>
              <div className="text-[10px] mt-1 opacity-70">Master Node</div>
            </div>
          </div>

          {/* Reasoning Level */}
          <div className={getNodeClass("PlannerAgent")}>
            <div className="font-bold text-sm">Planner</div>
            <div className="text-[10px] opacity-70">Strategy Gen</div>
          </div>
          
          <div className={getNodeClass("WorldModelAgent")}>
            <div className="font-bold text-sm">World Model</div>
            <div className="text-[10px] opacity-70">Environment Sim</div>
          </div>

          <div className={getNodeClass("CriticAgent")}>
            <div className="font-bold text-sm">Critic</div>
            <div className="text-[10px] opacity-70">Reward Eval</div>
          </div>

          {/* Execution Level */}
          <div className={getNodeClass("SchedulerAgent") + " mt-8"}>
            <div className="font-bold text-sm">Scheduler</div>
          </div>
          
          <div className={getNodeClass("MarketingAgent") + " mt-8"}>
            <div className="font-bold text-sm">Marketing</div>
          </div>

          <div className={getNodeClass("EmailAgent") + " mt-8"}>
            <div className="font-bold text-sm">Outreach</div>
          </div>

        </div>
      </div>

      {/* Live Action Stream Terminal */}
      <div className="mt-8 bg-black/80 border border-cyber-border rounded p-4 h-32 overflow-hidden flex flex-col justify-end">
        {logs.map((log, i) => (
          <div key={i} className="font-mono text-[11px] mb-1 animate-fade-in-up flex items-center gap-2">
            <span className={log.status === 'success' ? 'text-cyber-green' : 'text-cyber-cyan'}>
              [{new Date().toLocaleTimeString()}]
            </span>
            <span className="text-cyber-purple font-bold">@{log.agent}:</span>
            <span className="text-gray-300">{log.action}</span>
          </div>
        ))}
        {logs.length === 0 && <div className="text-gray-600 font-mono text-xs italic">// Network idle. Awaiting stimulus.</div>}
      </div>
    </div>
  )
}