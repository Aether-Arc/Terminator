"use client"

import { ForceGraph2D } from "react-force-graph"

export default function AgentGraph() {

  const data = {
    nodes: [
      { id: "Orchestrator" },
      { id: "Planner" },
      { id: "Scheduler" },
      { id: "Marketing" },
      { id: "Email" },
      { id: "Crisis" }
    ],
    links: [
      { source: "Orchestrator", target: "Planner" },
      { source: "Planner", target: "Scheduler" },
      { source: "Scheduler", target: "Marketing" },
      { source: "Scheduler", target: "Email" },
      { source: "Crisis", target: "Scheduler" }
    ]
  }

  return (
    <div className="bg-gray-800 p-4 rounded h-[500px]">
      <ForceGraph2D graphData={data} />
    </div>
  )
}