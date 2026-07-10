import { FaRobot, FaCircle, FaServer } from "react-icons/fa";

export default function Navbar() {
  return (
    <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6 shadow-sm z-10 sticky top-0">
      {/* Left: Logo & Brand */}
      <div className="flex items-center gap-3">
        <div className="bg-cyan-500/10 p-2 rounded-lg border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.15)]">
          <FaRobot className="text-cyan-400 text-xl" />
        </div>
        <h1 className="text-lg font-bold text-slate-100 tracking-wide font-sans">
          AI Code Agent <span className="text-cyan-400 font-mono text-xs ml-1 px-1.5 py-0.5 bg-cyan-900/30 rounded border border-cyan-800/50">v1.0</span>
        </h1>
      </div>

      {/* Right: Stacked Telemetry Info Panel (No User Profile) */}
      <div className="flex flex-col items-end gap-0.5">
        
        {/* Top Line: Engine Driver Context */}
        <div className="flex items-center gap-1.5 text-cyan-400 font-mono text-xs font-bold tracking-wide">
          <FaServer className="text-[10px] text-slate-500" />
          <span>Ollama Engine</span>
        </div>

        {/* Bottom Line: Network Live Status */}
        <div className="flex items-center gap-1.5">
          <FaCircle className="text-[6px] text-emerald-400 animate-pulse drop-shadow-[0_0_4px_rgba(16,185,129,0.8)]" />
          <span className="text-[9px] uppercase font-mono font-extrabold text-slate-400 tracking-wider">
            System Online
          </span>
        </div>

      </div>
    </header>
  );
}