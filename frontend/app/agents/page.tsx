"use client"
import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { createEvent, approvePlan, simulateCrisis, fetchHistory, forkEvent, fetchThreadState } from '../../lib/api'
import AgentMonitor from '../../components/AgentMonitor'
import MonteCarloChart from '../../components/MonteCarloChart'
import { Play, CheckCircle, AlertTriangle, FastForward, Server, Mail, Calendar, Share2, MessageSquare, History, Send, Plus, Edit3 } from 'lucide-react'

export default function AgentsPage() {
  const router = useRouter()
  const [status, setStatus] = useState<"IDLE" | "PLANNING" | "AWAITING_APPROVAL" | "EXECUTING" | "COMPLETED" | "CRISIS">("IDLE")
  const [logs, setLogs] = useState<any[]>([])
  const [eventData, setEventData] = useState<any>(null)
  const [crisisInput, setCrisisInput] = useState("");

  // 🚀 Advanced State for History & Time Travel
  const [activeThread, setActiveThread] = useState<string | null>(null)
  const [historyThreads, setHistoryThreads] = useState<string[]>([])
  const [chatInput, setChatInput] = useState("")
  const [simMetrics, setSimMetrics] = useState<any>(null)

  // Results State
  const [schedule, setSchedule] = useState<any>(null) // Keeps raw object for reference
  const [scheduleStr, setScheduleStr] = useState<string>("") // 🚀 For the Editable Textarea
  const [marketing, setMarketing] = useState<string>("")
  const [emailLogs, setEmailLogs] = useState<any[]>([])
  const [score, setScore] = useState<number>(0)

  const ws = useRef<WebSocket | null>(null)
  const hasFired = useRef(false);

  useEffect(() => {
    // 1. Fetch History for the Sidebar
    fetchHistory()
      .then(res => setHistoryThreads(res?.threads || []))
      .catch(() => console.log("No history found yet."))

    if (hasFired.current) return;
    hasFired.current = true;

    // 2. Connect to Swarm Live Stream (WebSocket)
    ws.current = new WebSocket("ws://localhost:8000/ws/swarm")
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLogs(prev => [...prev, data])
    }

    // 3. Fetch the payload the user typed in the form
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
    try {
      const result = await createEvent(payload)

      setActiveThread(result.thread_id) // Save the dynamic thread ID
      setSchedule(result.schedule)

      // 🚀 Load the schedule into the editable text area
      setScheduleStr(JSON.stringify(result.schedule, null, 2))
      if (result.stability_score) setScore(result.stability_score)

      if (result.requires_approval) {
        setStatus("AWAITING_APPROVAL")
      } else {
        setStatus("COMPLETED")
      }

      // Refresh sidebar
      fetchHistory().then(res => setHistoryThreads(res?.threads || []))
    } catch (e) {
      console.error(e)
      setStatus("IDLE")
    }
  }

  // 🚀 NEW: Load Full State when clicking a past thread in the sidebar
  const loadPastThread = async (threadId: string) => {
    setActiveThread(threadId)
    setLogs([{ agent: "System", action: `Loaded SQLite memory for ${threadId}...`, status: "success" }])

    try {
      const data = await fetchThreadState(threadId)
      setSchedule(data.schedule)
      setScheduleStr(JSON.stringify(data.schedule, null, 2))
      setMarketing(data.marketing)
      setEmailLogs(data.email_logs || [])
      setStatus(data.status)
    } catch (e) {
      console.error("Failed to load thread", e)
    }
  }

  const handleApprove = async () => {
    setStatus("EXECUTING")
    try {
      // 🚀 Parse the user-edited string from the textarea back into JSON
      const editedScheduleJson = JSON.parse(scheduleStr)

      // Pass the edited plan back to the backend
      const result = await approvePlan({ ...eventData, edited_plan: editedScheduleJson })
      setMarketing(result.marketing)
      setEmailLogs(result.email_outreach_logs || [])
      setStatus("COMPLETED")

      // 🧠 SAVE TO DASHBOARD LOCAL STORAGE
      const finalManifest = {
        event_name: eventData.name,
        schedule: editedScheduleJson, // Save the human-edited version
        marketing: result.marketing,
        email_outreach_logs: result.email_outreach_logs,
        stability_score: score || 95.2,
        agent_outputs: result.agent_outputs || {}
      }
      localStorage.setItem("swarmResult", JSON.stringify(finalManifest))

    } catch (e) {
      alert("Invalid JSON format in schedule! Please fix the brackets/quotes before approving.")
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

      // Update local storage
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

  // 🚀 NEW: TIME TRAVEL CHAT HANDLER
  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatInput || !activeThread) return;

    setStatus("PLANNING")
    setChatInput("") // clear box

    try {
      // Fork the state and rewind time in LangGraph!
      const result = await forkEvent({ thread_id: activeThread, new_prompt: chatInput })

      setSchedule(result.schedule)
      setScheduleStr(JSON.stringify(result.schedule, null, 2))
      if (result.stability_score) setScore(result.stability_score)

      setStatus("AWAITING_APPROVAL") // Wait for user to approve the newly generated plan
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="h-screen flex bg-[#1e1e1e] text-vscode-text font-mono overflow-hidden relative">

      {/* 🚀 LEFT SIDEBAR: ChatGPT Style History */}
      <div className="w-64 border-r border-vscode-border bg-[#181818] flex flex-col z-20">
        <div className="p-4 border-b border-vscode-border">
          <button onClick={() => { localStorage.removeItem("eventPayload"); router.push('/') }} className="w-full flex items-center gap-2 bg-vscode-blue/10 text-vscode-blue border border-vscode-blue/30 px-4 py-2 rounded text-xs hover:bg-vscode-blue hover:text-white transition-all">
            <Plus size={14} /> New Event Swarm
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          <h3 className="text-[10px] text-gray-500 uppercase tracking-widest mb-2 px-2 flex items-center gap-2">
            <History size={10} /> Saved Threads
          </h3>
          {historyThreads.map(thread => (
            <button
              key={thread}
              onClick={() => loadPastThread(thread)}
              className={`w-full text-left px-3 py-2 text-xs rounded mb-1 flex items-center gap-2 truncate ${activeThread === thread ? 'bg-vscode-blue/20 text-vscode-blue' : 'hover:bg-[#2d2d2d] text-gray-400'}`}
            >
              <MessageSquare size={12} /> {thread}
            </button>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL: Main Content */}
      <div className="flex-1 flex flex-col relative p-4">
        <div className="scanline"></div>

        {/* HEADER */}
        <div className="flex justify-between items-center border-b border-vscode-border pb-4 mb-4 z-10">
          <div className="flex items-center gap-3">
            <Server className="text-vscode-blue" size={20} />
            <h1 className="text-lg text-white font-bold tracking-widest uppercase">
              EventOS / {activeThread || "Initializing"}
            </h1>
            <span className={`px-2 py-1 text-[10px] rounded border ${status === 'COMPLETED' ? 'border-vscode-green text-vscode-green' : status === 'CRISIS' ? 'border-red-500 text-red-500' : 'border-vscode-yellow text-vscode-yellow animate-pulse'}`}>
              STATUS: {status}
            </span>
          </div>

          {/* HUMAN IN THE LOOP CONTROLS */}
          <div className="flex gap-4">
            {status === "AWAITING_APPROVAL" && (
              <button onClick={handleApprove} className="flex items-center gap-2 bg-vscode-green/20 text-vscode-green border border-vscode-green px-4 py-2 rounded text-xs hover:bg-vscode-green hover:text-black transition-all shadow-[0_0_15px_rgba(78,201,176,0.3)]">
                <CheckCircle size={14} /> APPROVE SCHEDULE & RESUME
              </button>
            )}
            {status === "COMPLETED" && (
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type custom crisis here..."
                  value={crisisInput}
                  onChange={(e) => setCrisisInput(e.target.value)}
                  className="bg-[#2d2d2d] border border-red-500/50 text-red-400 px-3 py-1 text-xs rounded outline-none focus:border-red-500 w-64"
                />
                <button onClick={handleInjectCrisis} className="flex items-center gap-2 bg-red-500/20 text-red-400 border border-red-500 px-4 py-2 rounded text-xs hover:bg-red-500 hover:text-white transition-all shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                  <AlertTriangle size={14} /> INJECT
                </button>
                <button onClick={() => router.push('/dashboard')} className="flex items-center gap-2 bg-vscode-blue/20 text-vscode-blue border border-vscode-blue px-4 py-2 rounded text-xs hover:bg-vscode-blue hover:text-white transition-all shadow-[0_0_15px_rgba(86,156,214,0.3)]">
                  <FastForward size={14} /> VIEW FINAL MANIFEST
                </button>
              </div>
            )}
          </div>
        </div>

        {/* MAIN DASHBOARD GRID */}
        <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden z-10 mb-4">

          {/* LEFT PANEL: Live Agent Terminal */}
          <div className="col-span-4 flex flex-col border border-vscode-border bg-[#252526] rounded shadow-xl overflow-hidden">
            <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex gap-2">
              <span className="text-vscode-blue">Terminal</span>
              <span className="text-gray-500">VectorDB Logs</span>
            </div>
            <AgentMonitor logs={logs} />
          </div>

          {/* RIGHT PANEL: Outputs */}
          <div className="col-span-8 grid grid-rows-2 gap-4 overflow-hidden">

            {/* 🚀 EDITABLE SCHEDULE PANEL */}
            <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col shadow-xl">
              <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Calendar size={14} className="text-vscode-yellow" /> <span>schedule.json</span>
                </div>
                {status === "AWAITING_APPROVAL" && <span className="text-vscode-blue flex items-center gap-1"><Edit3 size={12} /> Editable</span>}
              </div>

              <textarea
                value={scheduleStr}
                onChange={(e) => setScheduleStr(e.target.value)}
                disabled={status !== "AWAITING_APPROVAL"}
                className="flex-1 p-4 bg-[#1e1e1e] text-vscode-orange text-xs font-mono outline-none resize-none disabled:opacity-70"
                placeholder="Awaiting Swarm..."
              />
            </div>

            {/* BOTTOM RIGHT: Marketing & Emails (Split) */}
            <div className="grid grid-cols-2 gap-4 overflow-hidden">
              <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col shadow-xl">
                <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex items-center gap-2">
                  <Share2 size={14} className="text-vscode-purple" /> <span>marketing_assets.md</span>
                </div>
                <div className="p-4 overflow-y-auto text-xs text-vscode-text whitespace-pre-wrap">
                  {marketing ? marketing : <span className="text-gray-500 italic">Awaiting Human Approval to generate copy...</span>}
                </div>
              </div>

              {/* 🚀 NEW: MONTE CARLO VISUALIZATION PANEL */}
              <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col shadow-xl h-64 mt-4">
                <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex items-center gap-2">
                  <Play size={14} className="text-vscode-blue" /> <span>physics_engine.viz</span>
                </div>
                <div className="flex-1">
                  {/* Pass your simulation data here. For the hackathon demo, you can even mock this array if the real data is too complex to route! */}
                  <MonteCarloChart metrics={simMetrics} />
                </div>
              </div>

              <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col shadow-xl">
                <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex items-center gap-2">
                  <Mail size={14} className="text-vscode-green" /> <span>email_outreach.log</span>
                </div>
                <div className="p-4 overflow-y-auto text-xs">
                  {Array.isArray(emailLogs) && emailLogs.length > 0 ? (
                    emailLogs.map((log, i) => (
                      <div key={i} className="mb-2 border-b border-vscode-border pb-2">
                        <span className="text-vscode-blue">[{log.status || 'SENT'}]</span> To: <span className="text-vscode-orange">{log.email}</span>
                        <br />
                        <span className="text-gray-400">"{log.preview || log.subject}"</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-gray-500 italic">No emails dispatched yet.</span>
                  )}
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* 🚀 BOTTOM CHAT INPUT (Time Machine Controls) */}
        <div className="border border-vscode-border bg-[#181818] rounded-lg z-10 shadow-xl">
          <form onSubmit={handleChatSubmit} className="flex items-center gap-4 bg-[#252526] rounded-lg p-2 focus-within:border-vscode-blue transition-colors">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="e.g. 'Rewind and change the budget to $20k' or 'Add a 30 min coffee break...'"
              className="flex-1 bg-transparent border-none outline-none text-vscode-text text-sm px-2"
            />
            <button type="submit" disabled={status === "PLANNING"} className="bg-vscode-blue/20 text-vscode-blue p-2 rounded hover:bg-vscode-blue hover:text-white transition-all disabled:opacity-50">
              <Send size={16} />
            </button>
          </form>
        </div>

      </div>
    </div>
  )
}