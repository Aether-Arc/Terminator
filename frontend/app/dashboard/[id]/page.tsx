"use client"
import { useState, useEffect } from 'react'
import { Send, CheckCircle, Mail, History, Clock, Edit2, Save, MessageSquare, Plus, PanelLeftClose, PanelLeftOpen, Sparkles, LayoutTemplate, Briefcase, Bell, BellOff } from 'lucide-react'
import Link from 'next/link'
import { fetchHistory, fetchThreadState } from '../../../lib/api'

export default function Dashboard({ params }: { params: { id: string } }) {
  // Navigation & History State
  const [threads, setThreads] = useState<any[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Chat & Toggle State
  const [chatInput, setChatInput] = useState("")
  const [autoNotify, setAutoNotify] = useState(false) // 🚀 Auto-WhatsApp Toggle
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([
    { role: 'ai', content: 'Hello! I am your Event Intelligence Agent. How can we adjust the current plan?' }
  ])

  // Workspace State
  const [schedule, setSchedule] = useState<any[]>([])
  const [outputs, setOutputs] = useState<any>({ marketing: [], comms: [], operations: [] })
  const [status, setStatus] = useState("AWAITING_APPROVAL")
  const [isEditing, setIsEditing] = useState(false)

  // Load history and thread data on mount
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

    if (params.id) {
      fetchThreadState(params.id)
        .then(data => {
          if (data.schedule) setSchedule(data.schedule);

          if (data.agent_outputs) {
            setOutputs({
              marketing: data.agent_outputs.marketing || [],
              comms: data.agent_outputs.comms || data.agent_outputs.emails || [],
              operations: data.agent_outputs.operations || []
            });
          }
          if (data.status) setStatus(data.status);
        })
        .catch(err => console.error("Could not load thread data", err));
    }
  }, [params.id])

  // Handles Chat Submission
  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput("");

    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setStatus("PROCESSING_UPDATE");

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: params.id,
          payload: {
            action: "prompt",
            message: userMessage,
            auto_notify: autoNotify // 🚀 Tells backend to send WhatsApp immediately
          }
        })
      });
      const data = await res.json();

      if (data.schedule) setSchedule(data.schedule);

      const incomingOutputs = data.agent_outputs || data;
      
      setOutputs(prev => ({
        ...prev,
        marketing: incomingOutputs.marketing || prev.marketing,
        comms: incomingOutputs.comms || incomingOutputs.emails || prev.comms,
        operations: incomingOutputs.operations || prev.operations
      }));

      const successMsg = autoNotify 
        ? "Workspace updated and WhatsApp notifications have been automatically dispatched!"
        : "I've updated the workspace based on your request. Please review the changes.";

      setMessages(prev => [...prev, { role: 'ai', content: data.status === "dispatched" ? "Communications dispatched successfully!" : successMsg }]);
      setStatus(data.status === "dispatched" ? "COMPLETED" : "AWAITING_APPROVAL");
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, there was an error updating the event." }]);
      setStatus("AWAITING_APPROVAL");
    }
  }

  // Saves manual UI edits
  const handleSaveEdits = async () => {
    setIsEditing(false);
    setStatus("SAVING_EDITS");
    setMessages(prev => [...prev, { role: 'user', content: "*(Saved manual edits to workspace)*" }]);

    try {
      await fetch('http://localhost:8000/api/edit/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: params.id,
          schedule: schedule
        })
      });
      setMessages(prev => [...prev, { role: 'ai', content: "Manual edits successfully saved to memory." }]);
    } catch (e) {
      console.error(e);
    }
    setStatus("AWAITING_APPROVAL");
  }

  const handleApprove = async () => {
    setStatus("FINALIZING");
    setMessages(prev => [...prev, { role: 'user', content: "Approve all assets." }]);

    try {
      const res = await fetch('http://localhost:8000/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: params.id })
      });
      const data = await res.json();

      const incomingOutputs = data.agent_outputs || data;

      if (incomingOutputs.marketing || incomingOutputs.email_outreach_logs || incomingOutputs.comms) {
        setOutputs(prev => ({
          ...prev,
          marketing: incomingOutputs.marketing || prev.marketing,
          comms: incomingOutputs.email_outreach_logs || incomingOutputs.comms || prev.comms
        }));
      }

      setMessages(prev => [...prev, { role: 'ai', content: "Event approved! All assets are finalized and ready for deployment." }]);
      setStatus("COMPLETED");
    } catch (e) {
      console.error(e);
      setStatus("AWAITING_APPROVAL");
    }
  }

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
          <Link href="/" className="w-full bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-100 text-sm py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 font-semibold transition-all">
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
              <div className="bg-white text-slate-500 p-4 rounded-2xl rounded-bl-none text-sm border border-slate-200 shadow-sm flex items-center gap-3">
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-75"></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-150"></span>
                </span>
                Updating workspace...
              </div>
            </div>
          )}
        </div>

        {/* 🚀 UPGRADED: Chat Input with Auto-Notify Toggle */}
        <div className="p-4 bg-white border-t border-slate-100 flex flex-col gap-3">
          <div className="flex items-center justify-end px-2">
            <button 
              type="button"
              onClick={() => setAutoNotify(!autoNotify)}
              className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-full transition-all ${
                autoNotify 
                  ? 'bg-green-100 text-green-700 border border-green-200' 
                  : 'bg-slate-100 text-slate-500 border border-slate-200 hover:bg-slate-200'
              }`}
            >
              {autoNotify ? <Bell size={12} className="animate-pulse" /> : <BellOff size={12} />}
              {autoNotify ? "Auto-WhatsApp ON" : "Auto-WhatsApp OFF"}
            </button>
          </div>

          <form onSubmit={handleChat} className="flex items-center gap-3 bg-slate-50 border border-slate-200 p-2 rounded-2xl focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder={autoNotify ? "e.g., Delay keynote by 1hr (Will auto-send!)" : "e.g., Delay keynote, or send custom broadcast..."}
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
            {status === "AWAITING_APPROVAL" && (
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
                      <input className="bg-white text-indigo-600 text-xs font-mono p-2 rounded-lg w-28 border border-slate-200 outline-none shadow-sm" value={item.time} onChange={e => { const newSched = [...schedule]; newSched[i].time = e.target.value; setSchedule(newSched); }} />
                      <input className="bg-white text-slate-700 text-sm flex-1 p-2 rounded-lg border border-slate-200 outline-none shadow-sm font-medium" value={item.session} onChange={e => { const newSched = [...schedule]; newSched[i].session = e.target.value; setSchedule(newSched); }} />
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

          {/* 🚀 COMMUNICATION HUB (Displays the CommsAgent Drafts) */}
          <section>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2"><Mail size={14} /> Communication Hub</h3>
              <button onClick={() => { setChatInput("Send all drafted communications"); handleChat({ preventDefault: () => { } } as any); }} className="bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 hover:bg-emerald-500 shadow-sm transition-all"><Send size={12} /> Dispatch All</button>
            </div>

            <div className="space-y-4">
              {outputs.comms?.length === 0 && <p className="text-sm text-slate-400 italic text-center p-4">No comms drafted yet.</p>}
              {outputs.comms?.map((item: any, i: number) => {
                const data = item.output;
                return (
                  <div key={i} className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
                    <div className="flex justify-between items-center mb-3">
                      <div className="text-xs font-bold text-slate-500 bg-slate-50 inline-block px-2.5 py-1 rounded-md">{item.task}</div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${data.status === 'SENT' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>{data.status || 'DRAFTED'}</span>
                    </div>

                    {data.use_email && (
                      <div className="mb-3 bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <p className="text-xs text-slate-500 mb-1">📧 <strong>{data.email_subject}</strong></p>
                        <p className="text-sm text-slate-600 whitespace-pre-wrap">{data.email_body}</p>
                      </div>
                    )}
                    {data.use_whatsapp && (
                      <div className="bg-green-50 p-3 rounded-lg border border-green-100">
                        <p className="text-xs text-green-700 mb-1 font-bold">💬 WhatsApp</p>
                        <p className="text-sm text-green-800 whitespace-pre-wrap">{data.whatsapp_body}</p>
                      </div>
                    )}
                  </div>
                )
              })}
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
                  <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{item.output}</p>
                </div>
              ))}
            </div>
          </section>

          {/* OPERATIONS & LOGISTICS PANEL (Budget formatting safe) */}
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
                const isBudget = item.domain === 'budget' && isObject && item.output.total_calculated_cost !== undefined;

                return (
                  <div key={i} className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                      <span className={`text-[10px] font-extrabold px-3 py-1.5 rounded-full uppercase tracking-widest shadow-sm ${
                        isBudget ? 'text-emerald-700 bg-emerald-100' : 'text-amber-700 bg-amber-100'
                      }`}>
                        {item.domain || "Operation"}
                      </span>
                      <span className="text-xs font-bold text-slate-400 max-w-[60%] truncate text-right" title={item.task}>
                        {item.task}
                      </span>
                    </div>

                    <div className="flex-1 bg-slate-50/50 rounded-xl p-4 border border-slate-100 overflow-y-auto max-h-[350px]">
                      {isBudget ? (
                        <div className="space-y-4">
                          <div className="flex justify-between items-center bg-emerald-50 text-emerald-800 p-4 rounded-xl border border-emerald-200 shadow-sm">
                            <span className="font-bold text-sm">Total Est. Cost</span>
                            <span className="font-mono font-black text-xl flex items-center gap-1">
                              {item.output.currency || "$"} {Number(item.output.total_calculated_cost || 0).toLocaleString()}
                            </span>
                          </div>
                          <div className="space-y-2">
                            {item.output.line_items?.map((li: any, idx: number) => (
                              <div key={idx} className="flex flex-col gap-1 bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                                <div className="flex justify-between items-center">
                                  <p className="font-bold text-slate-700 text-sm">{li.category || "Item"}</p>
                                  <span className="font-mono text-slate-600 font-semibold text-sm">
                                    {Number(li.cost || 0).toLocaleString()}
                                  </span>
                                </div>
                                <p className="text-xs text-slate-400 italic leading-relaxed">{li.notes || "No notes provided."}</p>
                              </div>
                            ))}
                          </div>
                          <p className="text-[10px] text-slate-400 text-right italic pt-2">Location Indexed: {item.output.pricing_location || "Unknown"}</p>
                        </div>
                      ) : isObject ? (
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