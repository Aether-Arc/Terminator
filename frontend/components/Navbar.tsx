import Link from 'next/link'

export default function Navbar() {
  return (
    <div className="w-14 h-full bg-vscode-activityBar flex flex-col items-center py-4 border-r border-vscode-border z-10 shrink-0">
      <div className="text-vscode-blue font-bold text-xl mb-8 tracking-widest" title="EventOS">OS</div>
      <nav className="flex flex-col gap-4 w-full">
        {/* Setup / Input Page */}
        <Link href="/" className="p-3 text-gray-500 hover:text-white flex justify-center hover:bg-vscode-sidebar border-l-2 border-transparent hover:border-vscode-blue transition-all" title="Event Setup (Input)">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        </Link>
        {/* Dashboard */}
        <Link href="/dashboard" className="p-3 text-gray-500 hover:text-white flex justify-center hover:bg-vscode-sidebar border-l-2 border-transparent hover:border-vscode-blue transition-all" title="Swarm Monitor">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
        </Link>
        {/* Agents Graph */}
        <Link href="/agents" className="p-3 text-gray-500 hover:text-white flex justify-center hover:bg-vscode-sidebar border-l-2 border-transparent hover:border-vscode-blue transition-all" title="Agent Network">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" /></svg>
        </Link>
      </nav>
    </div>
  )
}