"use client"
import Link from 'next/link'
import { CalendarRange, ArrowRight } from 'lucide-react'

// 🚀 Now accepts schedule and threadId as props
export default function ScheduleView({ schedule = [], threadId = "latest" }: { schedule?: any[], threadId?: string }) {
  
  // Fallback so it doesn't crash while loading
  const displaySchedule = schedule.length > 0 ? schedule : [
    { session: "Generating Timeline...", time: "..." }
  ]

  return (
    <div className="bg-white border border-slate-200 p-6 rounded-3xl shadow-sm font-sans w-full relative z-10">
      <div className="flex items-center gap-3 mb-5">
        <div className="bg-indigo-50 p-2 rounded-lg border border-indigo-100">
          <CalendarRange className="text-indigo-600" size={20} />
        </div>
        <h2 className="text-lg font-bold text-slate-800 tracking-tight">Event Schedule</h2>
      </div>

      <div className="flex flex-col gap-1 mb-6 max-h-[300px] overflow-y-auto pr-2">
        {displaySchedule.map((s, idx) => (
          <div key={idx} className="flex justify-between items-center border-b border-slate-100 py-3 last:border-0 hover:bg-slate-50 px-2 rounded-lg transition-colors">
            <span className="font-semibold text-slate-700 text-sm truncate pr-4">{s.session}</span>
            <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100 whitespace-nowrap">
              {s.time}
            </span>
          </div>
        ))}
      </div>

      <div className="pt-4 border-t border-slate-100 mt-auto">
        {/* 🚀 Dynamic Link Button */}
        <Link href={`/schedule/detailed/${threadId}`} className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/20 px-4 py-3.5 rounded-xl text-sm font-bold transition-all duration-300 group">
          View Detailed Itinerary 
          <ArrowRight size={16} className="text-indigo-200 group-hover:text-white transition-colors group-hover:translate-x-1" />
        </Link>
      </div>
    </div>
  )
}