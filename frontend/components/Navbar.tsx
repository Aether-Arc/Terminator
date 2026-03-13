"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { PlusSquare, LayoutDashboard, Network } from 'lucide-react'

export default function Navbar() {
  const pathname = usePathname()

  // Helper to determine if a route is active
  const isActive = (path: string) => {
    if (path === '/' && pathname !== '/') return false;
    return pathname?.startsWith(path);
  }

  return (
    <div className="w-16 h-full bg-white flex flex-col items-center py-6 border-r border-slate-200 z-50 shrink-0 shadow-sm">
      
      {/* LOGO */}
      <div className="text-indigo-600 font-extrabold text-2xl mb-10 tracking-tighter" title="EventOS">
        OS
      </div>
      
      <nav className="flex flex-col gap-3 w-full px-2">
        
        {/* Setup / Home Page */}
        <Link 
          href="/" 
          className={`p-3 rounded-xl flex justify-center transition-all group ${
            isActive('/') 
              ? 'bg-indigo-50 text-indigo-600 shadow-sm border border-indigo-100' 
              : 'text-slate-400 hover:text-indigo-600 hover:bg-slate-50 border border-transparent'
          }`}
          title="New Event"
        >
          <PlusSquare size={22} className={`${isActive('/') ? '' : 'group-hover:scale-110'} transition-transform duration-200`} />
        </Link>
        
        {/* Dashboard / Outputs */}
        <Link 
          href="/dashboard" 
          className={`p-3 rounded-xl flex justify-center transition-all group ${
            isActive('/dashboard') 
              ? 'bg-indigo-50 text-indigo-600 shadow-sm border border-indigo-100' 
              : 'text-slate-400 hover:text-indigo-600 hover:bg-slate-50 border border-transparent'
          }`}
          title="Event Dashboards"
        >
          <LayoutDashboard size={22} className={`${isActive('/dashboard') ? '' : 'group-hover:scale-110'} transition-transform duration-200`} />
        </Link>
        
        {/* Live Agents View */}
        <Link 
          href="/agents" 
          className={`p-3 rounded-xl flex justify-center transition-all group ${
            isActive('/agents') 
              ? 'bg-indigo-50 text-indigo-600 shadow-sm border border-indigo-100' 
              : 'text-slate-400 hover:text-indigo-600 hover:bg-slate-50 border border-transparent'
          }`}
          title="Swarm Monitor"
        >
          <Network size={22} className={`${isActive('/agents') ? '' : 'group-hover:scale-110'} transition-transform duration-200`} />
        </Link>

      </nav>
    </div>
  )
}