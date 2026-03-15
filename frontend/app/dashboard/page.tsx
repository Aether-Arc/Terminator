"use client"
import { useState, useEffect, useRef } from 'react'
import { Send, CheckCircle, Mail, History, Clock, Edit2, Save, MessageSquare, Plus, PanelLeftClose, PanelLeftOpen, Terminal, Sparkles, LayoutTemplate, Briefcase, Bell } from 'lucide-react'
import Link from 'next/link'
import { fetchHistory } from '../../lib/api'

export default function Dashboard({ params }: { params: { id: string } }) {
  // Navigation & History State
  const [threads, setThreads] = useState<any[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Chat State
  const [chatInput, setChatInput] = useState("")
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([
    { role: 'ai', content: 'Hello! I am your Event Intelligence Agent. How can we adjust the current plan?' }
  ])
  
  // 🚀 FIX 2: Added Auto-Notify State
  const [autoNotify, setAutoNotify] = useState(false)

  // Workspace State
  const [schedule, setSchedule] = useState<any[]>([])
  const [outputs, setOutputs] = useState<any>({ marketing: [], emails: [], operations: [] })
  const [status, setStatus] = useState("AWAITING_APPROVAL")
  const [isEditing, setIsEditing] = useState(false)

  // 🚀 FIX 1: WebSocket State for Real-Time Streaming
  const ws = useRef<WebSocket | null>(null)
  const [liveAction, setLiveAction] = useState("Analyzing request...")

  // Load history & initialize WebSocket on mount
  useEffect(() => {
    fetchHistory()
      .then(res => {
        if (res && res.threads) {
          const historyList = res.threads.map((t: string) => ({
            id: t,
            title: `Thread (${t.substring(0, 8)})`
          }));

          setThreads([
            { id: params.id, title: "Current Active Plan" },
            ...historyList.filter((t: any) => t.id !== params.id)
          ]);
        }
      })
      .catch(err => console.error("Could not fetch history", err));

    // 🚀 FIX 1: Attach WebSocket to stream Agent activity to the Dashboard
    ws.current = new WebSocket("ws://localhost:8000/ws/swarm")
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.action || data.message) {
        setLiveAction(`[${data.agent || "System"}] ${data.action || data.message}`)
      }
    }

    return () => ws.current?.close()
  }, [params.id])

  // Handles Chat Submission
  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput("");

    // Add User Message to Chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setStatus("PROCESSING_UPDATE");
    setLiveAction("Connecting to Swarm..."); // Reset live text

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({
          thread_id: params.id,
          // 🚀 FIX 2: Inject the auto_notify flag into the backend!
          payload: { action: "prompt", message: userMessage, auto_notify: autoNotify }
        })
      });
      const data = await res.json();

      if (data.schedule) setSchedule(data.schedule);
      if (data.agent_outputs) setOutputs(data.agent_outputs);

      // 🚀 FIX 3: Replaced the "Ghost Reply" with the actual Backend Audit Log
      const aiReply = data.audit_log && data.audit_log.length > 0 
        ? data.audit_log[data.audit_log.length - 1] 
        : data.reply || "Workspace successfully updated.";

      setMessages(prev => [...prev, { role: 'ai', content: aiReply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, there was an error updating the event." }]);
    }

    setStatus("AWAITING_APPROVAL");
  }

  // Saves manual UI edits
  const handleSaveEdits = async () => {
    setIsEditing(false);
    setStatus("SAVING_EDITS");
    setMessages(prev => [...prev, { role: 'user', content: "*(Saved manual edits to workspace)*" }]);

    await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        thread_id: params.id,
        payload: { action: "direct_edit", schedule, agent_outputs: outputs }
      })
    });

    setMessages(prev => [...prev, { role: 'ai', content: "Manual edits successfully saved to memory." }]);
    setStatus("AWAITING_APPROVAL");
  }

  const handleApprove = async () => {
    setStatus("FINALIZING");
    setMessages(prev => [...prev, { role: 'user', content: "Approve all assets." }]);

    await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ thread_id: params.id, payload: { action: "approve" } })
    });

    setMessages(prev => [...prev, { role: 'ai', content: "Event approved! All assets are finalized and ready for deployment." }]);
    setStatus("COMPLETED");
  }

  // Helper for status badge styles
  const getStatusStyles = (currentStatus: string) => {
    switch (currentStatus) {
      case 'COMPLETED': return 'bg-emerald-100 text-emerald-700 border-emerald-200'
      case 'PROCESSING_UPDATE': return 'bg-indigo-100 text-indigo-700 border-indigo-200 animate-pulse'
      case 'SAVING_EDITS': return 'bg-blue-100 text-blue-700 border-blue-200 animate-pulse'
      case 'AWAITING_APPROVAL': return 'bg-amber-100 text-amber-700 border-amber-200'
      default: return 'bg-slate-100 text-slate-500 border-slate-200'
    }
  }

  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 font-sans overflow-hidden">

      {/* COLUMN 1: Sidebar (History) */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-white border-r border-slate-200 flex flex-col overflow-hidden shadow-sm z-20`}>
        <div className="p-4 border-b border-slate-100">
          <Link href="/dashboard/new" className="w-full bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-100 text-sm py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 font-semibold transition-all">
            <Plus size={16} /> New Event
          </Link>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3 mt-2 px-3 flex items-center gap-2">
            <History size={12} /> Past Events
          </div>
          {threads.map((t) => (
            <Link key={t.id} href={`/dashboard/${t.id}`}>
              <div className={`px-3 py-2.5 rounded-xl text-sm flex items-center gap-3 cursor-pointer truncate transition-all ${t.id === params.id ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-600 hover:bg-slate-50'}`}>
                <MessageSquare size={14} className={t.id === params.id ? 'text-indigo-500' : 'text-slate-400'} />
                <span className="truncate">{t.title}</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* COLUMN 2: Chat Interface */}
      <div className="flex-[0.8] flex flex-col border-r border-slate-200 bg-white min-w-[350px] z-10 shadow-sm relative">
        <header className="h-16 border-b border-slate-100 flex items-center justify-between px-5 bg-white">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-slate-400 hover:text-indigo-600 transition-colors bg-slate-50 hover:bg-indigo-50 p-1.5 rounded-lg">
              {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
            </button>
            <div className="font-bold text-slate-800 flex items-center gap-2">
              <Sparkles size={18} className="text-indigo-500" /> Copilot
            </div>
          </div>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${m.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-none shadow-indigo-200'
                  : 'bg-white text-slate-700 rounded-bl-none border border-slate-200'
                }`}>
                {m.content}
              </div>
            </div>
          ))}
          {status === "PROCESSING_UPDATE" && (
            <div className="flex justify-start">
              <div className="bg-white text-slate-600 p-4 rounded-2xl rounded-bl-none text-sm border border-slate-200 shadow-sm flex items-center gap-3">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-75"></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-150"></span>
                </span>
                {/* 🚀 FIX 1: Stream live websocket text here */}
                <span className="font-mono text-xs text-indigo-600 font-medium">{liveAction}</span>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input Area */}
        <div className="p-4 bg-white border-t border-slate-100 flex flex-col gap-3">
          
          {/* 🚀 FIX 2: Auto-Notify Toggle Switch */}
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-1.5 text-slate-400">
               <Bell size={12} className={autoNotify ? 'text-emerald-500' : ''} />
               <span className="text-[10px] font-bold uppercase tracking-wider">Alerts</span>
            </div>
            <label className="flex items-center gap-2 cursor-pointer group">
              <span className={`text-xs font-semibold transition-colors ${autoNotify ? 'text-emerald-600' : 'text-slate-400 group-hover:text-slate-600'}`}>
                Auto-Notify Participants
              </span>
              <div className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${autoNotify ? 'bg-emerald-500' : 'bg-slate-200'}`}>
                <input type="checkbox" className="sr-only" checked={autoNotify} onChange={() => setAutoNotify(!autoNotify)} disabled={status === "PROCESSING_UPDATE" || isEditing} />
                <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${autoNotify ? 'translate-x-4' : 'translate-x-1'}`} />
              </div>
            </label>
          </div>

          <form onSubmit={handleChat} className="flex items-center gap-3 bg-slate-50 border border-slate-200 p-2 rounded-2xl focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="e.g., Delay the event by 2 hours..."
              className="flex-1 bg-transparent px-3 outline-none text-sm text-slate-800 placeholder:text-slate-400"
              disabled={status === "PROCESSING_UPDATE" || isEditing}
            />
            <button type="submit" disabled={!chatInput.trim() || status === "PROCESSING_UPDATE"} className="bg-indigo-600 p-2.5 rounded-xl text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm shadow-indigo-200">
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>

      {/* COLUMN 3: Live Workspace (Outputs & Schedule) */}
      <div className="flex-[1.2] flex flex-col bg-slate-50 overflow-hidden">

        <header className="h-16 border-b border-slate-200 flex items-center justify-between px-8 bg-white shadow-sm z-10">
          <h2 className="font-bold text-slate-800 flex items-center gap-3">
            <LayoutTemplate size={18} className="text-slate-400" />
            Live Workspace
            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide border ${getStatusStyles(status)}`}>
              {status.replace("_", " ")}
            </span>
          </h2>
          <div className="flex gap-3">
            {isEditing ? (
              <button onClick={handleSaveEdits} className="bg-blue-50 text-blue-600 border border-blue-200 px-4 py-2 text-sm rounded-xl font-semibold flex items-center gap-2 hover:bg-blue-100 transition-all shadow-sm">
                <Save size={16} /> Save Edits
              </button>
            ) : (
              <button onClick={() => setIsEditing(true)} className="bg-white text-slate-600 border border-slate-200 px-4 py-2 text-sm rounded-xl font-semibold flex items-center gap-2 hover:bg-slate-50 transition-all shadow-sm">
                <Edit2 size={16} /> Edit manually
              </button>
            )}
            {status !== "COMPLETED" && (
              <button onClick={handleApprove} className="bg-emerald-500 text-white px-5 py-2 text-sm rounded-xl font-semibold flex items-center gap-2 hover:bg-emerald-600 transition-all shadow-md shadow-emerald-500/20">
                <CheckCircle size={16} /> Approve Plan
              </button>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-8">

          {/* SCHEDULE PANEL */}
          <section>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2"><Clock size={14} /> Master Schedule</h3>
            <div className="bg-white border border-slate-200 rounded-2xl p-3 shadow-sm">
              {schedule.length === 0 && <p className="text-sm text-slate-400 p-5 text-center italic">No schedule generated yet. Awaiting Swarm.</p>}
              {schedule.map((item: any, i) => (
                <div key={i} className="mb-2 p-3.5 bg-slate-50 rounded-xl border-l-4 border-indigo-500 flex flex-col gap-1.5">
                  {isEditing ? (
                    <div className="flex gap-3">
                      <input className="bg-white text-indigo-600 text-xs font-mono p-2 rounded-lg w-28 border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none shadow-sm" value={item.time} onChange={e => { const newSched = [...schedule]; newSched[i].time = e.target.value; setSchedule(newSched); }} />
                      <input className="bg-white text-slate-700 text-sm flex-1 p-2 rounded-lg border border-slate-200 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none shadow-sm font-medium" value={item.session} onChange={e => { const newSched = [...schedule]; newSched[i].session = e.target.value; setSchedule(newSched); }} />
                    </div>
                  ) : (
                    <>
                      <span className="text-indigo-500 text-xs font-mono font-semibold">{item.time}</span>
                      <p className="text-sm font-medium text-slate-800">{item.session}</p>
                    </>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* EMAILS PANEL */}
          <section>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2"><Mail size={14} /> Communication Hub</h3>
            <div className="space-y-4">
              {outputs.emails?.length === 0 && <p className="text-sm text-slate-400 italic text-center p-4">No emails drafted yet.</p>}
              {outputs.emails?.map((item: any, i: number) => (
                <div key={i} className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
                  <div className="text-xs font-bold text-slate-400 mb-3 bg-slate-50 inline-block px-2.5 py-1 rounded-md">{item.task}</div>
                  {isEditing ? (
                    <textarea className="w-full bg-slate-50 text-slate-700 text-sm p-4 rounded-xl border border-slate-200 min-h-[120px] outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all" value={item.output} onChange={e => { const newOutputs = { ...outputs }; newOutputs.emails[i].output = e.target.value; setOutputs(newOutputs); }} />
                  ) : (
                    <p className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{item.output}</p>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* MARKETING PANEL */}
          <section>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2"><MessageSquare size={14} /> Social & Marketing</h3>
            <div className="space-y-4">
              {outputs.marketing?.length === 0 && <p className="text-sm text-slate-400 italic text-center p-4">No marketing assets yet.</p>}
              {outputs.marketing?.map((item: any, i: number) => (
                <div key={i} className="p-5 bg-indigo-50/50 rounded-2xl border border-indigo-100 shadow-sm">
                  <div className="text-xs font-bold text-indigo-500 mb-3 bg-indigo-100 inline-block px-2.5 py-1 rounded-md">{item.task}</div>
                  {isEditing ? (
                    <textarea className="w-full bg-white text-slate-700 text-sm p-4 rounded-xl border border-indigo-200 min-h-[120px] outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm" value={item.output} onChange={e => { const newOutputs = { ...outputs }; newOutputs.marketing[i].output = e.target.value; setOutputs(newOutputs); }} />
                  ) : (
                    <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{item.output}</p>
                  )}
                </div>
              ))}
            </div>
          </section>
          
          {/* OPERATIONS & LOGISTICS PANEL (Budget, Volunteer, Sponsor, Resource) */}
          <section className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                <Briefcase size={14} className="text-amber-500" /> Operations & Logistics
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {outputs.operations?.length === 0 && (
                <p className="text-sm text-slate-400 italic p-4 col-span-2 border border-dashed border-slate-200 rounded-2xl text-center">
                  No operational logistics drafted yet.
                </p>
              )}

              {outputs.operations?.map((item: any, i: number) => {
                const isObject = typeof item.output === 'object' && item.output !== null;

                return (
                  <div key={i} className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                      <span className="text-[10px] font-extrabold text-amber-700 bg-amber-100 px-3 py-1.5 rounded-full uppercase tracking-widest shadow-sm">
                        {item.domain || "Operation"}
                      </span>
                      <span className="text-xs font-bold text-slate-400 max-w-[60%] truncate text-right" title={item.task}>
                        {item.task}
                      </span>
                    </div>

                    <div className="flex-1 bg-slate-50/50 rounded-xl p-4 border border-slate-100 overflow-y-auto max-h-[250px]">
                      {isObject ? (
                        <pre className="text-[11px] text-slate-600 font-mono whitespace-pre-wrap leading-relaxed">
                          {JSON.stringify(item.output, null, 2)}
                        </pre>
                      ) : (
                        <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                          {item.output}
                        </p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </section>

        </div>
      </div>
    </div>
  )
}