import { NavLink } from "react-router-dom";
import {
  FaHome,
  FaSearch,
  FaFileAlt,
  FaTerminal, 
  FaShieldAlt,
  FaWrench,
  FaRobot
} from "react-icons/fa";

// 🎯 FIX: 'Settings' object has been removed from this array
const menuItems = [
  { name: "Dashboard", path: "/", icon: <FaHome /> },
  { name: "Scanner Engine", path: "/scan", icon: <FaSearch /> },
  { name: "Reports & Metrics", path: "/reports", icon: <FaFileAlt /> },
  { name: "Issue Explorer", path: "/issues", icon: <FaTerminal /> },
  { name: "Validation Hub", path: "/validation", icon: <FaShieldAlt /> },
  { name: "System Tools", path: "/tools", icon: <FaWrench /> },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col text-white shadow-xl relative z-20">
      
      {/* Brand Section */}
      <div className="p-6 flex items-center gap-3 border-b border-slate-800/60 mb-4">
        <div className="bg-cyan-500/10 p-2 rounded-lg border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.15)]">
          <FaRobot className="text-cyan-400 text-2xl" />
        </div>
        <div className="flex flex-col">
          <h2 className="text-xl font-bold tracking-wide text-slate-100 font-sans leading-tight">
            AI Code
          </h2>
          <h2 className="text-xl font-bold tracking-wide text-cyan-400 font-sans leading-tight">
            Agent
          </h2>
        </div>
      </div>

      {/* Navigation Section */}
      <nav className="flex-1 flex flex-col gap-2 px-4 overflow-y-auto overflow-x-hidden">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-mono text-sm border ${
                isActive
                  ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30 shadow-[inset_0_0_15px_rgba(6,182,212,0.1)]"
                  : "border-transparent hover:bg-slate-800/50 hover:border-slate-700 hover:text-slate-200 text-slate-400"
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer Status Widget */}
      <div className="p-4 border-t border-slate-800/60 mt-auto">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col gap-2 relative overflow-hidden group">
          <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <FaShieldAlt className="text-6xl text-cyan-400" />
          </div>
          <p className="text-[10px] font-mono text-slate-400 uppercase tracking-wider z-10">Engine Status</p>
          <p className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 z-10">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
            Fully Operational
          </p>
        </div>
      </div>
      
    </aside>
  );
}