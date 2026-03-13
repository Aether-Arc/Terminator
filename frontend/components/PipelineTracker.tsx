import React from 'react';

// 🚀 FIXED: Capitalized IDs to match the WebSocket mapping exactly
const PIPELINE_NODES = [
  { id: "Planner", label: "Event Planner" },
  { id: "Scheduler", label: "Scheduler" },
  { id: "Human_review", label: "Human Approval" },
  { id: "Execution_phase", label: "Map-Reduce Execution", isParallel: true },
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
      <div className="flex items-center justify-between bg-slate-50 p-4 rounded-xl border border-slate-200">
        {PIPELINE_NODES.map((node, index) => {
          const status = nodeStatuses[node.id] || "waiting";
          
          // 🚀 MATCHED TO LIGHT THEME
          const colors = {
            waiting: "bg-white text-slate-400 border-slate-200",
            running: "bg-indigo-50 text-indigo-600 border-indigo-200 animate-pulse shadow-sm",
            completed: "bg-emerald-50 text-emerald-600 border-emerald-200",
          };

          return (
            <React.Fragment key={node.id}>
              <div className={`flex flex-col items-center gap-2 z-10`}>
                <div className={`px-4 py-2 rounded-full text-xs font-bold border transition-all duration-500 ${colors[status]}`}>
                  {node.label}
                </div>
              </div>
              {/* Connector Line */}
              {index < PIPELINE_NODES.length - 1 && (
                <div className={`flex-1 h-1 mx-2 rounded-full transition-all duration-500 ${
                  status === "completed" ? "bg-emerald-200" : "bg-slate-200"
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
            <div key={node.id} className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm transition-all">
              <div className="flex justify-between items-center p-3 px-4 bg-slate-50 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <h3 className="font-semibold text-slate-700 text-sm">{node.label}</h3>
                  {status === "running" && (
                    <span className="flex items-center gap-2 px-2.5 py-1 bg-indigo-100 text-indigo-700 text-[10px] font-bold uppercase tracking-wider rounded-md">
                      <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-ping"></div>
                      Executing
                    </span>
                  )}
                  {status === "completed" && (
                    <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 text-[10px] font-bold uppercase tracking-wider rounded-md">Done</span>
                  )}
                </div>
              </div>
              
              {/* Streaming Content Body */}
              <div className="p-4 text-xs text-slate-500 font-mono whitespace-pre-wrap leading-relaxed">
                {activeLogs[node.id] || (status === "running" ? "Initializing agent logic..." : "Task successfully completed.")}
                {status === "running" && <span className="inline-block w-1.5 h-3 ml-1 bg-indigo-400 animate-pulse"></span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}