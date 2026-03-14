"use client"
import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { createEvent, approvePlan, simulateCrisis, fetchHistory, forkEvent, fetchThreadState, sendChatCommand } from '../../lib/api'
import AgentMonitor from '../../components/AgentMonitor'
import MonteCarloChart from '../../components/MonteCarloChart'
import PipelineTracker, { NodeStatus } from '../../components/PipelineTracker'
import { Play, CheckCircle, AlertTriangle, FastForward, Server, Mail, Calendar, Share2, MessageSquare, History, Send, Plus, Edit3, LayoutTemplate, Terminal } from 'lucide-react'

export default function AgentsPage() {
  const router = useRouter()
  const [status, setStatus] = useState<"IDLE" | "PLANNING" | "AWAITING_APPROVAL" | "EXECUTING" | "COMPLETED" | "CRISIS">("IDLE")
  const [logs, setLogs] = useState<any[]>([])
  const [eventData, setEventData] = useState<any>(null)
  const [crisisInput, setCrisisInput] = useState("");

  // Advanced State for History & Time Travel
  const [activeThread, setActiveThread] = useState<string | null>(null)
  const [historyThreads, setHistoryThreads] = useState<string[]>([])
  const [chatInput, setChatInput] = useState("")
  const [simMetrics, setSimMetrics] = useState<any>(null)

  // LangGraph Telemetry State
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, NodeStatus>>({})
  const [activeLogs, setActiveLogs] = useState<Record<string, string>>({})

  // Results State
  const [schedule, setSchedule] = useState<any>(null) 
  const [scheduleStr, setScheduleStr] = useState<string>("") 
  const [marketing, setMarketing] = useState<string>("")
  const [emailLogs, setEmailLogs] = useState<any[]>([])
  const [score, setScore] = useState<number>(0)

  const ws = useRef<WebSocket | null>(null)
  const hasFired = useRef(false);

  useEffect(() => {
    fetchHistory()
      .then(res => setHistoryThreads(res?.threads || []))
      .catch(() => console.log("No history found yet."))

    if (hasFired.current) return;
    hasFired.current = true;

    ws.current = new WebSocket("ws://localhost:8000/ws/swarm")
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      setLogs(prev => [...prev, data])

      const agentMapping: Record<string, string> = {
        "PlannerAgent": "Planner",
        "SchedulerAgent": "Scheduler",
        "Orchestrator": "Human_review",
        "MarketingAgent": "Execution_phase",
        "BudgetAgent": "Execution_phase",
        "EmailAgent": "Execution_phase",
        "VolunteerAgent": "Execution_phase",
      }

      const mappedNodeName = agentMapping[data.agent] || data.agent;

      if (mappedNodeName === "Planner") {
        setNodeStatuses(prev => ({ ...prev, Planner: "running" }));
      } else if (mappedNodeName === "Scheduler") {
        setNodeStatuses(prev => ({ ...prev, Planner: "completed", Scheduler: "running" }));
      } else if (data.message && data.message.includes("Awaiting Human")) {
         setNodeStatuses(prev => ({ ...prev, Scheduler: "completed", Human_review: "running" }));
      } else if (mappedNodeName === "Execution_phase") {
         setNodeStatuses(prev => ({ ...prev, Human_review: "completed", Execution_phase: "running" }));
      }

      if (mappedNodeName) {
        setActiveLogs(prev => ({ ...prev, [mappedNodeName]: data.action || data.message || "Working..." }));
      }
    }

    const payloadStr = localStorage.getItem("eventPayload")
    if (payloadStr) {
      const payload = JSON.parse(payloadStr)
      setEventData(payload)
      startSwarm(payload)
    } else {
      router.push('/')
    }

    return () => ws.current?.close()
  }, [])

  const startSwarm = async (payload: any) => {
    setStatus("PLANNING")
    setNodeStatuses({ Planner: "running", Scheduler: "waiting", Human_review: "waiting", Execution_phase: "waiting" })
    try {
      const result = await createEvent(payload)

      setActiveThread(result.thread_id) 
      setSchedule(result.schedule)
      setScheduleStr(JSON.stringify(result.schedule, null, 2))
      if (result.stability_score) setScore(result.stability_score)

      if (result.marketing) {
         setMarketing(Array.isArray(result.marketing) ? result.marketing.map((m: any) => `[${m.task}]\n${m.output}`).join("\n\n") : result.marketing);
      }
      if (result.email_outreach_logs) {
         setEmailLogs(result.email_outreach_logs);
      }

      if (result.requires_approval) {
        setStatus("AWAITING_APPROVAL")
        setNodeStatuses(prev => ({ ...prev, Scheduler: "completed", Human_review: "running" }))
      } else {
        setStatus("COMPLETED")
      }

      fetchHistory().then(res => setHistoryThreads(res?.threads || []))
    } catch (e) {
      console.error(e)
      setStatus("IDLE")
    }
  }

  const loadPastThread = async (threadId: string) => {
    setActiveThread(threadId)
    setLogs([{ agent: "System", action: `Loaded SQLite memory for ${threadId}...`, status: "success" }])

    try {
      const data = await fetchThreadState(threadId)
      setSchedule(data.schedule)
      setScheduleStr(JSON.stringify(data.schedule, null, 2))
      
      if (data.marketing_copy) {
        setMarketing(Array.isArray(data.marketing_copy) ? data.marketing_copy.map((m: any) => `[${m.platform || m.domain}]\n${m.copy || m.output}`).join("\n\n") : data.marketing_copy)
      }
      setEmailLogs(data.email_logs || [])
      setStatus(data.status || "COMPLETED")
      
      setNodeStatuses({ Planner: "completed", Scheduler: "completed", Human_review: "completed", Execution_phase: "completed" })
    } catch (e) {
      console.error("Failed to load thread", e)
    }
  }

  const handleApprove = async () => {
    if (!activeThread) {
      alert("No active thread found to approve.");
      return;
    }

    setStatus("EXECUTING")
    setNodeStatuses(prev => ({ ...prev, Human_review: "completed", Execution_phase: "running" }))
    
    // 1. Safely validate the JSON first
    let editedScheduleJson;
    try {
      editedScheduleJson = JSON.parse(scheduleStr)
    } catch (e) {
      alert("Invalid JSON format in schedule! Please fix the brackets/quotes before approving.")
      setStatus("AWAITING_APPROVAL")
      return; // Stop execution if JSON is actually bad
    }

    // 2. Send the approval to the Backend WITH the thread_id
    try {
      // 🚀 THE FIX: Explicitly attach the activeThread as the thread_id!
      const result = await approvePlan({ 
        ...eventData, 
        thread_id: activeThread, 
        edited_plan: editedScheduleJson 
      })
      
      // Update the UI with the final generated assets
      if (result.agent_outputs?.marketing) {
         setMarketing(Array.isArray(result.agent_outputs.marketing) ? result.agent_outputs.marketing.map((m: any) => `[${m.task || m.domain}]\n${m.output || m.copy}`).join("\n\n") : result.agent_outputs.marketing);
      }
      
      setEmailLogs(result.agent_outputs?.comms || result.email_outreach_logs || [])
      setStatus("COMPLETED")
      setNodeStatuses(prev => ({ ...prev, Execution_phase: "completed" }))

      // Save the finalized data to local storage for the Dashboard
      const finalManifest = {
        event_name: eventData?.name,
        schedule: editedScheduleJson, 
        marketing: result.agent_outputs?.marketing,
        email_outreach_logs: result.agent_outputs?.comms,
        agent_outputs: result.agent_outputs || {}
      }
      localStorage.setItem("swarmResult", JSON.stringify(finalManifest))

    } catch (e: any) {
      console.error("Backend Approval Error:", e)
      alert(`Backend Error: Could not resume the Swarm. Check the terminal!`)
      setStatus("AWAITING_APPROVAL")
    }
  }

  const handleInjectCrisis = async () => {
    if (!crisisInput) return;
    setStatus("CRISIS")
    try {
      const result = await simulateCrisis({
        description: crisisInput,
        event_name: eventData?.name,
        csv_content: eventData?.csv_content,
        expected_crowd: eventData?.expected_crowd,
      })

      setSchedule(result.new_schedule)
      setScheduleStr(JSON.stringify(result.new_schedule, null, 2))

      let newEmails = emailLogs || [];
      if (result.emergency_emails_sent) {
        newEmails = [...emailLogs, ...result.emergency_emails_sent]
        setEmailLogs(newEmails)
      }
      setStatus("COMPLETED")

      const existingDataStr = localStorage.getItem("swarmResult")
      let manifest = existingDataStr ? JSON.parse(existingDataStr) : {}
      manifest.schedule = result.new_schedule
      manifest.email_outreach_logs = newEmails
      manifest.crisis_injected = result.crisis_injected
      manifest.applied_solution = result.applied_solution
      localStorage.setItem("swarmResult", JSON.stringify(manifest))

    } catch (e) {
      console.error(e)
    }
  }

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatInput || !activeThread) return;

    // 🚀 Update UI to show the Swarm is thinking
    setStatus("EXECUTING")
    setNodeStatuses(prev => ({ ...prev, Human_review: "completed", Execution_phase: "running" }))
    const input = chatInput;
    setChatInput("")

    try {
      // 🚀 THE FIX: Call the Smart Brain (resume_workflow) instead of the Time Machine!
      const result = await sendChatCommand(activeThread, input)

      // Update the UI with the surgically edited JSON
      if (result.schedule) {
        setSchedule(result.schedule)
        setScheduleStr(JSON.stringify(result.schedule, null, 2))
      }
      
      if (result.agent_outputs) {
         const outputs = result.agent_outputs;
         if (outputs.marketing) {
           setMarketing(Array.isArray(outputs.marketing) ? outputs.marketing.map((m: any) => `[${m.task || m.domain}]\n${m.output || m.copy}`).join("\n\n") : outputs.marketing);
         }
         if (outputs.comms) {
           setEmailLogs(outputs.comms);
         }
      }

      // Pause the graph again so the human can review the changes!
      setStatus("AWAITING_APPROVAL") 
      setNodeStatuses(prev => ({ ...prev, Execution_phase: "completed", Human_review: "running" }))
      
    } catch (e) {
      console.error(e)
      setStatus("AWAITING_APPROVAL")
      alert("Failed to apply intelligent updates. See console.")
    }
  }

  // Helper for status badge styles
  const getStatusStyles = (currentStatus: string) => {
    switch(currentStatus) {
      case 'COMPLETED': return 'bg-emerald-100 text-emerald-700 border-emerald-200'
      case 'CRISIS': return 'bg-red-100 text-red-700 border-red-200'
      case 'AWAITING_APPROVAL': return 'bg-amber-100 text-amber-700 border-amber-200'
      case 'IDLE': return 'bg-slate-100 text-slate-500 border-slate-200'
      default: return 'bg-indigo-100 text-indigo-700 border-indigo-200 animate-pulse'
    }
  }

  return (
    <div className="h-screen flex bg-slate-50 text-slate-800 font-sans overflow-hidden">

      {/* LEFT SIDEBAR: History */}
      <div className="w-64 border-r border-slate-200 bg-white flex flex-col z-20 shadow-sm">
        <div className="p-4 border-b border-slate-100">
          <button onClick={() => { localStorage.removeItem("eventPayload"); router.push('/') }} className="w-full flex items-center justify-center gap-2 bg-indigo-50 text-indigo-600 border border-indigo-100 px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-100 transition-all shadow-sm">
            <Plus size={16} /> New Swarm
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          <h3 className="text-[11px] text-slate-400 font-bold uppercase tracking-widest mb-3 mt-2 px-3 flex items-center gap-2">
            <History size={12} /> Saved Threads
          </h3>
          <div className="space-y-1">
            {historyThreads.map(thread => (
              <button
                key={thread}
                onClick={() => loadPastThread(thread)}
                className={`w-full text-left px-3 py-2.5 text-sm rounded-xl flex items-center gap-3 truncate transition-all ${activeThread === thread ? 'bg-indigo-50 text-indigo-700 font-medium' : 'hover:bg-slate-50 text-slate-600'}`}
              >
                <MessageSquare size={14} className={activeThread === thread ? 'text-indigo-500' : 'text-slate-400'} /> 
                <span className="truncate">{thread}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* RIGHT PANEL: Main Content */}
      <div className="flex-1 flex flex-col relative p-6 overflow-y-auto">
        
        {/* HEADER */}
        <div className="flex justify-between items-center border-b border-slate-200 pb-5 mb-6 z-10">
          <div className="flex items-center gap-3">
            <div className="bg-white p-2 rounded-lg shadow-sm border border-slate-100">
              <Server className="text-indigo-500" size={22} />
            </div>
            <h1 className="text-2xl text-slate-900 font-extrabold tracking-tight">
              EventOS <span className="text-slate-400 font-normal mx-2">/</span> <span className="text-indigo-600 font-semibold">{activeThread || "Initializing..."}</span>
            </h1>
            <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${getStatusStyles(status)} ml-2`}>
              {status.replace("_", " ")}
            </span>
          </div>

          <div className="flex gap-3">
            {status === "AWAITING_APPROVAL" && (
              <button onClick={handleApprove} className="flex items-center gap-2 bg-emerald-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-emerald-600 transition-all shadow-md shadow-emerald-500/20">
                <CheckCircle size={16} /> Approve & Resume
              </button>
            )}
            {status === "COMPLETED" && (
              <div className="flex gap-3">
                <div className="relative flex items-center">
                  <AlertTriangle size={14} className="absolute left-3 text-red-400" />
                  <input
                    type="text"
                    placeholder="Simulate custom crisis..."
                    value={crisisInput}
                    onChange={(e) => setCrisisInput(e.target.value)}
                    className="bg-white border border-slate-200 text-slate-800 pl-9 pr-3 py-2 text-sm rounded-xl outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 w-64 shadow-sm placeholder:text-slate-400"
                  />
                </div>
                <button onClick={handleInjectCrisis} className="flex items-center gap-2 bg-red-50 text-red-600 border border-red-200 px-4 py-2 rounded-xl text-sm font-semibold hover:bg-red-100 transition-all">
                  Inject
                </button>
                <button onClick={() => router.push('/dashboard')} className="flex items-center gap-2 bg-white text-indigo-600 border border-slate-200 px-5 py-2 rounded-xl text-sm font-semibold hover:bg-slate-50 transition-all shadow-sm">
                  <LayoutTemplate size={16} /> View Manifest
                </button>
              </div>
            )}
          </div>
        </div>

        {/* PIPELINE TRACKER */}
        <div className="z-10 mb-6 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
           <PipelineTracker nodeStatuses={nodeStatuses} activeLogs={activeLogs} />
        </div>

        {/* MAIN DASHBOARD GRID */}
        <div className="grid grid-cols-12 gap-6 z-10 mb-6 flex-shrink-0">

          {/* LEFT PANEL: Live Agent Terminal */}
          <div className="col-span-4 flex flex-col border border-slate-200 bg-slate-900 rounded-2xl shadow-sm overflow-hidden h-[600px]">
            <div className="bg-slate-800 border-b border-slate-700 px-4 py-3 text-xs flex gap-3 items-center font-medium">
              <span className="text-indigo-400 flex items-center gap-1.5"><Terminal size={14}/> Terminal</span>
              <span className="text-slate-500">VectorDB Logs</span>
            </div>
            <div className="flex-1 text-slate-300 font-mono text-xs overflow-hidden">
               <AgentMonitor logs={logs} />
            </div>
          </div>

          {/* RIGHT PANEL: Outputs */}
          <div className="col-span-8 flex flex-col gap-6">

            {/* EDITABLE SCHEDULE PANEL */}
            <div className="border border-slate-200 bg-white rounded-2xl overflow-hidden flex flex-col shadow-sm h-72">
              <div className="bg-slate-50 border-b border-slate-100 px-4 py-3 text-sm flex justify-between items-center font-semibold text-slate-700">
                <div className="flex items-center gap-2">
                  <Calendar size={16} className="text-indigo-500" /> <span>schedule.json</span>
                </div>
                {status === "AWAITING_APPROVAL" && <span className="text-indigo-500 bg-indigo-50 px-2 py-1 rounded border border-indigo-100 text-xs flex items-center gap-1"><Edit3 size={12} /> Editable</span>}
              </div>

              <textarea
                value={scheduleStr}
                onChange={(e) => setScheduleStr(e.target.value)}
                disabled={status !== "AWAITING_APPROVAL"}
                className="flex-1 p-5 bg-white text-slate-700 text-sm font-mono outline-none resize-none disabled:bg-slate-50 disabled:text-slate-500 focus:ring-inset focus:ring-2 focus:ring-indigo-500/10"
                placeholder="Awaiting Swarm computation..."
                spellCheck={false}
              />
            </div>

            {/* BOTTOM RIGHT: Marketing & Emails (Split) */}
            <div className="grid grid-cols-2 gap-6 flex-1 min-h-[304px]">
              
              <div className="border border-slate-200 bg-white rounded-2xl overflow-hidden flex flex-col shadow-sm">
                <div className="bg-slate-50 border-b border-slate-100 px-4 py-3 text-sm flex items-center gap-2 font-semibold text-slate-700">
                  <Share2 size={16} className="text-purple-500" /> <span>marketing_assets.md</span>
                </div>
                <div className="p-5 overflow-y-auto text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">
                  {marketing ? marketing : <span className="text-slate-400 italic">Awaiting Human Approval to execute Map-Reduce Swarm...</span>}
                </div>
              </div>

              <div className="border border-slate-200 bg-white rounded-2xl overflow-hidden flex flex-col shadow-sm">
                <div className="bg-slate-50 border-b border-slate-100 px-4 py-3 text-sm flex items-center gap-2 font-semibold text-slate-700">
                  <Mail size={16} className="text-emerald-500" /> <span>email_outreach.log</span>
                </div>
                <div className="p-5 overflow-y-auto text-sm">
                  {Array.isArray(emailLogs) && emailLogs.length > 0 ? (
                    emailLogs.map((log, i) => (
                      <div key={i} className="mb-4 border-b border-slate-100 pb-4 last:border-0 last:pb-0 last:mb-0">
                        <span className="text-indigo-600 font-bold text-xs bg-indigo-50 px-2 py-0.5 rounded mr-2">[{log.status || 'DRAFTED'}]</span> 
                        <span className="text-slate-500 text-xs">To:</span> <span className="text-slate-800 font-medium">{log.email || log.recipient || "All Participants"}</span>
                        <span className="text-slate-500 italic mt-2 block bg-slate-50 p-2 rounded-lg border border-slate-100">"{log.preview || log.body || log.subject || "View details..."}"</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-slate-400 italic">No emails drafted yet.</span>
                  )}
                </div>
              </div>

            </div>
            
          </div>
        </div>

        {/* BOTTOM CHAT INPUT (Time Machine Controls) */}
        <div className="border border-slate-200 bg-white rounded-2xl shadow-md mt-auto focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all">
          <form onSubmit={handleChatSubmit} className="flex items-center gap-4 rounded-2xl p-2.5">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="e.g. 'Rewind and change the budget to $20k' or 'Push the keynote back 2 hours...'"
              className="flex-1 bg-transparent border-none outline-none text-slate-800 text-sm px-4 placeholder:text-slate-400"
            />
            <button type="submit" disabled={status === "PLANNING"} className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none flex items-center justify-center">
              <Send size={16} />
            </button>
          </form>
        </div>

      </div>
    </div>
  )
}