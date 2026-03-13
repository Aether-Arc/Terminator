import React, { useState } from 'react';

// Define our specific LangGraph nodes
const PIPELINE_NODES = [
  { id: "planner", label: "Event Planner" },
  { id: "scheduler", label: "Scheduler" },
  { id: "human_review", label: "Human Approval" },
  { id: "execution_phase", label: "Map-Reduce Execution", isParallel: true },
];

export type NodeStatus = "waiting" | "running" | "completed";

interface PipelineTrackerProps {
  nodeStatuses: Record<string, NodeStatus>;
  activeLogs: Record<string, string>; // The live streaming text for each node
}

export default function PipelineTracker({ nodeStatuses, activeLogs }: PipelineTrackerProps) {
  return (
    <div className="space-y-6">
      {/* 1. PIPELINE PROGRESS BAR */}
      <div className="flex items-center justify-between bg-black/20 p-4 rounded-2xl border border-white/10 backdrop-blur-md">
        {PIPELINE_NODES.map((node, index) => {
          const status = nodeStatuses[node.id] || "waiting";
          
          const colors = {
            waiting: "bg-slate-800 text-slate-500 border-slate-700",
            running: "bg-blue-500/20 text-blue-400 border-blue-500/50 animate-pulse shadow-[0_0_15px_rgba(59,130,246,0.5)]",
            completed: "bg-emerald-500/20 text-emerald-400 border-emerald-500/50",
          };

          return (
            <React.Fragment key={node.id}>
              <div className={`flex flex-col items-center gap-2`}>
                <div className={`px-4 py-2 rounded-full text-xs font-bold border transition-all duration-500 ${colors[status]}`}>
                  {node.label}
                </div>
              </div>
              {/* Connector Line */}
              {index < PIPELINE_NODES.length - 1 && (
                <div className={`flex-1 h-1 mx-2 rounded-full transition-all duration-500 ${
                  status === "completed" ? "bg-emerald-500/50" : "bg-slate-800"
                }`} />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* 2. EXECUTING NODE CARDS */}
      <div className="grid grid-cols-1 gap-4">
        {PIPELINE_NODES.map((node) => {
          const status = nodeStatuses[node.id] || "waiting";
          // Only show cards that are currently running or just completed
          if (status === "waiting") return null;

          return (
            <div key={node.id} className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md transition-all">
              <div className="flex justify-between items-center p-4 bg-black/20">
                <div className="flex items-center gap-3">
                  <h3 className="font-semibold text-slate-200">{node.label}</h3>
                  {status === "running" && (
                    <span className="flex items-center gap-2 px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-md">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
                      Executing
                    </span>
                  )}
                  {status === "completed" && (
                    <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-md">Done</span>
                  )}
                </div>
              </div>
              
              {/* Streaming Content Body */}
              <div className="p-4 border-t border-white/5 text-sm text-slate-400 font-mono whitespace-pre-wrap">
                {activeLogs[node.id] || (status === "running" ? "Initializing agent logic..." : "Task successfully completed.")}
                {status === "running" && <span className="inline-block w-2 h-4 ml-1 bg-blue-400 animate-pulse"></span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}