"use client"
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Clock, MapPin, Users, CheckCircle2, AlertCircle, Info, History, Sparkles, RefreshCw } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export default function DetailedSchedule() {
  const [history, setHistory] = useState<string[]>([]);
  const [currentThread, setCurrentThread] = useState<string | null>(null);
  const [detailedSchedule, setDetailedSchedule] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [missingDetails, setMissingDetails] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/history`);
      if (res.ok) {
        const data = await res.json();
        const fetchedThreads = data.threads || []; 
        setHistory(fetchedThreads);
        if (data.history && data.history.length > 0) {
          selectThread(data.history[0]); // Auto-load most recent
        } else {
          setLoading(false);
        }
      }
    } catch (e) {
      console.error("Failed to load history", e);
      setLoading(false);
    }
  }

  const selectThread = async (threadId: string) => {
    setCurrentThread(threadId);
    setLoading(true);
    setMissingDetails(false);

    try {
      const res = await fetch(`${API_URL}/thread/${encodeURIComponent(threadId)}`);
      if (res.ok) {
        const data = await res.json();
        
        // Look for the itinerary payload in the Operations array
        const ops = data.agent_outputs?.operations || [];
        const itineraryTask = ops.find((w: any) => w.domain === "itinerary");
        
        if (itineraryTask && Array.isArray(itineraryTask.output)) {
          setDetailedSchedule(itineraryTask.output);
        } else if (data.schedule && data.schedule.length > 0) {
          // FALLBACK: Base schedule exists, but detailed agent hasn't run yet
          setMissingDetails(true);
          const fallback = data.schedule.map((s: any, idx: number) => ({
             id: idx, session: s.session, time: s.time, location: "TBD", description: "Awaiting detailed generation.", volunteersRequired: 0, status: "Pending", type: "General"
          }));
          setDetailedSchedule(fallback);
        } else {
          setDetailedSchedule([]);
        }
      }
    } catch (e) {
      console.error("Failed to fetch thread state", e);
    }
    setLoading(false);
  }

  const handleGenerate = async () => {
    if (!currentThread) return;
    setLoading(true);
    try {
      // 🚀 Point directly to the new, specialized endpoint
      await fetch(`${API_URL}/api/generate_itinerary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ thread_id: currentThread })
      });
      
      // Reload instantly without the 4-second timeout delay
      selectThread(currentThread); 
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900">
      
      {/* LEFT SIDEBAR: History */}
      <div className="w-72 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 shadow-sm z-20">
        <div className="p-6 border-b border-slate-100 flex items-center gap-3">
          <History className="text-indigo-500" size={20} />
          <h2 className="font-bold text-slate-800 tracking-tight">Memory Archive</h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
           {history.map(th => (
             <button 
                key={th} 
                onClick={() => selectThread(th)} 
                className={`text-left text-sm p-3.5 rounded-xl transition-all duration-200 border ${
                  currentThread === th 
                    ? 'bg-indigo-50 text-indigo-700 font-bold border-indigo-200 shadow-sm' 
                    : 'text-slate-600 hover:bg-slate-50 border-transparent hover:border-slate-200'
                }`}
             >
               {th}
             </button>
           ))}
        </div>
      </div>

      {/* MAIN CANVAS */}
      <div className="flex-1 flex flex-col h-screen overflow-y-auto pb-20 relative">
        
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-10 h-24 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/simulation" className="p-2.5 bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 rounded-xl text-slate-500 hover:text-indigo-600 transition-all">
                <ArrowLeft size={20} />
              </Link>
              <div>
                <h1 className="text-2xl font-extrabold tracking-tight">Detailed Itinerary</h1>
                <p className="text-sm text-slate-500 font-medium flex items-center gap-2 mt-0.5">
                   <Sparkles size={14} className="text-amber-500" /> Logistics & Operations Breakdown
                </p>
              </div>
            </div>
            
            {/* Generate Button (Only shows if details are missing) */}
            {missingDetails && (
               <button onClick={handleGenerate} className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-indigo-600/20">
                 <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                 Generate Missing Details
               </button>
            )}
          </div>
        </header>

        {/* Content */}
        <div className="max-w-6xl mx-auto px-10 mt-10 w-full">
          {loading ? (
            <div className="flex items-center justify-center h-64 text-indigo-500 animate-pulse font-bold tracking-widest uppercase text-sm">
              Syncing Swarm Data...
            </div>
          ) : detailedSchedule.length === 0 ? (
             <div className="border-2 border-dashed border-slate-200 rounded-3xl p-20 flex flex-col items-center justify-center text-center">
               <AlertCircle size={48} className="text-slate-300 mb-4" />
               <h3 className="text-xl font-bold text-slate-700">No schedule found</h3>
               <p className="text-slate-500 mt-2 text-sm max-w-sm">Select a different conversation from the history sidebar or run a new event planner simulation.</p>
             </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {detailedSchedule.map((event, idx) => (
                <div key={event.id || idx} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-xl hover:shadow-indigo-500/10 transition-all duration-300 group flex flex-col">
                  
                  {/* Top Badges */}
                  <div className="flex justify-between items-start mb-5">
                    <span className={`text-[10px] font-extrabold tracking-widest uppercase px-3 py-1 rounded-full border ${
                      event.type === 'Keynote' ? 'bg-rose-50 text-rose-600 border-rose-100' : 
                      event.type === 'Break' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 
                      event.type === 'General' ? 'bg-slate-100 text-slate-600 border-slate-200' :
                      'bg-indigo-50 text-indigo-600 border-indigo-100'
                    }`}>
                      {event.type}
                    </span>
                    
                    {event.status === "Locked" ? (
                      <CheckCircle2 size={18} className="text-emerald-500" />
                    ) : (
                      <AlertCircle size={18} className="text-amber-500" />
                    )}
                  </div>

                  {/* Core Info */}
                  <h3 className="text-lg font-bold leading-tight mb-5 text-slate-800 group-hover:text-indigo-600 transition-colors">
                    {event.session}
                  </h3>
                  
                  <div className="space-y-3.5 mb-6 flex-1">
                    <div className="flex items-center gap-3 text-sm text-slate-600 font-medium">
                      <div className="p-1.5 bg-slate-50 rounded-md border border-slate-100"><Clock size={14} className="text-slate-400"/></div>
                      <span className="bg-slate-50 px-2 py-0.5 rounded text-slate-700 border border-slate-100">{event.time}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-600 font-medium">
                      <div className="p-1.5 bg-slate-50 rounded-md border border-slate-100"><MapPin size={14} className="text-slate-400"/></div>
                      {event.location}
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-600 font-medium">
                      <div className="p-1.5 bg-slate-50 rounded-md border border-slate-100"><Users size={14} className="text-slate-400"/></div>
                      {event.volunteersRequired} Volunteers Required
                    </div>
                  </div>

                  {/* Description Block */}
                  <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-sm text-slate-600 leading-relaxed font-medium flex gap-3">
                    <Info size={16} className="text-indigo-400 shrink-0 mt-0.5" />
                    <p>{event.description}</p>
                  </div>

                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}