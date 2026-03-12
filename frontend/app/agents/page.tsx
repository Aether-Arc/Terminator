"use client"
import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { createEvent, approvePlan, simulateCrisis } from '../../lib/api'
import AgentMonitor from '../../components/AgentMonitor'
import { Play, CheckCircle, AlertTriangle, FastForward, Server, Mail, Calendar, Share2 } from 'lucide-react'

export default function AgentsPage() {
  const router = useRouter()
  const [status, setStatus] = useState<"IDLE" | "PLANNING" | "AWAITING_APPROVAL" | "EXECUTING" | "COMPLETED" | "CRISIS">("IDLE")
  const [logs, setLogs] = useState<any[]>([])
  const [eventData, setEventData] = useState<any>(null)
  const [crisisInput, setCrisisInput] = useState("");
  
  // Results State
  const [schedule, setSchedule] = useState<any>(null)
  const [marketing, setMarketing] = useState<string>("")
  const [emailLogs, setEmailLogs] = useState<any[]>([])
  const [score, setScore] = useState<number>(0)
  
  const ws = useRef<WebSocket | null>(null)

  const hasFired = useRef(false);

  useEffect(() => {
    if (hasFired.current) return; // 2. If already fired, stop here!
    hasFired.current = true;      // 3. Mark as fired
    // 1. Connect to Swarm Live Stream (WebSocket)
    ws.current = new WebSocket("ws://localhost:8000/ws/swarm")
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLogs(prev => [...prev, data])
    }

    // 2. Fetch the payload the user typed in the form
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
      setSchedule(result.schedule)
      if (result.stability_score) setScore(result.stability_score)
      
      if (result.requires_approval) {
        setStatus("AWAITING_APPROVAL")
      } else {
        setStatus("COMPLETED")
      }
    } catch (e) {
      console.error(e)
      setStatus("IDLE")
    }
  }

  const handleApprove = async () => {
    setStatus("EXECUTING")
    try {
      // Pass the schedule and original payload back to the backend
      const result = await approvePlan({ ...eventData, schedule })
      setMarketing(result.marketing)
      setEmailLogs(result.email_outreach_logs)
      setStatus("COMPLETED")
      
      // 🧠 SAVE TO DASHBOARD LOCAL STORAGE
      const finalManifest = {
        event_name: eventData.name,
        schedule: schedule,
        marketing: result.marketing,
        email_outreach_logs: result.email_outreach_logs,
        stability_score: score || 95.2,
        agent_outputs: result.agent_outputs || {} // New Modular Outputs
      }
      localStorage.setItem("swarmResult", JSON.stringify(finalManifest))
      
    } catch (e) {
      console.error(e)
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
      
      // Update UI with the crisis fixes!
      setSchedule(result.new_schedule)
      let newEmails = emailLogs;
      if (result.emergency_emails_sent) {
        newEmails = [...emailLogs, ...result.emergency_emails_sent]
        setEmailLogs(newEmails)
      }
      setStatus("COMPLETED")
      
      // 🧠 UPDATE DASHBOARD DATA WITH CRISIS RESOLUTION
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

  return (
    <div className="h-screen flex flex-col p-4 bg-[#1e1e1e] text-vscode-text font-mono overflow-hidden relative">
      <div className="scanline"></div>
      
      {/* HEADER */}
      <div className="flex justify-between items-center border-b border-vscode-border pb-4 mb-4 z-10">
        <div className="flex items-center gap-3">
          <Server className="text-vscode-blue" size={20} />
          <h1 className="text-lg text-white font-bold tracking-widest uppercase">EventOS / Swarm Control</h1>
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
      <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden z-10">
        
        {/* LEFT PANEL: Live Agent Terminal */}
        <div className="col-span-4 flex flex-col border border-vscode-border bg-[#252526] rounded shadow-xl overflow-hidden">
          <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex gap-2">
            <span className="text-vscode-blue">Terminal</span>
            <span className="text-gray-500">VectorDB Logs</span>
          </div>
          <AgentMonitor logs={logs} />
        </div>

        {/* RIGHT PANEL: Outputs (Schedule, Marketing, Emails) */}
        <div className="col-span-8 grid grid-rows-2 gap-4 overflow-hidden">
          
          {/* TOP RIGHT: Schedule / Timelines */}
          <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col">
            <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex items-center gap-2">
              <Calendar size={14} className="text-vscode-yellow" /> <span>schedule.json</span>
            </div>
            <div className="p-4 overflow-y-auto text-xs whitespace-pre-wrap text-vscode-orange">
              {schedule ? JSON.stringify(schedule, null, 2) : <span className="text-gray-500 italic">Waiting for Planner & Scheduler Agents...</span>}
            </div>
          </div>

          {/* BOTTOM RIGHT: Marketing & Emails (Split) */}
          <div className="grid grid-cols-2 gap-4 overflow-hidden">
            
            {/* Marketing View */}
            <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col">
              <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex items-center gap-2">
                <Share2 size={14} className="text-vscode-purple" /> <span>marketing_assets.md</span>
              </div>
              <div className="p-4 overflow-y-auto text-xs text-vscode-text">
                {marketing ? marketing : <span className="text-gray-500 italic">Awaiting Human Approval to generate copy...</span>}
              </div>
            </div>

            {/* Email Logs View */}
            <div className="border border-vscode-border bg-[#252526] rounded overflow-hidden flex flex-col">
              <div className="bg-[#1e1e1e] border-b border-vscode-border p-2 text-xs flex items-center gap-2">
                <Mail size={14} className="text-vscode-green" /> <span>email_outreach.log</span>
              </div>
              <div className="p-4 overflow-y-auto text-xs">
                {emailLogs.length > 0 ? (
                  emailLogs.map((log, i) => (
                    <div key={i} className="mb-2 border-b border-vscode-border pb-2">
                      <span className="text-vscode-blue">[{log.status}]</span> To: <span className="text-vscode-orange">{log.email}</span>
                      <br />
                      <span className="text-gray-400">"{log.preview}"</span>
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
    </div>
  )
}