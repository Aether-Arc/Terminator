"use client"
import { useState, useEffect } from 'react'
import { Download, Share2, Layers, Sparkles, Image as ImageIcon, History, MessageSquare, Plus, PanelLeftClose, PanelLeftOpen, AlertTriangle } from 'lucide-react'
import Link from 'next/link'
import Navbar from '../../../components/Navbar'
import { fetchHistory, fetchThreadState } from '../../../lib/api'

export default function Studio({ params }: { params: { id: string } }) {
  const [designs, setDesigns] = useState<any[]>([])
  const [agentErrors, setAgentErrors] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  
  // Sidebar State
  const [threads, setThreads] = useState<any[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    // 1. Fetch History for Sidebar
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

    // 2. Fetch Designs for the Main Canvas
    if (params.id) {
      fetchThreadState(params.id)
        .then(data => {
          const agentOutputs = data.agent_outputs || {};
          const designArray = agentOutputs.design || [];
          
          let extractedCards: any[] = [];
          let detectedErrors: string[] = [];
          
          // 🚀 AGGRESSIVE PARSER: Catch edge-case JSON formats and errors
          designArray.forEach((taskObj: any) => {
            let out = taskObj.output;
            
            if (!out) return;

            // Handle stringified JSON
            if (typeof out === 'string') {
              try { out = JSON.parse(out); } catch(e) {}
            }
            
            // Handle if the LLM nested it inside a "cards" key
            if (out && typeof out === 'object' && out.cards) {
              out = out.cards;
            }

            // Check if it's an error from Python
            if (out && (out.status === 'ERROR' || out.error)) {
              detectedErrors.push(out.error || JSON.stringify(out));
            } 
            // Check if it's an array of cards
            else if (Array.isArray(out)) {
              extractedCards = [...extractedCards, ...out];
            } 
            // Fallback: if it's just a single object card
            else if (out && typeof out === 'object' && (out.title || out.type)) {
              extractedCards.push(out);
            }
          });
          
          setDesigns(extractedCards);
          setAgentErrors(detectedErrors);
          setLoading(false);
        })
        .catch(err => {
          console.error("Could not load designs", err);
          setLoading(false);
        });
    }
  }, [params.id])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center">
        <Sparkles className="text-indigo-500 animate-pulse mb-4" size={32} />
        <p className="text-slate-500 font-medium">Fetching Generative UI components...</p>
      </div>
    )
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
            <Link key={t.id} href={`/studio/${t.id}`}>
              <div className={`px-3 py-2.5 rounded-xl text-sm flex items-center gap-3 cursor-pointer truncate transition-all ${t.id === params.id ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-slate-600 hover:bg-slate-50'}`}>
                <Layers size={14} className={t.id === params.id ? 'text-indigo-500' : 'text-slate-400'} />
                <span className="truncate">{t.title}</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* COLUMN 2: Main Studio Canvas */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
       
        
        {/* Toggle Sidebar Button */}
        <div className="absolute top-[80px] left-6 z-30">
           <button onClick={() => setSidebarOpen(!sidebarOpen)} className="bg-white border border-slate-200 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors p-2 rounded-lg shadow-sm">
             {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
           </button>
        </div>

        <main className="flex-1 overflow-y-auto p-8 pt-12 md:px-16">
          <div className="mb-10 pl-10 md:pl-0">
            <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
              <Layers className="text-indigo-600" /> Generative Design Studio
            </h1>
            <p className="text-slate-500 mt-2 text-sm max-w-2xl">
              Our Web-Enabled DesignAgent researched live trends and synthesized these ready-to-publish social media cards natively in the browser.
            </p>
          </div>

          {/* 🚀 DEBUG MONITOR: Shows Python crashes if they occurred */}
          {agentErrors.length > 0 && (
            <div className="mb-8 bg-red-50 border border-red-200 rounded-2xl p-6">
              <h3 className="text-red-700 font-bold flex items-center gap-2 mb-2">
                <AlertTriangle size={18} /> DesignAgent Encountered an Error
              </h3>
              <ul className="list-disc pl-5 text-red-600 text-sm space-y-1 font-mono">
                {agentErrors.map((err, idx) => <li key={idx}>{err}</li>)}
              </ul>
            </div>
          )}

          {designs.length === 0 && agentErrors.length === 0 ? (
            <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-16 flex flex-col items-center justify-center text-center mt-10">
              <ImageIcon size={48} className="text-slate-300 mb-4" />
              <h3 className="text-lg font-bold text-slate-700">No designs found in this Thread</h3>
              <p className="text-slate-500 text-sm max-w-sm mt-2">
                If this is an old event, try generating a <b>Brand New Event</b> so the updated DesignAgent can run!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-20">
              {designs.map((card, i) => (
                <div key={i} className={`relative rounded-[2rem] p-8 aspect-square flex flex-col justify-between shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 bg-gradient-to-br ${card.gradient || 'from-slate-100 to-slate-200'} overflow-hidden group`}>
                  
                  {/* Visual Glass Effect */}
                  <div className="absolute top-0 right-0 w-64 h-64 bg-white/20 blur-3xl rounded-full -translate-y-1/2 translate-x-1/3"></div>
                  
                  <div className="relative z-10 flex justify-between items-start">
                    <span className="bg-white/60 backdrop-blur-md text-slate-800 text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider shadow-sm">
                      {card.platform || 'Social'}
                    </span>
                    <span className="bg-white/40 text-slate-600 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-widest border border-white/50">
                      {card.type || 'Promo'}
                    </span>
                  </div>
                  
                  <div className="relative z-10 mt-auto">
                    <h2 className="text-3xl font-black text-slate-800 tracking-tight leading-none mb-3 drop-shadow-sm">
                      {card.title || 'Event Highlight'}
                    </h2>
                    {card.subtitle && (
                      <h3 className="text-lg font-semibold text-indigo-600 mb-4 tracking-tight">
                        {card.subtitle}
                      </h3>
                    )}
                    <p className="text-sm font-medium text-slate-700 leading-relaxed max-w-[90%] backdrop-blur-sm bg-white/30 p-3 rounded-xl border border-white/40 shadow-sm">
                      {card.body || 'No description provided.'}
                    </p>
                  </div>

                  <div className="absolute inset-x-0 bottom-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity flex justify-end gap-2 bg-gradient-to-t from-black/10 to-transparent">
                    <button className="bg-white text-slate-700 p-2 rounded-full hover:bg-slate-100 shadow-sm">
                      <Share2 size={16} />
                    </button>
                    <button className="bg-slate-800 text-white p-2 rounded-full hover:bg-slate-700 shadow-sm">
                      <Download size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}