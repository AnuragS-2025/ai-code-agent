import { useState, useEffect } from "react";
import { 
  FaCogs, FaTools, FaCheckCircle, FaServer, FaSpinner, 
  FaTimesCircle, FaRobot, FaFolderOpen, FaSave 
} from "react-icons/fa";
import { getConfig, getTools } from "../services/api";

export default function ToolsConfig() {
  const [config, setConfig] = useState({});
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);

  const [scanFolder, setScanFolder] = useState(() => localStorage.getItem("ai_agent_folder") || "C:/Projects");
  const [saving, setSaving] = useState(false);
  const [savedAction, setSavedAction] = useState(false);

  useEffect(() => {
    let isMounted = true;
    
    async function loadSystemMeta() {
      try {
        const [configRes, toolsRes] = await Promise.allSettled([getConfig(), getTools()]);
        
        if (isMounted) {
          if (configRes.status === "fulfilled") {
            const configPayload = configRes.value?.data || configRes.value || {};
            setConfig(
              configPayload.config ||
              configPayload.settings ||
              configPayload
            );
          }
          
          if (toolsRes.status === "fulfilled") {
            const toolsPayload = toolsRes.value?.data || toolsRes.value || {};
            setTools(
              toolsPayload.tools ||
              toolsPayload.available_tools ||
              []
            );
          }
        }
      } catch (err) {
        console.error("System parameter config load failed:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    
    loadSystemMeta();
    return () => { isMounted = false; };
  }, []);

  const handleSaveSettings = () => {
    setSaving(true);
    setSavedAction(false);

    setTimeout(() => {
      localStorage.setItem("ai_agent_model", "Ollama");
      localStorage.setItem("ai_agent_folder", scanFolder);

      setSaving(false);
      setSavedAction(true);
      setTimeout(() => setSavedAction(false), 3000);
    }, 600);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 font-mono text-cyan-500 gap-4 min-h-100">
        <FaSpinner className="animate-spin text-4xl" />
        <p className="text-sm tracking-wider animate-pulse">Querying engine telemetry matrices...</p>
      </div>
    );
  }

  const configEntries = Object.entries(config);

  return (
    <div className="space-y-8 text-white w-full max-w-7xl mx-auto p-4 md:p-6 animate-fadeIn">
      {/* Header Panel */}
      <div className="border-b border-slate-800/60 pb-6">
        <h2 className="text-3xl font-extrabold flex items-center gap-3 tracking-tight bg-linear-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          <FaCogs className="text-yellow-500 text-2xl drop-shadow-[0_0_10px_rgba(234,179,8,0.4)]" /> Engine Parameters & Telemetry
        </h2>
        <p className="text-slate-400 mt-2 text-xs font-sans tracking-wide">
          Manage local AI agent environment parameters, target filesystem path triggers, and network status modules.
        </p>
      </div>

      {/* Symmetric Modern Grid Architecture */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
        
        {/* LEFT COMPONENT COLUMN: Core Metrics Stack Layout */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          {/* Section A: Active System Configuration Card */}
          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800/80 p-6 rounded-2xl shadow-2xl flex flex-col flex-1">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-mono mb-4 flex items-center gap-2 border-b border-slate-800/80 pb-3 font-bold">
              <FaServer className="text-cyan-400 text-sm" /> Active System Configuration
            </h3>
            
            <div className="grid grid-cols-1 gap-2.5 overflow-y-auto max-h-75 custom-scrollbar pr-1">
              {configEntries.length > 0 ? (
                configEntries.map(([key, val], idx) => {
                  // Hide internal objects and status flags
                  if (
                    key === "success" || 
                    key === "status" || 
                    key === "settings" || 
                    typeof val === "object"
                  ) {
                    return null;
                  }

                  return (
                    <div key={idx} className="flex justify-between items-center bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/60 text-xs font-mono hover:border-slate-700/80 hover:bg-black/40 transition-all duration-200 shadow-xs group">
                      <span className="text-slate-400 font-medium tracking-wide group-hover:text-slate-200 transition-colors">
                        {key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
                      </span>
                      <span className="text-cyan-400 font-bold truncate max-w-[60%] bg-black/40 px-3 py-1.5 rounded-lg border border-slate-800/40 shadow-inner">
                        {typeof val === "boolean" ? (
                          <span className={val ? "text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.4)]" : "text-rose-400"}>
                            {val ? "True" : "False"}
                          </span>
                        ) : (
                          String(val)
                        )}
                      </span>
                    </div>
                  );
                })
              ) : (
                <div className="flex items-center justify-center h-24 text-slate-500 text-xs font-mono bg-black/20 rounded-xl border border-dashed border-slate-800">
                  No active telemetry signals found.
                </div>
              )}
            </div>
          </div>

          {/* Section B: Discovered System Analyzers Card */}
          <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800/80 p-6 rounded-2xl shadow-2xl flex flex-col flex-1">
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-mono mb-4 flex items-center gap-2 border-b border-slate-800/80 pb-3 font-bold">
              <FaTools className="text-yellow-500 text-sm" /> Discovered System Analyzers
            </h3>
            
            <div className="grid grid-cols-1 gap-2.5 overflow-y-auto max-h-75 custom-scrollbar pr-1">
              {tools.length > 0 ? (
                tools.map((tool, index) => {
                  const toolName = typeof tool === "string" ? tool : tool.name || "Unknown";
                  const enabled = typeof tool === "object" ? tool.enabled !== false : true;

                  return (
                    <div key={index} className="bg-slate-950/50 p-3.5 rounded-xl border border-slate-800/60 flex items-center justify-between text-xs hover:border-slate-700/80 hover:bg-black/40 transition-all duration-200 shadow-xs group">
                      <span className="font-mono flex items-center gap-3 font-bold text-slate-300 capitalize tracking-wide group-hover:text-white transition-colors">
                        <FaTools className="text-slate-500 text-xs group-hover:text-yellow-500/70 transition-colors" /> {toolName}
                      </span>
                      
                      <span
                        className={`text-[10px] uppercase px-3.5 py-1.5 rounded-md flex items-center gap-2 font-mono font-extrabold border transition-all duration-300 ${
                          enabled
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]"
                            : "bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]"
                        }`}
                      >
                        {enabled ? <FaCheckCircle className="text-[11px]" /> : <FaTimesCircle className="text-[11px]" />}
                        {enabled ? "Active Node" : "Offline"}
                      </span>
                    </div>
                  );
                })
              ) : (
                <div className="flex items-center justify-center h-24 text-slate-500 text-xs font-mono bg-black/20 rounded-xl border border-dashed border-slate-800">
                  No analyzer hooks integrated yet.
                </div>
              )}
            </div>
          </div>

        </div>

        {/* RIGHT COMPONENT COLUMN: Unified Local Control Matrix */}
        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 shadow-2xl flex flex-col justify-between h-full sticky top-6">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-mono mb-6 flex items-center gap-2 border-b border-slate-800/80 pb-3 font-bold">
              <FaRobot className="text-cyan-400 text-sm" /> Local Agent Controls
            </h3>
            
            <div className="space-y-7">
              {/* Infrastructure Configuration */}
              <div className="space-y-3">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono block ml-1">
                  Active AI Infrastructure
                </label>
                <div className="w-full bg-slate-950/80 border border-slate-800/80 rounded-xl px-4 py-3.5 text-cyan-400 font-mono text-xs font-bold tracking-wide select-none shadow-inner border-l-4 border-l-cyan-500 flex items-center gap-3">
                  <FaServer className="text-slate-500 text-sm" /> Ollama Engine (Local Node)
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed font-sans px-1 pt-1">
                  Air-gapped deployment active. Model execution and dynamic neural processes evaluate safely on your local silicon logic circuits.
                </p>
              </div>

              {/* Workspace Filepath Form Input */}
              <div className="space-y-3">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2 ml-1">
                  <FaFolderOpen className="text-yellow-500 text-[11px]" /> Default Scan Workspace Path
                </label>
                <input
                  type="text"
                  value={scanFolder}
                  onChange={(e) => setScanFolder(e.target.value)}
                  placeholder="e.g., C:/Projects"
                  className="w-full bg-black/40 border border-slate-700/60 rounded-xl px-4 py-4 text-slate-200 focus:outline-none focus:border-cyan-500/80 focus:ring-1 focus:ring-cyan-500/50 transition-all duration-300 font-mono text-xs shadow-inner placeholder:text-slate-600"
                />
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="pt-6 border-t border-slate-800/80 flex flex-col gap-3 mt-10">
            <button 
              onClick={handleSaveSettings}
              disabled={saving}
              className="w-full flex items-center justify-center gap-2.5 bg-linear-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 text-white py-3.5 rounded-xl font-bold text-xs tracking-widest uppercase transition-all duration-200 shadow-[0_0_15px_rgba(8,145,178,0.3)] hover:shadow-[0_0_25px_rgba(8,145,178,0.5)] disabled:opacity-50 disabled:shadow-none cursor-pointer active:scale-[0.98]"
            >
              {saving ? <FaSpinner className="animate-spin text-sm" /> : <FaSave className="text-sm" />}
              {saving ? "Commiting Updates..." : "Save Controls Config"}
            </button>

            {savedAction && (
              <div className="flex items-center justify-center gap-2 text-emerald-400 font-mono text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/20 py-3 rounded-xl animate-pulse text-center w-full shadow-inner mt-2">
                <FaCheckCircle className="text-xs" /> Global local matrix updated!
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}