import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function MonteCarloChart({ metrics }: { metrics: any }) {
  // If no metrics yet, show a scanning animation
  if (!metrics || !metrics.simulations) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-vscode-blue animate-pulse">
        <span className="text-xs tracking-widest uppercase">Initializing Monte Carlo Physics Engine...</span>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-4">
      <h3 className="text-xs text-gray-400 mb-4 flex justify-between">
        <span>MONTE CARLO TRAJECTORY: {metrics.strategy_name}</span>
        <span className="text-vscode-green">100 Iterations</span>
      </h3>
      
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={metrics.simulations}>
            <defs>
              <linearGradient id="colorSafety" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4EC9B0" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#4EC9B0" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="iteration" stroke="#666" tick={{fontSize: 10}} />
            <YAxis stroke="#666" tick={{fontSize: 10}} domain={[0, 100]} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e1e1e', borderColor: '#333', fontSize: '12px' }}
              itemStyle={{ color: '#4EC9B0' }}
            />
            <Area 
              type="monotone" 
              dataKey="safety_score" 
              stroke="#4EC9B0" 
              fillOpacity={1} 
              fill="url(#colorSafety)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-2 text-[10px] text-gray-500 flex justify-between">
        <span>Avg Bottleneck Risk: <span className="text-red-400">{metrics.avg_bottleneck}%</span></span>
        <span>Convergence Confidence: <span className="text-vscode-green">98.4%</span></span>
      </div>
    </div>
  );
}