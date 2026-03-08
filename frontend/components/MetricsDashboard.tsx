import { LineChart,Line,XAxis,YAxis } from "recharts"

export default function MetricsDashboard(){

  const data = [
    {day:1,users:200},
    {day:2,users:450},
    {day:3,users:800}
  ]

  return(

    <LineChart width={400} height={300} data={data}>

      <XAxis dataKey="day"/>
      <YAxis/>

      <Line dataKey="users"/>

    </LineChart>

  )
}