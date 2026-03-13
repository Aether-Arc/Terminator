"use client"
import { useState, useEffect } from 'react'
import { Send, CheckCircle, Mail, Clock, Edit2, Save, MessageSquare, Briefcase } from 'lucide-react'

export default function Dashboard({ params }: { params: { id: string } }) {
  const [chatInput, setChatInput] = useState("")
  const [schedule, setSchedule] = useState<any[]>([])
  const [outputs, setOutputs] = useState<any>({ marketing: [], emails: [], operations: [] })
  const [status, setStatus] = useState("AWAITING_APPROVAL")
  const [isEditing, setIsEditing] = useState(false)

  // Submits a prompt to adjust things WITHOUT a full replan
  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    const prompt = chatInput;
    setChatInput("");
    setStatus("PROCESSING_UPDATE");

    // LangGraph interrupt resume payload
    const res = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ 
        thread_id: params.id, 
        payload: { action: "prompt", message: prompt } 
      })
    });
    const data = await res.json();
    
    if (data.schedule) setSchedule(data.schedule);
    if (data.agent_outputs) setOutputs(data.agent_outputs);
    setStatus("AWAITING_APPROVAL");
  }

  // Saves manual UI edits WITHOUT any LLM generation
  const handleSaveEdits = async () => {
    setIsEditing(false);
    setStatus("SAVING_EDITS");
    
    const res = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ 
        thread_id: params.id, 
        payload: { action: "direct_edit", schedule, agent_outputs: outputs } 
      })
    });
    setStatus("AWAITING_APPROVAL");
  }

  const handleApprove = async () => {
    setStatus("FINALIZING");
    await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ thread_id: params.id, payload: { action: "approve" } })
    });
    setStatus("COMPLETED");
  }

  return (
    <div className="flex h-screen bg-[#0f1117] text-white font-sans">
      <div className="flex-1 flex flex-col p-8 overflow-hidden">
        
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold">Event Intelligence Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1">Status: {status.replace("_", " ")}</p>
          </div>
          <div className="flex gap-4">
            {isEditing ? (
              <button onClick={handleSaveEdits} className="bg-blue-600 px-6 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-500 transition">
                <Save size={18} /> Save Edits
              </button>
            ) : (
              <button onClick={() => setIsEditing(true)} className="bg-slate-700 px-6 py-2 rounded-lg flex items-center gap-2 hover:bg-slate-600 transition">
                <Edit2 size={18} /> Edit Manually
              </button>
            )}
            {status !== "COMPLETED" && (
              <button onClick={handleApprove} className="bg-emerald-600 px-6 py-2 rounded-lg flex items-center gap-2 hover:bg-emerald-500 transition">
                <CheckCircle size={18} /> Approve All Assets
              </button>
            )}
          </div>
        </header>

        <div className="grid grid-cols-2 gap-6 flex-1 overflow-hidden">
          
          {/* COLUMN 1: Schedule */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6 overflow-y-auto">
            <h2 className="text-sm uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
              <Clock size={16}/> Master Schedule
            </h2>
            {schedule.map((item: any, i) => (
              <div key={i} className="mb-3 p-3 bg-white/5 rounded-lg border-l-4 border-blue-500">
                {isEditing ? (
                  <div className="flex gap-2">
                    <input 
                      className="bg-black/40 text-blue-400 text-xs font-mono p-1 rounded w-24" 
                      value={item.time} 
                      onChange={e => {
                        const newSched = [...schedule];
                        newSched[i].time = e.target.value;
                        setSchedule(newSched);
                      }}
                    />
                    <input 
                      className="bg-black/40 text-sm flex-1 p-1 rounded" 
                      value={item.session}
                      onChange={e => {
                        const newSched = [...schedule];
                        newSched[i].session = e.target.value;
                        setSchedule(newSched);
                      }}
                    />
                  </div>
                ) : (
                  <>
                    <span className="text-blue-400 text-xs font-mono">{item.time}</span>
                    <p className="text-sm font-medium mt-1">{item.session}</p>
                  </>
                )}
              </div>
            ))}
          </div>

          {/* COLUMN 2: Content (Emails, Marketing, Ops) */}
          <div className="bg-slate-900/50 border border-white/10 rounded-2xl p-6 overflow-y-auto space-y-6">
            
            {/* EMAILS */}
            <div>
              <h2 className="text-sm uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
                <Mail size={16}/> Email Campaigns
              </h2>
              {outputs.emails?.map((item: any, i: number) => (
                <div key={i} className="mb-4 p-4 bg-black/20 rounded-xl border border-white/5">
                  <div className="text-xs text-slate-400 mb-2">{item.task}</div>
                  {isEditing ? (
                    <textarea 
                      className="w-full bg-black/40 text-sm p-2 rounded min-h-[80px]" 
                      value={item.output} 
                      onChange={e => {
                        const newOutputs = {...outputs};
                        newOutputs.emails[i].output = e.target.value;
                        setOutputs(newOutputs);
                      }}
                    />
                  ) : (
                    <p className="text-xs italic text-slate-300">{item.output}</p>
                  )}
                </div>
              ))}
            </div>

            {/* MARKETING */}
            <div>
              <h2 className="text-sm uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
                <MessageSquare size={16}/> Social & Marketing
              </h2>
              {outputs.marketing?.map((item: any, i: number) => (
                <div key={i} className="mb-4 p-3 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
                  <div className="text-xs text-indigo-300 mb-2">{item.task}</div>
                  {isEditing ? (
                    <textarea 
                      className="w-full bg-black/40 text-sm p-2 rounded min-h-[80px]" 
                      value={item.output} 
                      onChange={e => {
                        const newOutputs = {...outputs};
                        newOutputs.marketing[i].output = e.target.value;
                        setOutputs(newOutputs);
                      }}
                    />
                  ) : (
                    <p className="text-xs text-slate-200">{item.output}</p>
                  )}
                </div>
              ))}
            </div>

          </div>
        </div>

        {/* Smart Chat Box for Prompting Targeted Edits */}
        <form onSubmit={handleChat} className="mt-6 flex gap-4 bg-slate-900 border border-white/10 p-2 rounded-xl">
          <input 
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Type 'Delay the event by 2 hours' or 'Change the venue to Hall B'..."
            className="flex-1 bg-transparent px-4 outline-none text-sm"
            disabled={status !== "AWAITING_APPROVAL" || isEditing}
          />
          <button type="submit" className="bg-blue-600 p-3 rounded-lg hover:bg-blue-500 disabled:opacity-50">
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  )
}