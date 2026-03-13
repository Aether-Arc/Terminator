"use client"
import { useState, useEffect } from 'react'
import { Sparkles, Download, LayoutTemplate, ArrowLeft, Layers, Palette } from 'lucide-react'
import Link from 'next/link'
import { fetchThreadState } from '../../../lib/api'

export default function CreativeStudio({ params }: { params: { id: string } }) {
  const [cards, setCards] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      fetchThreadState(params.id)
        .then(data => {
          // Extract the design outputs from the graph state
          const designTask = data.agent_outputs?.design?.[0];
          if (designTask && Array.isArray(designTask.output)) {
            setCards(designTask.output);
          }
        })
        .catch(err => console.error("Could not load designs", err))
        .finally(() => setLoading(false));
    }
  }, [params.id])

  if (loading) {
    return (
      <div className="h-screen bg-slate-50 flex items-center justify-center font-sans">
        <div className="flex flex-col items-center gap-4 text-indigo-500 animate-pulse">
          <Sparkles size={32} />
          <p className="font-semibold text-sm tracking-widest uppercase">Rendering Generative UI...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-indigo-500/30 relative">
      
      {/* Subtle Background Pattern (Matches Landing Page) */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

      {/* Header */}
      <header className="h-20 border-b border-slate-200 flex items-center justify-between px-8 bg-white/80 backdrop-blur-xl sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-6">
          <Link href={`/simulation`} className="text-slate-400 hover:text-indigo-600 transition-colors bg-slate-50 hover:bg-indigo-50 p-2 rounded-xl">
            <ArrowLeft size={20} />
          </Link>
          <div className="flex items-center gap-3">
            <div className="bg-indigo-50 p-2.5 rounded-xl border border-indigo-100">
              <Palette size={20} className="text-indigo-600" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900">Creative Studio</h1>
              <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase">{params.id}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <button className="bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 shadow-sm">
            <LayoutTemplate size={16} className="text-slate-400" /> Edit Templates
          </button>
        </div>
      </header>

      {/* Main Canvas */}
      <div className="max-w-7xl mx-auto p-8 relative z-10 pt-12">
        <div className="mb-10 text-center max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold mb-4 uppercase tracking-widest">
            <Sparkles size={12} /> Autonomous Design
          </div>
          <h2 className="text-4xl font-extrabold mb-4 text-slate-900 tracking-tight">Generated Campaign Assets</h2>
          <p className="text-slate-500 leading-relaxed text-sm">
            Our Web-Enabled DesignAgent researched live trends and synthesized these ready-to-publish social media cards natively in the browser.
          </p>
        </div>

        {cards.length === 0 ? (
          <div className="border-2 border-dashed border-slate-200 bg-white rounded-3xl p-20 flex flex-col items-center justify-center text-center shadow-sm">
            <Layers size={48} className="text-slate-300 mb-4" />
            <h3 className="text-xl font-bold text-slate-700">No designs found</h3>
            <p className="text-slate-500 mt-2 text-sm">Ensure the swarm has completed the execution phase and the Design Agent was selected.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {cards.map((card, idx) => (
              <div 
                key={idx} 
                className={`bg-gradient-to-br ${card.gradient || 'from-indigo-50 to-white'} p-8 rounded-[2rem] text-slate-800 shadow-xl shadow-slate-200/50 relative overflow-hidden group flex flex-col min-h-[420px] hover:-translate-y-2 hover:shadow-2xl hover:shadow-indigo-500/20 transition-all duration-500 border border-white`}
              >
                {/* Dynamic Ambient UI Glow Effect (Light Mode) */}
                <div className="absolute -top-20 -right-20 w-64 h-64 bg-white opacity-60 rounded-full blur-[40px] group-hover:scale-150 transition-transform duration-700 pointer-events-none"></div>

                {/* Badges */}
                <div className="flex justify-between items-start mb-8 relative z-10">
                  <span className="bg-white/60 backdrop-blur-md px-4 py-1.5 rounded-full text-[10px] font-extrabold tracking-widest uppercase border border-white/50 text-indigo-600 shadow-sm">
                    {card.type}
                  </span>
                  <span className="text-slate-400 text-[10px] font-bold uppercase tracking-widest bg-white/40 px-3 py-1 rounded-full">{card.platform}</span>
                </div>
                
                {/* Typography / Copy */}
                <div className="relative z-10 flex-1 flex flex-col justify-center">
                  <h4 className="font-extrabold text-3xl leading-tight mb-3 text-slate-900 tracking-tight">{card.title}</h4>
                  <h5 className="text-sm font-bold text-indigo-600 mb-6 tracking-wide uppercase">{card.subtitle}</h5>
                  <p className="text-sm text-slate-600 leading-relaxed font-medium bg-white/40 backdrop-blur-sm p-5 rounded-2xl border border-white/60 shadow-sm">
                    {card.body}
                  </p>
                </div>

                {/* Export Action */}
                <div className="mt-8 relative z-10">
                   <button className="w-full bg-white hover:bg-indigo-600 text-slate-800 hover:text-white border border-slate-100 px-4 py-3.5 rounded-xl text-sm font-bold transition-all duration-300 shadow-sm flex items-center justify-center gap-2 group-hover:shadow-lg">
                     <Download size={16}/> Export High-Res
                   </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}