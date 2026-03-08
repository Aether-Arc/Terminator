"use client"

import EventForm from "../../components/EventForm"
import ScheduleView from "../../components/ScheduleView"
import AgentMonitor from "../../components/AgentMonitor"

export default function Dashboard(){

  return(

    <div className="grid grid-cols-2 gap-6">

      <div>
        <EventForm/>
      </div>

      <div>
        <ScheduleView/>
      </div>

      <div className="col-span-2">
        <AgentMonitor/>
      </div>

    </div>
  )
}