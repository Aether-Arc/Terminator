export default function ScheduleView(){

  const schedule = [
    {session:"Opening",time:"9:00"},
    {session:"AI Workshop",time:"10:00"},
    {session:"Hackathon Start",time:"12:00"}
  ]

  return(

    <div className="bg-gray-800 p-4 rounded">

      <h2 className="text-lg mb-3">
        Event Schedule
      </h2>

      {schedule.map((s)=>(
        <div key={s.session}
         className="flex justify-between border-b py-2">

         <span>{s.session}</span>
         <span>{s.time}</span>

        </div>
      ))}

    </div>
  )
}