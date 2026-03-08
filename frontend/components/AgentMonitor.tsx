export default function AgentMonitor(){

  const agents = [
    "Planner Agent",
    "Scheduler Agent",
    "Marketing Agent",
    "Email Agent",
    "Crisis Agent",
    "Crowd Prediction Agent"
  ]

  return(

    <div className="bg-gray-800 p-4 rounded">

      <h2 className="mb-4 text-lg">
        Agent Activity
      </h2>

      {agents.map((a)=>(
        <div key={a}
          className="border-b border-gray-600 py-2">
          {a} → running
        </div>
      ))}

    </div>
  )
}