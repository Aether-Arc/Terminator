"use client"
import { useState } from "react"
import { manualOverride } from "../../lib/api"
import { useRouter } from "next/navigation"

export default function SimulationPanel() {
  const [log, setLog] = useState<string[]>([])
  const [customCrisis, setCustomCrisis] = useState("")
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const fireCrisis = async (description: string) => {
    setLoading(true)
    setLog(prev => [...prev, `<span class="text-vscode-blue">admin@eventos</span>:~$ inject_crisis --desc <span class="text-vscode-orange">'${description}'</span>`])
    
    // Allow UI to update terminal text
    setTimeout(async () => {
      setLog(prev => [...prev, `<span class="text-red-500 font-bold">[CRITICAL]</span> Anomaly detected. Waking MCTS Planner...`])
      
      try {
        const payloadString = localStorage.getItem("eventPayload");
        const eventData = JSON.parse(payloadString || "{}");

        const result = await manualOverride({
            override_type: "custom_crisis",
            description: description,
            event_name: eventData.name,
            expected_crowd: eventData.expected_crowd,
            csv_content: eventData.csv_content
        });

        setLog(prev => [...prev, `<span class="text-vscode-green font-bold">[RESOLVED]</span> Schedule re-calculated. Mitigation: ${result.applied_solution?.mitigation_strategy}`])
        
        // Update the dashboard with the new resolved schedule
        localStorage.setItem("swarmResult", JSON.stringify(result));
        setTimeout(() => router.push("/dashboard"), 1500);

      } catch(e) {
        setLog(prev => [...prev, `<span class="text-red-500">[ERROR]</span> Swarm failed to resolve crisis.`])
      }
      setLoading(false);
    }, 500);
  }

  return (
    <div className="bg-[#1e1e1e] border border-red-900/40 rounded flex-1 flex flex-col shadow-lg relative overflow-hidden h-full">
      <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-red-600 via-orange-500 to-red-600"></div>
      
      <div className="p-3 border-b border-vscode-border bg-[#252526] flex justify-between items-center">
        <h2 className="text-vscode-text font-mono text-[11px] uppercase tracking-widest flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
          Monte Carlo Crisis Injector
        </h2>
      </div>
      
      <div className="p-4 flex flex-col flex-1 gap-4">
        
        <div className="flex gap-2">
            <input 
                type="text" 
                disabled={loading}
                value={customCrisis} 
                onChange={(e) => setCustomCrisis(e.target.value)} 
                placeholder="Describe a random emergency..." 
                className="flex-1 bg-[#2d2d2d] border border-vscode-border rounded text-xs px-3 text-vscode-text outline-none focus:border-red-500"
            />
            <button 
                onClick={() => fireCrisis(customCrisis)}
                disabled={loading || customCrisis.length === 0}
                className="bg-red-900/40 border border-red-500 text-red-400 px-4 py-2 rounded text-xs hover:bg-red-500 hover:text-white transition-colors"
            >
                INJECT
            </button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button disabled={loading} onClick={() => fireCrisis("The main keynote speaker just cancelled their flight.")} className="border border-vscode-border bg-[#2d2d2d] hover:bg-red-900/40 text-vscode-text text-xs p-2 rounded transition-all text-left font-mono">
            <span className="text-vscode-purple">exec</span> kill_keynote()
          </button>
          <button disabled={loading} onClick={() => fireCrisis("The main hall air conditioning broke and it is too hot.")} className="border border-vscode-border bg-[#2d2d2d] hover:bg-orange-900/40 text-vscode-text text-xs p-2 rounded transition-all text-left font-mono">
            <span className="text-vscode-purple">exec</span> ac_failure()
          </button>
        </div>
        
        <div className="bg-black/60 p-3 rounded flex-1 overflow-y-auto font-mono text-xs border border-vscode-border/50 text-gray-300">
          {log.map((l, i) => <div key={i} dangerouslySetInnerHTML={{ __html: l }} className="mb-2"></div>)}
          {log.length === 0 && <span className="text-vscode-green opacity-50 italic">// Physics engine idle. Awaiting crisis parameters...</span>}
        </div>
      </div>
    </div>
  )
}