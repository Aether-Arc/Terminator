import Link from "next/link"

export default function Navbar() {

  return (

    <div className="flex justify-between bg-black p-4">

      <h1 className="text-xl font-bold">
        SkyNet
      </h1>

      <div className="flex gap-6">

        <Link href="/dashboard">Dashboard</Link>
        <Link href="/agents">Agents</Link>
        <Link href="/simulation">Simulation</Link>
        <Link href="/analytics">Analytics</Link>

      </div>

    </div>
  )
}