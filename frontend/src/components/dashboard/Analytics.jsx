export default function Analytics({ topRules = {}, summary = {} }) {
  const totalIssues = summary.total_issues || 0;
  const fixedIssues = summary.total_fixed || 0;
  const remainingIssues = totalIssues - fixedIssues > 0 ? totalIssues - fixedIssues : 0;

  // 🎯 FIX 1: Safe fallback jo 0 issues hone par fake bugs nahi banayega
  const currentRules = Object.keys(topRules).length > 0 
    ? topRules 
    : { "bandit": 0, "ruff": 0, "semgrep": 0 };

  const ruleLabels = Object.keys(currentRules);
  const ruleValues = Object.values(currentRules);

  // Auto Scaling logic taaki single digit errors bhi fully scale up ho sakein
  const maxRuleValue = Math.max(...ruleValues, 1);

  // 🎯 FIX 2: Handle both numeric scores (96%) and letter grades (A+) properly
  const rawScore = summary.security_score ?? 100;
  const displayScore = typeof rawScore === "number" ? `${rawScore}%` : rawScore;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
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

                {/* Main Active Bar */}
                <div 
                  className={`w-full max-w-9 rounded-t transition-all duration-500 ease-out ${
                    rawValue > 0 
                      ? "bg-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.4)] hover:bg-cyan-400" 
                      : "bg-slate-800/50" // Clean slate for 0 bugs
                  }`}
                  style={{ 
                    height: `${calculatedPercentage}%`,
                    minHeight: rawValue > 0 ? '16px' : '4px' 
                  }}
                ></div>

                {/* Bottom Label Axis */}
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 mt-2 block pt-1 border-t border-slate-800/60 w-full text-center truncate px-1">
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
              <span className="w-3 h-3 bg-cyan-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.5)]"></span>
              <span className="text-sm text-slate-400 font-medium">Fixed Issues ({fixedIssues})</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${remainingIssues > 0 ? "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" : "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"}`}></span>
              <span className="text-sm text-slate-400 font-medium">Remaining ({remainingIssues})</span>
            </div>
          </div>

          <div className="relative flex items-center justify-center">
            {/* Glowing Ring UI Layer */}
            <div className={`w-28 h-28 rounded-full border-4 flex items-center justify-center transition-colors ${
              remainingIssues > 0 
                ? "border-cyan-500/10 border-t-cyan-500 border-r-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.1)]"
                : "border-emerald-500/10 border-t-emerald-500 border-r-emerald-500 border-b-emerald-500 border-l-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.2)]"
            }`}>
              <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center absolute shadow-inner">
                <div className="text-center">
                  <span className={`text-3xl font-bold block ${remainingIssues === 0 ? "text-emerald-400" : "text-slate-200"}`}>
                    {displayScore}
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