import Link from "next/link"

export default function Home() {

  return (

    <div className="flex flex-col items-center justify-center h-screen gap-6">

      <h1 className="text-4xl font-bold">
        SkyNet – AI Event Operating System
      </h1>

      <Link
        href="/dashboard"
        className="bg-blue-600 px-6 py-3 rounded"
      >
        Open Dashboard
      </Link>

    </div>

  )
}