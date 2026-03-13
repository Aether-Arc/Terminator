import EventForm from '../components/EventForm'

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col p-4 relative font-sans text-slate-800">
      
      {/* Subtle Background Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      
      <div className="relative z-10 flex flex-col items-center justify-center mt-12 mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold mb-6">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          Swarm Engine Online
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight text-center">
          Event<span className="text-indigo-600">OS</span>
        </h1>
        <p className="text-slate-500 text-sm md:text-base mt-3 max-w-xl text-center leading-relaxed">
          Brief your AI Swarm. Our autonomous agents will research, budget, schedule, and draft assets for your next event in seconds.
        </p>
      </div>
      
      <div className="relative z-10 pb-12">
        <EventForm />
      </div>
    </div>
  )
}