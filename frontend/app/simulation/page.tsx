"use client"

import { simulateCrisis } from "../../lib/api"

export default function Simulation(){

  const cancelSpeaker = async ()=>{

    await simulateCrisis({
      type:"speaker_cancelled"
    })

    alert("Speaker cancelled → system re-planned")

  }

  return(

    <div>

      <h1 className="text-xl mb-4">
        Event Simulation
      </h1>

      <button
        className="bg-red-600 p-3 rounded"
        onClick={cancelSpeaker}
      >
        Simulate Speaker Cancellation
      </button>

    </div>
  )
}