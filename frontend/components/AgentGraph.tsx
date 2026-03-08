"use client"
import { useEffect, useState, useRef } from 'react'

interface SwarmMessage {
  agent: string;
  action: string;
  status: 'thinking' | 'simulating' | 'success' | 'idle' | 'error';
}

export default function AgentGraph() {
  const [activeNode, setActiveNode] = useState<string | null>(null)
  const [logs, setLogs] = useState<SwarmMessage[]>([])
  const [swarmStarted, setSwarmStarted] = useState(false)
  const terminalEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [logs])

  useEffect(() => {
    // 1. Clean WebSocket connection without aggressive reconnect loops
    const ws = new WebSocket('ws://localhost:8000/ws/swarm')
    let isMounted = true

    ws.onmessage = (event) => {
      if (!isMounted) return
      const data: SwarmMessage = JSON.parse(event.data)
      setActiveNode(data.agent)
      setLogs((prev) => [...prev, data])
      
      if (data.status === 'success' || data.status === 'idle') {
        setTimeout(() => { if (isMounted) setActiveNode(null) }, 1500)
      }
    }

    // 2. Auto-trigger the API Call exactly once
    const savedPayload = localStorage.getItem("eventPayload")
    if (savedPayload && !swarmStarted) {
      setSwarmStarted(true)
      fetch('http://localhost:8000/plan_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: savedPayload
      }).then(() => {
        localStorage.removeItem("eventPayload")
      }).catch(err => {
        setLogs(prev => [...prev, { agent: 'SYSTEM', action: `ERROR: ${err.message}`, status: 'error' }])
      })
    }

    // 3. Graceful cleanup for React StrictMode
    return () => {
      isMounted = false
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    }
  }, [swarmStarted])

  const getNodeClass = (nodeName: string) => {
    const base = "p-4 rounded border font-mono text-center transition-all duration-300 relative overflow-hidden min-h-[80px] flex flex-col items-center justify-center "
    if (activeNode === nodeName) {
      return base + "bg-vscode-blue/20 border-vscode-blue shadow-[0_0_15px_rgba(86,156,214,0.4)] text-white scale-105 z-10"
    }
    return base + "bg-[#252526] border-vscode-border text-gray-400"
  }

  const getStatusColor = (status: string) => {
    if (status === 'success') return 'text-vscode-green'
    if (status === 'error') return 'text-red-500'
    if (status === 'simulating') return 'text-vscode-purple'
    return 'text-vscode-blue'
  }

  return (
    <div className="bg-[#1e1e1e] rounded border border-vscode-border p-6 flex flex-col h-full relative terminal-glow shadow-xl">
      <h2 className="text-vscode-text font-mono text-sm mb-8 flex items-center gap-2 border-b border-vscode-border pb-2">
        <div className="w-2 h-2 rounded-full bg-vscode-blue animate-pulse"></div>
        Live Cognitive Network
      </h2>

      <div className="flex-1 flex items-center justify-center">
        <div className="grid grid-cols-3 gap-8 relative w-full max-w-3xl">
          
          <div className="col-span-3 flex justify-center mb-4">
            <div className={getNodeClass("Orchestrator") + " w-64"}>
              <div className="font-bold text-sm">Orchestrator</div>
              <div className="text-[10px] mt-1 text-gray-500">Master Node</div>
            </div>
          </div>

          <div className={getNodeClass("PlannerAgent")}>
            <div className="font-bold text-sm">Planner</div>
            <div className="text-[10px] text-gray-500">Strategy Gen</div>
          </div>
          
          <div className={getNodeClass("WorldModelAgent")}>
            <div className="font-bold text-sm">World Model</div>
            <div className="text-[10px] text-gray-500">CNN/RNN Sim</div>
          </div>

          <div className={getNodeClass("CriticAgent")}>
            <div className="font-bold text-sm">Critic</div>
            <div className="text-[10px] text-gray-500">RL Eval</div>
          </div>

          <div className={getNodeClass("SchedulerAgent") + " mt-4"}>
            <div className="font-bold text-sm">Scheduler</div>
          </div>
          
          <div className={getNodeClass("MarketingAgent") + " mt-4"}>
            <div className="font-bold text-sm">Marketing</div>
          </div>

          <div className={getNodeClass("EmailAgent") + " mt-4"}>
            <div className="font-bold text-sm">Outreach</div>
          </div>

        </div>
      </div>

      <div className="mt-8 bg-[#0d0d0d] border border-vscode-border rounded h-40 overflow-y-auto p-4 font-mono text-[11px] shadow-inner relative">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3 mb-1">
            <span className="text-gray-600 shrink-0">[{new Date().toLocaleTimeString()}]</span>
            <span className="text-vscode-blue font-bold w-32 shrink-0 text-right">@{log.agent}:</span>
            <span className={`${getStatusColor(log.status)} flex-1`}>{log.action}</span>
          </div>
        ))}
        {logs.length === 0 && <div className="text-gray-600 italic">// Awaiting uplink...</div>}
        <div ref={terminalEndRef} />
      </div>
    </div>
  )
}