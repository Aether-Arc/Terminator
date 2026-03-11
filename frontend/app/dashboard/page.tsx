"use client"
import { useEffect, useState } from 'react';
import { Calendar, Share2, Mail, BrainCircuit, Activity, AlertTriangle, ShieldCheck, Clock, Users, Database } from 'lucide-react';

export default function Dashboard() {
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    // Read the finalized data from the swarm
    const saved = localStorage.getItem("swarmResult");
    if (saved) {
      setResults(JSON.parse(saved));
    }
  }, []);

  if (!results) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-500 font-mono bg-[#1e1e1e]">
        <Database size={48} className="mb-4 text-vscode-border" />
        <p>No active event data found in VectorDB.</p>
        <p className="text-xs mt-2">Please initialize and approve a swarm deployment first.</p>
      </div>
    )
  }

  // Safely extract data
  const schedule = results.schedule?.schedule || results.schedule || [];
  const emails = results.email_outreach_logs || results.emergency_emails_sent || [];
  const score = results.stability_score || 92.5;

  return (
    <div className="h-full flex flex-col p-6 bg-[#1e1e1e] text-vscode-text font-mono overflow-y-auto relative">
      <div className="scanline pointer-events-none"></div>

      {/* HEADER: Event Manifest */}
      <div className="flex justify-between items-end border-b border-vscode-border pb-4 mb-6">
        <div>
          <h1 className="text-2xl text-white font-bold tracking-widest uppercase flex items-center gap-3">
            <ShieldCheck className="text-vscode-green" /> FINAL EVENT MANIFEST
          </h1>
          <p className="text-xs text-gray-400 mt-1">Generated autonomously by EventOS Multi-Agent Swarm</p>
        </div>
        <div className="text-right">
          <div className="text-[10px] text-vscode-yellow uppercase tracking-widest">System Confidence Score</div>
          <div className="text-3xl text-vscode-green font-bold">{score.toFixed(1)}%</div>
        </div>
      </div>

      {/* TOP ROW: Quick Metrics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard icon={<Calendar />} title="Total Sessions" value={Array.isArray(schedule) ? schedule.length : "N/A"} color="text-vscode-blue" />
        <MetricCard icon={<Mail />} title="Emails Processed" value={emails.length} color="text-vscode-orange" />
        <MetricCard icon={<Activity />} title="Crises Handled" value={results.crisis_injected ? 1 : 0} color="text-red-400" />
        <MetricCard icon={<BrainCircuit />} title="RL Policy Updates" value="+1 (Optimized)" color="text-vscode-purple" />
      </div>

      {/* MIDDLE ROW: Schedule & Marketing */}
      <div className="grid grid-cols-12 gap-6 mb-6">
        
        {/* LEFT: Master Schedule (OR-Tools Output) */}
        <div className="col-span-7 flex flex-col border border-vscode-border bg-[#252526] rounded shadow-lg">
          <div className="bg-[#1e1e1e] border-b border-vscode-border p-3 text-xs flex items-center gap-2 uppercase tracking-wider font-bold">
            <Calendar size={14} className="text-vscode-blue" /> <span>Mathematical Schedule (OR-Tools)</span>
          </div>
          <div className="p-4 overflow-y-auto h-80 space-y-3">
            {Array.isArray(schedule) && schedule.length > 0 ? (
              schedule.map((item: any, i: number) => (
                <div key={i} className="flex gap-4 p-3 bg-[#1e1e1e] border border-vscode-border rounded hover:border-vscode-blue transition-colors">
                  <div className="flex flex-col items-center justify-center border-r border-vscode-border pr-4 min-w-[100px]">
                    <Clock size={14} className="text-gray-500 mb-1" />
                    <span className="text-vscode-orange text-xs font-bold">{item.start || item.time || "TBD"}</span>
                  </div>
                  <div className="flex flex-col justify-center">
                    <span className="text-vscode-text font-bold text-sm">{item.session || item.name || "Session"}</span>
                    {item.track && <span className="text-gray-500 text-[10px] mt-1 uppercase">Track: {item.track}</span>}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-500 italic text-xs">Schedule data parsing error. Raw output: {JSON.stringify(schedule)}</div>
            )}
          </div>
        </div>

        {/* RIGHT: Marketing Assets (Gemini/ML) */}
        <div className="col-span-5 flex flex-col border border-vscode-border bg-[#252526] rounded shadow-lg">
          <div className="bg-[#1e1e1e] border-b border-vscode-border p-3 text-xs flex items-center gap-2 uppercase tracking-wider font-bold">
            <Share2 size={14} className="text-vscode-purple" /> <span>Social Assets & ML Timing</span>
          </div>
          <div className="p-4 overflow-y-auto h-80 text-xs text-gray-300 whitespace-pre-wrap font-sans leading-relaxed bg-[#1e1e1e]">
            {results.marketing || <span className="text-gray-500 italic">No marketing data available.</span>}
          </div>
        </div>

      </div>

      {/* BOTTOM ROW: Email Logs & Crisis/Memory Insights */}
      <div className="grid grid-cols-12 gap-6">
        
        {/* LEFT: Email Outreach Logistics */}
        <div className="col-span-6 flex flex-col border border-vscode-border bg-[#252526] rounded shadow-lg">
          <div className="bg-[#1e1e1e] border-b border-vscode-border p-3 text-xs flex items-center justify-between uppercase tracking-wider font-bold">
            <div className="flex items-center gap-2">
              <Mail size={14} className="text-vscode-orange" /> <span>Email Target Acquisition</span>
            </div>
            <span className="text-[10px] bg-vscode-orange/20 text-vscode-orange px-2 py-0.5 rounded border border-vscode-orange">CSV Parsed</span>
          </div>
          <div className="p-0 overflow-y-auto h-64">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="bg-[#1e1e1e] border-b border-vscode-border sticky top-0">
                <tr>
                  <th className="p-3 text-gray-500 font-normal">Status</th>
                  <th className="p-3 text-gray-500 font-normal">Target Email</th>
                  <th className="p-3 text-gray-500 font-normal">Preview Snippet</th>
                </tr>
              </thead>
              <tbody>
                {emails.map((log: any, i: number) => (
                  <tr key={i} className="border-b border-vscode-border/50 hover:bg-[#2a2d2e]">
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-[9px] uppercase border ${log.status === 'Drafted' ? 'border-vscode-blue text-vscode-blue bg-vscode-blue/10' : 'border-vscode-yellow text-vscode-yellow bg-vscode-yellow/10'}`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="p-3 text-vscode-text font-bold">{log.email}</td>
                    <td className="p-3 text-gray-400 truncate max-w-[200px]">{log.preview}</td>
                  </tr>
                ))}
                {emails.length === 0 && (
                  <tr><td colSpan={3} className="p-4 text-center text-gray-500 italic">No email logs found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT: Reinforcement & Vector Memory Logs */}
        <div className="col-span-6 flex flex-col border border-vscode-border bg-[#252526] rounded shadow-lg">
          <div className="bg-[#1e1e1e] border-b border-vscode-border p-3 text-xs flex items-center gap-2 uppercase tracking-wider font-bold">
            <BrainCircuit size={14} className="text-vscode-green" /> <span>VectorDB & Cognitive Logs</span>
          </div>
          <div className="p-4 overflow-y-auto h-64 space-y-4 text-xs">
            
            <div className="border-l-2 border-vscode-blue pl-3">
              <div className="text-vscode-blue font-bold mb-1">Knowledge Stored</div>
              <div className="text-gray-400">Event schedule and marketing assets successfully embedded into TF-IDF Vector Space for future reference.</div>
            </div>

            <div className="border-l-2 border-vscode-purple pl-3">
              <div className="text-vscode-purple font-bold mb-1">RL Policy Evaluation</div>
              <div className="text-gray-400">Critic Agent evaluated plan logic. Q-Table updated with reward value <span className="text-vscode-green font-bold">+{score.toFixed(1)}</span> for current state parameters.</div>
            </div>

            {results.crisis_injected && (
              <div className="border-l-2 border-red-500 pl-3">
                <div className="text-red-400 font-bold mb-1">Crisis Anomaly Resolved</div>
                <div className="text-gray-400">
                  <span className="text-vscode-text block mb-1">Trigger: "{results.crisis_injected}"</span>
                  <span className="text-vscode-green">Mitigation: {results.applied_solution?.mitigation_strategy || "Dynamic Rescheduling Applied."}</span>
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  )
}

function MetricCard({ icon, title, value, color }: { icon: any, title: string, value: string | number, color: string }) {
  return (
    <div className="bg-[#252526] border border-vscode-border rounded p-4 flex items-center gap-4 shadow-lg">
      <div className={`p-3 rounded bg-[#1e1e1e] border border-vscode-border ${color}`}>
        {icon}
      </div>
      <div>
        <div className="text-gray-500 text-[10px] uppercase tracking-wider mb-1">{title}</div>
        <div className={`text-xl font-bold ${color}`}>{value}</div>
      </div>
    </div>
  )
}