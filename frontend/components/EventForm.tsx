"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Calendar, MapPin, Users, Sparkles, Upload, FileText } from 'lucide-react'

export default function EventForm() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [selectedAgents, setSelectedAgents] = useState<string[]>(["marketing", "email", "budget", "sponsor", "volunteer"])

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

    // Perfectly maps to the backend event_data dictionary
    const payload = {
      name: formData.get("event_name"),
      expected_crowd: parseInt(formData.get("expected_crowd") as string),
      location: formData.get("location"),
      date: formData.get("date"),
      user_constraints: formData.get("user_constraints"), 
      csv_content: csvContent, 
      requested_agents: selectedAgents
    }

    localStorage.setItem("eventPayload", JSON.stringify(payload))
    
    router.push('/agents')
  }

  const optionalAgents = [
    { id: "sponsor", name: "Sponsorship Agent", desc: "Browses live web to draft targeted corporate pitches." },
    { id: "budget", name: "Financial CFO Agent", desc: "Researches local prices to build bottom-up budgets." },
    { id: "volunteer", name: "Operations Coordinator", desc: "Assigns physical shifts based on the timeline." },
    { id: "marketing", name: "Marketing Director", desc: "Researches trends to write viral social media copy." },
    { id: "email", name: "Communications Agent", desc: "Drafts hyper-personalized email invites." }
  ]

  return (
    <div className="bg-white border border-slate-200 rounded-3xl shadow-xl shadow-slate-200/50 w-full max-w-4xl mx-auto mt-8 overflow-hidden font-sans">
      <div className="bg-slate-50 px-8 py-5 border-b border-slate-100 flex items-center gap-3">
        <Sparkles className="text-indigo-500" size={20} />
        <h2 className="text-slate-800 font-semibold text-lg">Event Intelligence Configuration</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="p-8 flex flex-col gap-8">
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          
          {/* LEFT COLUMN: Core Event Details */}
          <div className="flex flex-col gap-5">
            <h3 className="text-slate-400 text-xs font-bold tracking-widest uppercase mb-1">Core Parameters</h3>
            
            <div>
              <label className="text-slate-600 text-sm font-medium mb-1.5 block">Event Name</label>
              <input required name="event_name" type="text" placeholder="e.g., Global AI Summit 2026" className="w-full bg-slate-50 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-slate-600 text-sm font-medium mb-1.5 flex items-center gap-1.5"><Users size={14}/> Expected Crowd</label>
                <input required name="expected_crowd" type="number" defaultValue={500} className="w-full bg-slate-50 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              </div>
              <div>
                <label className="text-slate-600 text-sm font-medium mb-1.5 flex items-center gap-1.5"><Calendar size={14}/> Event Date</label>
                <input required name="date" type="date" className="w-full bg-slate-50 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" />
              </div>
            </div>

            <div>
              <label className="text-slate-600 text-sm font-medium mb-1.5 flex items-center gap-1.5"><MapPin size={14}/> Location / Venue</label>
              <input required name="location" type="text" placeholder="e.g., Moscone Center, San Francisco" className="w-full bg-slate-50 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400" />
            </div>

            <div className="flex flex-col">
              <label className="text-slate-600 text-sm font-medium mb-1.5 flex items-center gap-1.5"><FileText size={14}/> Event Goals & Constraints (Prompt)</label>
              <textarea required name="user_constraints" placeholder="Describe the vibe, requirements, or specific requests. E.g., 'Make it a highly technical hackathon. We need a strict 1-hour lunch break and a main stage keynote.'" rows={4} className="w-full bg-slate-50 border border-slate-200 text-slate-800 px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none placeholder:text-slate-400"></textarea>
            </div>

            <div>
              <label className="text-slate-600 text-sm font-medium mb-1.5 flex items-center gap-1.5"><Upload size={14}/> Guest List (Optional CSV)</label>
              <input name="participants_csv" type="file" accept=".csv" className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100 transition-all cursor-pointer" />
            </div>
          </div>

          {/* RIGHT COLUMN: Agent Selection */}
          <div className="flex flex-col gap-3">
            <h3 className="text-slate-400 text-xs font-bold tracking-widest uppercase mb-1">Swarm Delegation</h3>
            <p className="text-sm text-slate-500 mb-2">Select the specialist AI agents to run alongside the core Planner and Scheduler.</p>
            
            <div className="flex flex-col gap-3">
              {optionalAgents.map(agent => (
                <label key={agent.id} className={`flex items-center gap-4 p-4 border rounded-2xl cursor-pointer transition-all ${selectedAgents.includes(agent.id) ? 'bg-indigo-50/50 border-indigo-200 shadow-sm' : 'bg-white border-slate-100 hover:border-slate-200 hover:bg-slate-50'}`}>
                  <input 
                    type="checkbox" 
                    checked={selectedAgents.includes(agent.id)} 
                    onChange={() => toggleAgent(agent.id)}
                    className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-600"
                  />
                  <div className="flex flex-col">
                    <span className="text-slate-800 font-semibold text-sm">{agent.name}</span>
                    <span className="text-xs text-slate-500 mt-0.5">{agent.desc}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* SUBMIT BUTTON */}
        <div className="mt-4 pt-6 flex justify-end">
          <button type="submit" disabled={loading} className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-xl transition-all font-semibold shadow-lg shadow-indigo-600/30 disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2">
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Orchestrating Swarm...
              </span>
            ) : (
              <>Launch Event Intelligence <Sparkles size={18}/></>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}