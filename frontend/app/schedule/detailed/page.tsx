"use client"
import Link from 'next/link'
import { ArrowLeft, Clock, MapPin, Users, CheckCircle2, AlertCircle, Info } from 'lucide-react'

export default function DetailedSchedule() {
  // Expanded Mock Data (In production, pull this from your LangGraph state / Context)
  const detailedSchedule = [
    {
      id: 1,
      session: "Ignition Sequence: Welcome Protocol",
      time: "Day 1 | 9:00 AM - 10:30 AM",
      location: "Main Stage Auditorium",
      description: "Opening keynote addressing the crowd, setting the rules, and introducing the sponsor partners.",
      volunteersRequired: 4,
      status: "Locked",
      type: "Keynote"
    },
    {
      id: 2,
      session: "Interactive Lab: Building Autonomous Swarms",
      time: "Day 1 | 10:45 AM - 12:30 PM",
      location: "Workshop Room B",
      description: "Hands-on session where attendees will configure and deploy their first multi-agent local swarm.",
      volunteersRequired: 8,
      status: "Pending AV Setup",
      type: "Interactive"
    },
    {
      id: 3,
      session: "Networking Lunch & Sponsor Expo",
      time: "Day 1 | 12:30 PM - 1:30 PM",
      location: "Grand Courtyard",
      description: "Open networking session. Catering needs to be fully deployed by 12:15 PM.",
      volunteersRequired: 12,
      status: "Locked",
      type: "Break"
    }
  ]

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 pb-20">
      
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center gap-6">
          <Link href="/simulation" className="p-2 bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 rounded-xl text-slate-500 hover:text-indigo-600 transition-all">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight">Detailed Itinerary</h1>
            <p className="text-xs text-slate-500 font-medium">Logistics & Operations Breakdown</p>
          </div>
        </div>
      </header>

      {/* Grid Canvas */}
      <div className="max-w-7xl mx-auto px-6 mt-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {detailedSchedule.map((event) => (
            <div key={event.id} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-xl hover:shadow-indigo-500/10 transition-all group flex flex-col relative overflow-hidden">
              
              {/* Top Badges */}
              <div className="flex justify-between items-start mb-4">
                <span className={`text-[10px] font-extrabold tracking-widest uppercase px-3 py-1 rounded-full border ${
                  event.type === 'Keynote' ? 'bg-rose-50 text-rose-600 border-rose-100' : 
                  event.type === 'Break' ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 
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
              <h3 className="text-lg font-bold leading-tight mb-4 text-slate-800 group-hover:text-indigo-600 transition-colors">
                {event.session}
              </h3>
              
              <div className="space-y-3 mb-6 flex-1">
                <div className="flex items-center gap-3 text-sm text-slate-600 font-medium">
                  <div className="p-1.5 bg-slate-50 rounded-md border border-slate-100"><Clock size={14} className="text-slate-400"/></div>
                  {event.time}
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
      </div>
    </div>
  )
}