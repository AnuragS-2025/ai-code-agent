import { useState, useEffect } from "react";
import { FaWrench, FaCheckCircle, FaCode, FaArrowLeft, FaSpinner } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import * as api from "../services/api"; 

export default function Validation() {
  const navigate = useNavigate();
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fixingId, setFixingId] = useState(null);
  const [fixedLogs, setFixedLogs] = useState([]);

  useEffect(() => {
    let isMounted = true;
    
    async function loadIssues() {
      try {
        if (api && typeof api.getIssues === "function") {
          const data = await api.getIssues();
          if (isMounted) {
            // Priority ordering to maintain structural lists safely
            setIssues(data?.issues || (Array.isArray(data) ? data : []));
          }
        }
      } catch (err) {
        console.warn("Using fallback static issues data:", err.message);
        if (isMounted) {
          setIssues([
            { id: 1, file: "auth/service.py", line: 42, severity: "error", message: "Hardcoded password/token string found in environment map.", code: "JWT_SECRET = 'super_secret_rgba_token_key'", proposed: "import os\nJWT_SECRET = os.getenv('JWT_SECRET')" },
            { id: 2, file: "database/connection.py", line: 18, severity: "warning", message: "Unused import statement detected (sys module imported but never evaluated).", code: "import os\nimport sys", proposed: "import os" }
          ]);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadIssues();
    return () => { isMounted = false; };
  }, []);

  const handleApplyFix = async (id, file) => {
    try {
      setFixingId(id);
      setFixedLogs(prev => [...prev, `[AI AGENT] Communicating pipeline patch requirements for ${file}...`]);
      
      if (api && typeof api.applyCodeFix === "function") {
        // Trigger real Axios call directly to FastAPI
        await api.applyCodeFix(id, file);
        setFixedLogs(prev => [...prev, `[SUCCESS] Refactored patch successfully pushed to repository.`]);
      } else {
        // Fallback simulation timer
        await new Promise(resolve => setTimeout(resolve, 1000));
        setFixedLogs(prev => [...prev, `[SUCCESS] Simulated offline fallback commit for ${file}.`]);
      }
      
      setIssues(prev => prev.filter(issue => issue.id !== id));
    } catch (err) {
      console.error(err);
      setFixedLogs(prev => [...prev, `[CRITICAL ERROR] Patch deployment aborted: ${err.message}`]);
    } finally {
      setFixingId(null);
    }
  };

  if (loading) {
    return (
      <div className="text-center p-10 text-cyan-400 font-medium">
        Loading Agent Validation Hub...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate("/reports")} 
          className="p-2.5 bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 rounded-lg transition-colors"
        >
          <FaArrowLeft />
        </button>
        <div>
          <h1 className="text-4xl font-bold">AI Autofix Validator</h1>
          <p className="text-slate-400 mt-1">Review AI-proposed patches and trigger safe deployments into your codebase.</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 items-start">
        <div className="col-span-2 space-y-4">
          {issues.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center space-y-3">
              <div className="text-green-400 text-4xl flex justify-center"><FaCheckCircle /></div>
              <h3 className="text-xl font-semibold text-slate-200">All Clear!</h3>
              <p className="text-slate-500 text-sm">No remaining code vulnerabilities require validation actions.</p>
            </div>
          ) : (
            issues.map((issue) => (
              <div key={issue.id} className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-sm font-mono text-cyan-400 font-bold">{issue.file} : Line {issue.line}</span>
                    <p className="text-slate-300 text-sm mt-1">{issue.message}</p>
                  </div>
                  <button
                    onClick={() => handleApplyFix(issue.id, issue.file)}
                    disabled={fixingId !== null}
                    className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 px-4 py-2 rounded-lg text-xs font-bold transition-colors disabled:opacity-40"
                  >
                    {fixingId === issue.id ? <FaSpinner className="animate-spin" /> : <FaWrench />}
                    Accept & Fix
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div className="bg-red-950/20 border border-red-900/30 rounded-lg p-3">
                    <span className="text-red-400 block mb-1 font-semibold text-[10px] uppercase tracking-wider">Current Code</span>
                    <pre className="text-red-200/80 overflow-x-auto whitespace-pre-wrap">{issue.code}</pre>
                  </div>
                  
                  <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-lg p-3">
                    <span className="text-emerald-400 block mb-1 font-semibold text-[10px] uppercase tracking-wider">AI Proposed Patch</span>
                    <pre className="text-emerald-200/80 overflow-x-auto whitespace-pre-wrap">{issue.proposed}</pre>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-slate-200 font-semibold border-b border-slate-800 pb-2">
            <FaCode className="text-cyan-400" />
            <h3>Deployment Logs</h3>
          </div>
          <div className="bg-black/50 rounded-lg p-3 h-64 overflow-y-auto font-mono text-[11px] space-y-1.5 text-slate-400">
            {fixedLogs.length === 0 ? (
              <span className="text-slate-600 italic">Awaiting pipeline trigger signals...</span>
            ) : (
              fixedLogs.map((log, idx) => (
                <p key={idx} className={log.includes("[SUCCESS]") ? "text-emerald-400" : log.includes("[CRITICAL]") ? "text-red-400" : "text-cyan-500"}>
                  {log}
                </p>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}