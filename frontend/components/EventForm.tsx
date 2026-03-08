"use client"

import { useState } from "react"
import { createEvent } from "../lib/api"

export default function EventForm(){

  const [name,setName] = useState("")
  const [venue,setVenue] = useState("")

  const submit = async ()=>{

    await createEvent({
      name,
      venue,
      days:2,
      tracks:["AI","Cloud"],
      speakers:["Alice","Bob"]
    })

    alert("Event planned!")

  }

  return(

    <div className="bg-gray-800 p-4 rounded">

      <h2 className="text-lg mb-3">Create Event</h2>

      <input
        placeholder="Event name"
        className="w-full p-2 mb-2 text-black"
        onChange={(e)=>setName(e.target.value)}
      />

      <input
        placeholder="Venue"
        className="w-full p-2 mb-2 text-black"
        onChange={(e)=>setVenue(e.target.value)}
      />

      <button
        onClick={submit}
        className="bg-blue-600 px-4 py-2 rounded"
      >
        Run AI Swarm
      </button>

    </div>
  )
}