"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function EventForm() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>(["marketing", "email"]) // Baseline agents

  const toggleAgent = (agent: string) => {
    setSelectedAgents(prev => 
      prev.includes(agent) ? prev.filter(a => a !== agent) : [...prev, agent]
    )
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    
    const formData = new FormData(e.currentTarget)
    const file = formData.get("participants_csv") as File
    
    let csvContent = ""
    if (file && file.size > 0) {
      csvContent = await file.text()
    }

    const payload = {
      name: formData.get("event_name"),
      expected_crowd: parseInt(formData.get("expected_crowd") as string),
      marketing_prompt: formData.get("marketing_prompt"),
      csv_content: csvContent, 
      requested_agents: selectedAgents // Pass the dynamic agents to the backend!
    }

    localStorage.setItem("eventPayload", JSON.stringify(payload))
    router.push('/agents')
  }

  const optionalAgents = [
    { id: "sponsor", name: "Sponsor Pitch Agent", desc: "Browses live web for corporate sponsors" },
    { id: "budget", name: "Financial CFO Agent", desc: "Calculates total event costs" },
    { id: "volunteer", name: "Volunteer Coordinator", desc: "Assigns physical shifts based on schedule" },
    { id: "attendance_ml", name: "ML Attendance Predictor", desc: "Uses Gradient Boosting for drop-off rates" }
  ]

  return (
    <div className="bg-[#1e1e1e] border border-vscode-border rounded shadow-xl font-mono text-sm w-full max-w-4xl mx-auto mt-8">
      <div className="flex bg-[#252526] text-[11px] uppercase tracking-wider rounded-t">
        <div className="px-4 py-2 border-b-[1px] border-vscode-blue text-vscode-text bg-[#1e1e1e]">event_config.json</div>
      </div>
      
      <form onSubmit={handleSubmit} className="p-6 text-vscode-text flex flex-col gap-6">
        
        <div className="grid grid-cols-2 gap-6">
          <div className="flex flex-col gap-4 border-r border-vscode-border pr-6">
            <h3 className="text-vscode-blue text-xs tracking-widest uppercase mb-2">Core Parameters</h3>
            <div>
              <span className="text-vscode-purple">"event_name"</span>: 
              <input required name="event_name" type="text" defaultValue="Neurathon 2026" className="ml-2 bg-[#2d2d2d] border border-vscode-border text-vscode-orange px-2 py-1 rounded outline-none focus:border-vscode-blue w-full max-w-[200px]" />
            </div>
            <div>
              <span className="text-vscode-purple">"expected_crowd"</span>: 
              <input required name="expected_crowd" type="number" defaultValue={1500} className="ml-2 bg-[#2d2d2d] border border-vscode-border text-vscode-green px-2 py-1 rounded outline-none focus:border-vscode-blue w-24" />
            </div>
            <div className="flex flex-col">
              <span className="text-vscode-purple mb-1">"marketing_prompt"</span>: 
              <textarea required name="marketing_prompt" defaultValue="We are hosting a massive AI hackathon with top IITs. Make it sound highly competitive." rows={3} className="bg-[#2d2d2d] border border-vscode-border text-vscode-orange px-3 py-2 rounded outline-none focus:border-vscode-blue resize-none"></textarea>
            </div>
            <div>
              <span className="text-vscode-purple">"participants_csv"</span>: 
              <input name="participants_csv" type="file" accept=".csv" className="mt-2 block w-full text-vscode-blue file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:bg-vscode-blue file:text-white hover:file:bg-blue-600" />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <h3 className="text-vscode-purple text-xs tracking-widest uppercase mb-2">Dynamic Swarm Agents</h3>
            <p className="text-[10px] text-gray-500 mb-2">Select which advanced cognitive agents the Supervisor should queue for execution.</p>
            
            {optionalAgents.map(agent => (
              <label key={agent.id} className="flex items-start gap-3 p-3 border border-vscode-border bg-[#252526] rounded cursor-pointer hover:border-vscode-blue transition-colors">
                <input 
                  type="checkbox" 
                  checked={selectedAgents.includes(agent.id)} 
                  onChange={() => toggleAgent(agent.id)}
                  className="mt-1 accent-vscode-blue bg-[#1e1e1e]"
                />
                <div className="flex flex-col">
                  <span className="text-vscode-text font-bold text-xs">{agent.name}</span>
                  <span className="text-[10px] text-gray-400 mt-1">{agent.desc}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-4 border-t border-vscode-border pt-6 flex justify-end">
          <button type="submit" disabled={loading} className="bg-vscode-blue/20 border border-vscode-blue text-vscode-blue hover:bg-vscode-blue hover:text-white px-8 py-3 rounded transition-all tracking-widest text-xs font-bold shadow-[0_0_15px_rgba(86,156,214,0.3)]">
            {loading ? "INITIALIZING MCTS..." : "> BOOT SWARM ARCHITECTURE"}
          </button>
        </div>
      </form>
    </div>
  )
}