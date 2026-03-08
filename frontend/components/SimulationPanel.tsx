"use client"
import { useState } from "react"
import { simulateCrisis } from "../lib/api"

export default function SimulationPanel() {
  const [log, setLog] = useState<string[]>([])

  const triggerEvent = async (type: string) => {
    setLog(prev => [...prev, `Triggering: ${type}...`])
    const res = await simulateCrisis({ type })
    setLog(prev => [...prev, `Swarm Response: ${JSON.stringify(res.crisis)}`])
  }

  return (
    <div className="bg-gray-800 p-4 rounded mt-4 border border-red-500">
      <h2 className="text-xl text-red-400 mb-4 font-bold">Chaos Engine (Demo Mode)</h2>
      <div className="flex gap-4 mb-4">
        <button onClick={() => triggerEvent("speaker_cancelled")} className="bg-red-600 px-4 py-2 rounded hover:bg-red-700">
          Cancel Keynote Speaker
        </button>
        <button onClick={() => triggerEvent("room_overflow")} className="bg-orange-600 px-4 py-2 rounded hover:bg-orange-700">
          Overcrowd Main Hall
        </button>
        <button onClick={() => triggerEvent("budget_cut")} className="bg-yellow-600 px-4 py-2 rounded hover:bg-yellow-700 text-black">
          Slash Budget 20%
        </button>
      </div>
      
      <div className="bg-black p-3 rounded h-32 overflow-y-auto font-mono text-sm text-green-400">
        {log.map((l, i) => <div key={i}>{l}</div>)}
        {log.length === 0 && <span className="text-gray-600">Waiting for crisis injection...</span>}
      </div>
    </div>
  )
}