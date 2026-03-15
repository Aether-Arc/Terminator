"use client"
import { useState, useEffect, useRef } from 'react'
import { Send, CheckCircle, Mail, History, Clock, Edit2, Save, MessageSquare, Plus, PanelLeftClose, PanelLeftOpen, Sparkles, LayoutTemplate, Briefcase, Bell, BellOff, Trash2 } from 'lucide-react'
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

  // 🚀 WebSocket State for Real-Time Streaming
  const ws = useRef<WebSocket | null>(null)
  const [liveAction, setLiveAction] = useState("Analyzing request...")

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

    // 🚀 Attach WebSocket to stream Agent activity to the Dashboard
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

    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setStatus("PROCESSING_UPDATE");
    setLiveAction("Connecting to Swarm..."); // Reset live text

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: params.id,
          payload: {
            action: "prompt",
            message: userMessage,
            auto_notify: autoNotify 
          }
        })
      });
      const data = await res.json();

      // If the backend rejects the request, show the real error message!
      if (data.status === "error") {
        setMessages(prev => [...prev, { role: 'ai', content: data.message }]);
        setStatus("AWAITING_APPROVAL");
        return; // Stop execution
      }

      // Proceed normally if successful
      if (data.schedule) setSchedule(data.schedule);

      const incomingOutputs = data.agent_outputs || data;
      
      setOutputs(prev => ({
        ...prev,
        marketing: incomingOutputs.marketing || prev.marketing,
        comms: incomingOutputs.comms || incomingOutputs.emails || prev.comms,
        operations: incomingOutputs.operations || prev.operations
      }));

      // 🚀 Fix: Use backend Audit Log for realistic AI replies, fallback to custom message
      const defaultSuccessMsg = autoNotify 
        ? "Workspace updated and WhatsApp notifications have been automatically dispatched!"
        : "I've updated the workspace based on your request. Please review the changes.";
        
      const aiReply = data.audit_log && data.audit_log.length > 0 
        ? data.audit_log[data.audit_log.length - 1] 
        : data.reply || defaultSuccessMsg;

      setMessages(prev => [...prev, { role: 'ai', content: data.status === "dispatched" ? "Communications dispatched successfully!" : aiReply }]);
      setStatus(data.status === "dispatched" ? "COMPLETED" : "AWAITING_APPROVAL");
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, there was an error communicating with the swarm." }]);
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
                {/* 🚀 Stream live websocket text here */}
                <span className="font-mono text-xs text-indigo-600 font-medium">{liveAction}</span>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input with Auto-Notify Toggle */}
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
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                <Clock size={14} className="text-indigo-500" /> Master Schedule
              </h3>
              
              {isEditing && (
                <button 
                  onClick={() => setSchedule([...schedule, { time: "Day 1 | 00:00 AM - 00:00 AM", session: "New Event Session" }])}
                  className="bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 hover:bg-indigo-200 transition-colors"
                >
                  <Plus size={12} /> Add Session
                </button>
              )}
            </div>
            
            <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
              {schedule.length === 0 && <p className="text-sm text-slate-400 p-5 text-center italic">No schedule generated yet. Awaiting Swarm.</p>}
              
              {/* Process Schedule into Groups */}
              {(() => {
                const grouped: Record<string, any[]> = {};
                schedule.forEach((item, index) => {
                  let day = "Day 1";
                  let timeOnly = item.time || "TBD";
                  let sessionName = item.session || "Event Session";

                  const isSessionJustDay = /^Day\s*\d+$/i.test((item.session || "").trim());
                  
                  if (isSessionJustDay && item.status && item.status !== "Locked" && item.status !== "Pending") {
                    day = item.session.trim();
                    sessionName = item.status.trim();
                    timeOnly = item.time?.trim() || "TBD";
                  }
                  else if (item.time && item.time.includes("|")) {
                    const parts = item.time.split("|");
                    const dayPartIndex = parts.findIndex(p => p.toLowerCase().includes("day"));
                    
                    if (dayPartIndex !== -1) {
                      day = parts[dayPartIndex].trim();
                      timeOnly = parts.filter((_, idx) => idx !== dayPartIndex).join("|").trim();
                    } else {
                      day = parts[0].trim();
                      timeOnly = parts.slice(1).join("|").trim();
                    }
                  } 
                  else if (item.session && item.session.match(/Day\s*\d+/i)) {
                    const match = item.session.match(/Day\s*\d+/i);
                    if (match) {
                      day = match[0].trim();
                      sessionName = item.session.replace(/Day\s*\d+[-:| ]*/i, "").trim() || "Event Session";
                      timeOnly = item.time?.trim() || "TBD";
                    }
                  }

                  if (!grouped[day]) grouped[day] = [];
                  grouped[day].push({ ...item, session: sessionName, timeOnly, originalIndex: index });
                });

                return Object.entries(grouped).map(([day, items]) => (
                  <div key={day} className="mb-10 last:mb-0">
                    <div className="flex items-center gap-4 mb-6">
                      <div className="h-px flex-1 bg-slate-200"></div>
                      <span className="bg-slate-100 text-slate-600 font-black text-xs uppercase tracking-widest px-4 py-1.5 rounded-full border border-slate-200 shadow-sm">
                        {day}
                      </span>
                      <div className="h-px flex-1 bg-slate-200"></div>
                    </div>

                    <div className="relative border-l-2 border-slate-200 ml-4 md:ml-6 space-y-6 pb-4">
                      {items.map((item, i) => (
                        <div key={i} className="relative pl-6 md:pl-8 group">
                          {/* Timeline Dot */}
                          <div className="absolute w-3.5 h-3.5 bg-white border-2 border-indigo-500 rounded-full -left-[9px] top-4 ring-4 ring-white group-hover:bg-indigo-500 transition-colors"></div>
                          
                          {/* Event Card */}
                          <div className="bg-slate-50 border border-slate-100 hover:border-indigo-100 p-4 rounded-2xl shadow-sm hover:shadow-md transition-all flex flex-col gap-2 relative">
                            {isEditing ? (
                              <div className="flex flex-wrap gap-3 items-center">
                                <input 
                                  className="bg-white text-indigo-600 text-xs font-mono font-bold p-2.5 rounded-lg w-36 border border-slate-200 outline-none focus:ring-2 focus:ring-indigo-100 transition-all" 
                                  value={item.timeOnly} 
                                  onChange={e => { 
                                    const newSched = [...schedule]; 
                                    newSched[item.originalIndex].time = `${day} | ${e.target.value}`; 
                                    setSchedule(newSched); 
                                  }} 
                                />
                                <input 
                                  className="bg-white text-slate-800 text-sm flex-1 p-2.5 rounded-lg border border-slate-200 outline-none focus:ring-2 focus:ring-indigo-100 font-semibold transition-all" 
                                  value={item.session} 
                                  onChange={e => { 
                                    const newSched = [...schedule]; 
                                    newSched[item.originalIndex].session = e.target.value; 
                                    setSchedule(newSched); 
                                  }} 
                                />
                                <button 
                                  onClick={() => { 
                                    const newSched = schedule.filter((_, idx) => idx !== item.originalIndex); 
                                    setSchedule(newSched); 
                                  }}
                                  className="text-red-400 hover:text-red-600 hover:bg-red-50 p-2 rounded-lg transition-colors"
                                  title="Delete Session"
                                >
                                  <Trash2 size={16} />
                                </button>
                              </div>
                            ) : (
                              <div className="flex flex-col md:flex-row md:items-center gap-1 md:gap-4">
                                <span className="text-indigo-600 text-xs font-mono font-bold min-w-[140px]">
                                  {item.timeOnly}
                                </span>
                                <h4 className="text-sm font-bold text-slate-800 leading-snug">
                                  {item.session}
                                </h4>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ));
              })()}
            </div>
          </section>

          {/* COMMUNICATION HUB */}
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
              
              {outputs.marketing?.map((item: any, i: number) => {
                const isObject = typeof item.output === 'object' && item.output !== null;

                return (
                  <div key={i} className="p-5 bg-indigo-50/50 rounded-2xl border border-indigo-100 shadow-sm">
                    <div className="text-xs font-bold text-indigo-500 mb-3 bg-indigo-100 inline-block px-2.5 py-1 rounded-md">{item.task}</div>
                    
                    {isObject ? (
                      <pre className="text-[11px] text-red-500 font-mono whitespace-pre-wrap leading-relaxed">
                        {JSON.stringify(item.output, null, 2)}
                      </pre>
                    ) : (
                      <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{item.output}</p>
                    )}
                  </div>
                )
              })}
            </div>
          </section>

          {/* OPERATIONS & LOGISTICS PANEL */}
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
                const domain = item.domain || "operation";

                return (
                  <div key={i} className={`p-5 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-full hover:shadow-md transition-shadow ${domain === 'itinerary' ? 'md:col-span-2' : ''}`}>
                    
                    {/* Card Header */}
                    <div className="flex justify-between items-start mb-4">
                      <span className={`text-[10px] font-extrabold px-3 py-1.5 rounded-full uppercase tracking-widest shadow-sm ${
                        domain === 'budget' ? 'text-emerald-700 bg-emerald-100' : 
                        domain === 'volunteer' ? 'text-blue-700 bg-blue-100' :
                        domain === 'sponsor' ? 'text-purple-700 bg-purple-100' :
                        domain === 'itinerary' ? 'text-rose-700 bg-rose-100' :
                        'text-amber-700 bg-amber-100'
                      }`}>
                        {domain}
                      </span>
                      <span className="text-xs font-bold text-slate-400 max-w-[60%] truncate text-right" title={item.task}>
                        {item.task}
                      </span>
                    </div>

                    {/* Card Content Area */}
                    <div className="flex-1 bg-slate-50/50 rounded-xl p-4 border border-slate-100 overflow-y-auto max-h-[350px]">
                      
                      {/* BUDGET UI */}
                      {domain === 'budget' && isObject ? (
                        <div className="space-y-4">
                          <div className="flex justify-between items-center bg-emerald-50 text-emerald-800 p-4 rounded-xl border border-emerald-200 shadow-sm">
                            <span className="font-bold text-sm">Total Est. Cost</span>
                            <span className="font-mono font-black text-xl flex items-center gap-1">
                              {(() => {
                                const parseCost = (val: any) => {
                                  if (!val) return 0;
                                  const cleaned = String(val).replace(/[^0-9.-]+/g, "");
                                  return Number(cleaned) || 0;
                                };
                                let total = parseCost(item.output.total_calculated_cost);
                                if (total === 0 && Array.isArray(item.output.line_items)) {
                                  total = item.output.line_items.reduce((sum: number, li: any) => sum + parseCost(li.cost), 0);
                                }
                                return `${item.output.currency || "INR"} ${total.toLocaleString()}`;
                              })()}
                            </span>
                          </div>
                          <div className="space-y-2">
                            {item.output.line_items?.map((li: any, idx: number) => (
                              <div key={idx} className="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                                <div>
                                  <p className="font-bold text-slate-700 text-sm">{li.category || "Item"}</p>
                                  <p className="text-[10px] text-slate-400 italic line-clamp-1">{li.notes || "No notes."}</p>
                                </div>
                                <span className="font-mono text-slate-600 font-semibold text-sm">
                                  {Number(String(li.cost || 0).replace(/[^0-9.-]+/g, "")).toLocaleString()}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) 
                      
                      /* VOLUNTEER UI */
                      : domain === 'volunteer' && isObject ? (
                        <div className="space-y-4">
                          <div className="flex justify-between items-center bg-blue-50 text-blue-800 p-4 rounded-xl border border-blue-200 shadow-sm">
                            <span className="font-bold text-sm">Total Volunteers Needed</span>
                            <span className="font-black text-xl">{item.output.total_volunteers_required || 0}</span>
                          </div>
                          <div className="space-y-2">
                            {item.output.roles?.map((role: any, idx: number) => (
                              <div key={idx} className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                                <div className="flex justify-between items-start mb-1">
                                  <p className="font-bold text-slate-800 text-sm">{role.role_name}</p>
                                  <span className="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-0.5 rounded-lg">{role.headcount} slots</span>
                                </div>
                                <p className="text-xs text-indigo-600 font-semibold mb-1">{role.active_time}</p>
                                <p className="text-[11px] text-slate-500 italic">{role.reason}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )

                      /* SPONSOR UI */
                      : domain === 'sponsor' && isObject ? (
                        <div className="space-y-4">
                          <div className="bg-purple-50 text-purple-800 p-4 rounded-xl border border-purple-200 shadow-sm">
                            <h4 className="font-bold text-sm mb-2 flex items-center gap-2">
                              📧 {item.output.pitch_subject || "Sponsorship Pitch"}
                            </h4>
                            <p className="text-xs opacity-80 whitespace-pre-wrap leading-relaxed">{item.output.pitch_body || "Please see our tiers below."}</p>
                          </div>
                          
                          <div>
                            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Sponsorship Tiers</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                              {item.output.tiers?.map((tier: any, idx: number) => (
                                <div key={idx} className="bg-white border border-slate-200 p-3 rounded-xl shadow-sm text-center flex flex-col">
                                  <span className="font-black text-slate-700 text-sm uppercase tracking-wide">{tier.name}</span>
                                  <span className="text-purple-600 font-mono font-bold text-lg my-1">{tier.price}</span>
                                  <p className="text-[10px] text-slate-500 italic flex-1">{tier.perks}</p>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div>
                            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Target Companies</h4>
                            <div className="space-y-2">
                              {item.output.target_sponsors?.map((sponsor: any, idx: number) => (
                                <div key={idx} className="bg-white border border-slate-200 p-3 rounded-xl shadow-sm flex flex-col gap-1">
                                  <span className="font-bold text-slate-700 text-sm">{sponsor.company}</span>
                                  <p className="text-xs text-slate-500 italic">"{sponsor.pitch}"</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )

                      /* ITINERARY UI */
                      : domain === 'itinerary' && Array.isArray(item.output) ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {item.output.map((event: any, idx: number) => (
                            <div key={idx} className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                                <div className="flex justify-between items-start mb-1">
                                  <p className="font-bold text-slate-800 text-sm truncate">{event.session}</p>
                                  <span className="bg-rose-50 text-rose-600 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{event.type || 'Event'}</span>
                                </div>
                                <p className="text-xs text-indigo-600 font-semibold mb-2">{event.time} • {event.location || 'TBD'}</p>
                                <p className="text-[11px] text-slate-500 italic line-clamp-2">{event.description}</p>
                            </div>
                          ))}
                        </div>
                      )

                      /* RAW JSON FALLBACK */
                      : isObject ? (
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