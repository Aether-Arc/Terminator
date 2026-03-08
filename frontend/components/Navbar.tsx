import Link from 'next/link'

export default function Navbar() {
  return (
    <div className="w-14 h-full bg-vscode-activityBar flex flex-col items-center py-4 border-r border-vscode-border z-10">
      <div className="text-vscode-blue font-bold text-xl mb-8 tracking-widest">OS</div>
      <nav className="flex flex-col gap-4 w-full">
        <Link href="/dashboard" className="p-3 text-gray-500 hover:text-white flex justify-center hover:bg-vscode-sidebar border-l-2 border-transparent hover:border-vscode-blue transition-all" title="Explorer">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
        </Link>
        <Link href="/agents" className="p-3 text-gray-500 hover:text-white flex justify-center hover:bg-vscode-sidebar border-l-2 border-transparent hover:border-vscode-blue transition-all" title="Agent Source Control">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" /></svg>
        </Link>
        <Link href="/simulation" className="p-3 text-gray-500 hover:text-white flex justify-center hover:bg-vscode-sidebar border-l-2 border-transparent hover:border-vscode-blue transition-all" title="Debug/Simulation">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </Link>
      </nav>
    </div>
  )
}