"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function EventForm() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    
    // Extract form data
    const formData = new FormData(e.currentTarget)
    const payload = {
      name: formData.get("event_name"),
      expected_crowd: parseInt(formData.get("expected_crowd") as string),
      marketing_prompt: formData.get("marketing_prompt"),
      // We skip actual file upload for JSON APIs to avoid serialization errors in the demo
      has_csv: !!formData.get("participants_csv") 
    }

    // Save payload to localStorage and redirect to the agents graph 
    // to let the visualizer handle the API fetch, websocket, and data persistence.
    localStorage.setItem("eventPayload", JSON.stringify(payload))
    router.push('/agents')
  }

  return (
    <div className="bg-[#1e1e1e] border border-vscode-border rounded shadow-xl font-mono text-sm terminal-glow w-full max-w-3xl mx-auto mt-8">
      <div className="flex bg-[#252526] text-[11px] uppercase tracking-wider rounded-t">
        <div className="px-4 py-2 border-b-[1px] border-vscode-blue text-vscode-text bg-[#1e1e1e]">event_config.json</div>
      </div>
      
      <form onSubmit={handleSubmit} className="p-6 text-vscode-text flex flex-col gap-4">
        <div>
          <span className="text-vscode-purple">"event_name"</span>: 
          <input required name="event_name" type="text" defaultValue="Neurathon 2026" className="ml-2 bg-[#2d2d2d] border border-vscode-border text-vscode-orange px-2 py-1 rounded outline-none focus:border-vscode-blue w-64" />
          <span className="text-vscode-text">,</span>
        </div>

        <div>
          <span className="text-vscode-purple">"expected_crowd"</span>: 
          <input required name="expected_crowd" type="number" defaultValue={1500} className="ml-2 bg-[#2d2d2d] border border-vscode-border text-vscode-green px-2 py-1 rounded outline-none focus:border-vscode-blue w-32" />
          <span className="text-vscode-text">,</span>
        </div>

        <div>
          <span className="text-vscode-purple">"marketing_prompt"</span>: 
          <span className="text-vscode-text">{" {"}</span>
          <textarea required name="marketing_prompt" defaultValue="We are hosting a massive AI hackathon with top IITs. Make it sound highly competitive and futuristic." rows={3} className="block mt-2 ml-8 bg-[#2d2d2d] border border-vscode-border text-vscode-orange px-2 py-1 rounded outline-none focus:border-vscode-blue w-[80%] resize-none"></textarea>
          <span className="text-vscode-text mt-2 block">{"},"}</span>
        </div>

        <div>
          <span className="text-vscode-purple">"participants_csv"</span>: 
          <input name="participants_csv" type="file" accept=".csv" className="ml-2 text-vscode-blue file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:bg-vscode-blue file:text-white hover:file:bg-blue-600" />
        </div>

        <div className="mt-8 border-t border-vscode-border pt-6 flex justify-end">
          <button type="submit" disabled={loading} className="bg-vscode-blue/20 border border-vscode-blue text-vscode-blue hover:bg-vscode-blue hover:text-white px-6 py-2 rounded transition-all tracking-widest text-xs font-bold shadow-[0_0_10px_rgba(86,156,214,0.2)]">
            {loading ? "INITIALIZING SWARM..." : "> DEPLOY EVENT SWARM"}
          </button>
        </div>
      </form>
    </div>
  )
}