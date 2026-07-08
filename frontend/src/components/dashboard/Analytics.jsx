export default function Analytics({ topRules = {}, summary = {} }) {
  const totalIssues = summary.total_issues || 0;
  const fixedIssues = summary.total_fixed || 0;
  const remainingIssues = totalIssues - fixedIssues > 0 ? totalIssues - fixedIssues : 0;

  // Real data handling with stable mock fallback
  const currentRules = Object.keys(topRules).length 
    ? topRules 
    : { "E501": 12, "F401": 8, "B602": 15, "E722": 4, "B404": 9 };

  const ruleLabels = Object.keys(currentRules);
  const ruleValues = Object.values(currentRules);

  // Auto Scaling logic taaki single digital errors bhi fully scale up ho sakein
  const maxRuleValue = Math.max(...ruleValues, 1);

  return (
    <div className="grid grid-cols-2 gap-6 mt-8">
      {/* 1. Project Health Dynamic Bar Chart */}
      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
        <h3 className="text-xl font-semibold mb-4 text-slate-200">Project Health</h3>
        
        <div className="flex items-end justify-between h-48 pt-8 px-4 bg-slate-950/40 rounded-lg gap-4">
          {ruleLabels.map((label, idx) => {
            const rawValue = ruleValues[idx] || 0;
            const calculatedPercentage = ((rawValue / maxRuleValue) * 100).toFixed(0);

            return (
              <div key={label} className="flex flex-col items-center justify-end h-full w-full group relative">
                
                {/* Count tooltip on hover */}
                <span className="text-[11px] font-mono font-bold text-cyan-400 mb-1 opacity-0 group-hover:opacity-100 transition-opacity absolute -top-5">
                  {rawValue}
                </span>

                {/* Main Active Bar (Updated with canonical Tailwind class max-w-9) */}
                <div 
                  className="w-full max-w-9 bg-cyan-500 rounded-t transition-all duration-500 ease-out shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:bg-cyan-400"
                  style={{ 
                    height: `${calculatedPercentage}%`,
                    minHeight: rawValue > 0 ? '16px' : '4px' 
                  }}
                ></div>

                {/* Bottom Label Axis */}
                <span className="text-[11px] font-mono text-slate-400 mt-2 block pt-1 border-t border-slate-800/60 w-full text-center">
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Security Overview Circular Progress */}
      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
        <h3 className="text-xl font-semibold mb-4 text-slate-200">Security Overview</h3>
        <div className="flex items-center justify-around h-48 bg-slate-950/40 rounded-lg p-4">
          
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-cyan-500 rounded-full"></span>
              <span className="text-sm text-slate-400">Fixed Issues ({fixedIssues})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-red-500 rounded-full"></span>
              <span className="text-sm text-slate-400">Remaining ({remainingIssues})</span>
            </div>
          </div>

          <div className="relative flex items-center justify-center">
            {/* Glowing Ring UI Layer */}
            <div className="w-28 h-28 rounded-full border-4 border-cyan-500/10 border-t-cyan-500 border-r-cyan-500 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.1)]">
              <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center absolute">
                <div className="text-center">
                  <span className="text-3xl font-bold text-slate-200 block">
                    {summary.security_score || 96}%
                  </span>
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block mt-0.5">Score</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}