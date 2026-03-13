"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

// Define TypeScript interfaces based on your backend output
interface ScheduleItem {
  time: string;
  session: string;
  [key: string]: any;
}

interface EventData {
  thread_id: string;
  schedule: ScheduleItem[];
  marketing_copy: string;
  email_logs: any[];
  agent_outputs?: any;
}

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const threadId = searchParams.get("threadId") || "event_thread_1"; // Default for testing

  // State Management
  const [eventData, setEventData] = useState<EventData | null>(null);
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [aiInstruction, setAiInstruction] = useState("");
  
  // UI States
  const [isLoading, setIsLoading] = useState(true);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [isSavingManual, setIsSavingManual] = useState(false);

  // 1. FETCH EVENT DETAILS ON PAGE LOAD
  useEffect(() => {
    const fetchEventData = async () => {
      setIsLoading(true);
      try {
        // Replace with your actual FastAPI backend URL
        const response = await fetch(`http://localhost:8000/api/history/${threadId}`);
        const data = await response.json();
        
        if (!data.error) {
          setEventData(data);
          setSchedule(data.schedule || []);
        } else {
          console.error("Failed to load thread:", data.error);
        }
      } catch (error) {
        console.error("Error fetching event data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    if (threadId) {
      fetchEventData();
    }
  }, [threadId]);

  // 2. HANDLE AI INSTRUCTION SUBMIT (Routes to Planner)
  const handleAiInstructionSubmit = async () => {
    if (!aiInstruction.trim()) return;
    setIsAiLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/edit/prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          prompt_text: aiInstruction
        })
      });
      
      const result = await response.json();
      // If the AI rewrites the schedule, update the UI
      if (result.schedule) {
        setSchedule(result.schedule);
        alert("AI successfully replanned the event!");
      }
      setAiInstruction(""); // Clear input
    } catch (error) {
      console.error("AI Re-plan error:", error);
      alert("Failed to send AI instruction.");
    } finally {
      setIsAiLoading(false);
    }
  };

  // 3. HANDLE MANUAL SCHEDULE EDITS (Updates UI state locally)
  const handleScheduleChange = (index: number, field: keyof ScheduleItem, value: string) => {
    const updatedSchedule = [...schedule];
    updatedSchedule[index] = { ...updatedSchedule[index], [field]: value };
    setSchedule(updatedSchedule);
  };

  // 4. SAVE MANUAL EDITS (Bypasses LLM, instant update)
  const handleManualSave = async () => {
    setIsSavingManual(true);
    try {
      const response = await fetch(`http://localhost:8000/api/edit/manual`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          override_type: "edit_schedule",
          new_schedule: schedule,
          csv_content: "" // Pass your CSV content if needed for emails
        })
      });
      
      const result = await response.json();
      alert("Manual schedule edits saved and participants notified!");
    } catch (error) {
      console.error("Manual save error:", error);
      alert("Failed to save manual edits.");
    } finally {
      setIsSavingManual(false);
    }
  };

  if (isLoading) {
    return <div className="p-10 text-center text-xl">Loading Event Dashboard...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <header className="border-b pb-4">
        <h1 className="text-3xl font-bold text-gray-800">Event Dashboard</h1>
        <p className="text-gray-500">Thread ID: {threadId}</p>
      </header>

      {/* --- AI INSTRUCTION SECTION --- */}
      <section className="bg-blue-50 p-6 rounded-lg border border-blue-100 shadow-sm">
        <h2 className="text-xl font-semibold text-blue-800 mb-2">Ask AI to Re-plan</h2>
        <p className="text-sm text-blue-600 mb-4">
          Need a major change? Tell the Swarm to rebuild the schedule automatically.
        </p>
        <div className="flex gap-4">
          <input
            type="text"
            className="flex-1 p-3 border rounded-md shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="e.g., 'Make room for a 30 minute lunch break at 1 PM'"
            value={aiInstruction}
            onChange={(e) => setAiInstruction(e.target.value)}
            disabled={isAiLoading}
          />
          <button
            onClick={handleAiInstructionSubmit}
            disabled={isAiLoading || !aiInstruction.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isAiLoading ? "AI is Replanning..." : "Add AI Instruction"}
          </button>
        </div>
      </section>

      {/* --- MANUAL SCHEDULE EDITOR SECTION --- */}
      <section className="bg-white p-6 rounded-lg border shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Event Schedule</h2>
            <p className="text-sm text-gray-500">Edit table directly to fix typos or minor timing issues.</p>
          </div>
          <button
            onClick={handleManualSave}
            disabled={isSavingManual}
            className="bg-green-600 text-white px-5 py-2 rounded-md font-semibold hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {isSavingManual ? "Saving..." : "Save Manual Edits"}
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-100 text-gray-700">
                <th className="p-3 border-b w-1/4">Time</th>
                <th className="p-3 border-b w-3/4">Session</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="p-2 border-b">
                    <input
                      type="text"
                      className="w-full p-2 border rounded border-transparent hover:border-gray-300 focus:border-blue-500 focus:bg-white bg-transparent outline-none"
                      value={item.time}
                      onChange={(e) => handleScheduleChange(index, "time", e.target.value)}
                    />
                  </td>
                  <td className="p-2 border-b">
                    <input
                      type="text"
                      className="w-full p-2 border rounded border-transparent hover:border-gray-300 focus:border-blue-500 focus:bg-white bg-transparent outline-none"
                      value={item.session}
                      onChange={(e) => handleScheduleChange(index, "session", e.target.value)}
                    />
                  </td>
                </tr>
              ))}
              {schedule.length === 0 && (
                <tr>
                  <td colSpan={2} className="p-4 text-center text-gray-500">No schedule generated yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* --- MARKETING & EMAILS SECTION --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-white p-6 rounded-lg border shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Marketing Assets</h2>
          <div className="bg-gray-50 p-4 rounded-md h-64 overflow-y-auto whitespace-pre-wrap text-sm border">
            {eventData?.marketing_copy || "No marketing copy available."}
          </div>
        </section>

        <section className="bg-white p-6 rounded-lg border shadow-sm">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Email Logs</h2>
          <div className="bg-gray-50 p-4 rounded-md h-64 overflow-y-auto text-sm border">
            {eventData?.email_logs && eventData.email_logs.length > 0 ? (
              <ul className="space-y-2">
                {eventData.email_logs.map((log, idx) => (
                  <li key={idx} className="border-b pb-2 last:border-0 text-gray-700">
                    <span className="font-semibold text-gray-900">To:</span> {log.recipient || "Participants"} <br />
                    <span className="font-semibold text-gray-900">Status:</span> {log.status || "Sent"}
                  </li>
                ))}
              </ul>
            ) : (
              <span className="text-gray-500">No email logs available.</span>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}