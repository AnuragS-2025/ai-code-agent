import { useEffect, useState } from "react";
import { FaShieldAlt, FaExclamationTriangle, FaInfoCircle, FaFileCode, FaCheckCircle, FaWrench } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { getReport } from "../services/api";

export default function Reports() {
  const navigate = useNavigate();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState("all");

  useEffect(() => {
    let isMounted = true;

    async function fetchReportDetails() {
      try {
        const data = await getReport();
        if (isMounted) {
          setReportData(data);
        }
      } catch (error) {
        console.error("Failed to load audit report:", error);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchReportDetails();

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="text-center p-10 text-cyan-400 font-medium">
        Loading Code Audit Reports...
      </div>
    );
  }

  // Fallback / Mock mockup objects agar backend response blank ho toh array parsing safe rahe
  const summary = reportData?.summary || { total_scans: 42, total_issues: 148, warnings: 19, errors: 8 };
  const issues = reportData?.issues || [
    { id: 1, file: "auth/service.py", line: 42, severity: "error", tool: "Bandit", message: "Hardcoded password/token string found in environment map.", code: "JWT_SECRET = 'super_secret_rgba_token_key'" },
    { id: 2, file: "database/connection.py", line: 18, severity: "warning", tool: "Ruff", message: "Unused import statement detected (sys module imported but never evaluated).", code: "import os\nimport sys  # 👈 Unused issue" },
    { id: 3, file: "routes/users.py", line: 105, severity: "info", tool: "Flake8", message: "Line length exceeds standard formatting limit (longer than 88 chars).", code: "return {'status': 'success', 'message': 'User details pulled securely from cluster indexing primary keys'}" }
  ];

  // Filtering issues based on sidebar selector dropdown matrix
  const filteredIssues = issues.filter(issue => {
    if (selectedSeverity === "all") return true;
    return issue.severity.toLowerCase() === selectedSeverity.toLowerCase();
  });

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold">Vulnerability Report</h1>
          <p className="text-slate-400 mt-2">Deep analytics of security posture and standard code optimization specs.</p>
        </div>
        <button 
          onClick={() => navigate("/validation")}
          className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-slate-950 px-5 py-3 rounded-lg font-bold shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-colors"
        >
          <FaWrench /> Auto-Fix Pipeline
        </button>
      </div>

      {/* Mini Counters Ribbon Layout */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-lg text-xl"><FaFileCode /></div>
          <div>
            <span className="text-slate-500 text-xs uppercase font-semibold">Audited Files</span>
            <span className="block text-2xl font-bold text-slate-200">{summary.total_scans ?? 42}</span>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-red-500/10 text-red-500 rounded-lg text-xl"><FaShieldAlt /></div>
          <div>
            <span className="text-slate-500 text-xs uppercase font-semibold">Critical Errors</span>
            <span className="block text-2xl font-bold text-red-500">{summary.errors ?? 8}</span>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-yellow-500/10 text-yellow-500 rounded-lg text-xl"><FaExclamationTriangle /></div>
          <div>
            <span className="text-slate-500 text-xs uppercase font-semibold">Warnings</span>
            <span className="block text-2xl font-bold text-yellow-400">{summary.warnings ?? 19}</span>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-green-500/10 text-green-400 rounded-lg text-xl"><FaCheckCircle /></div>
          <div>
            <span className="text-slate-500 text-xs uppercase font-semibold">Total Threat Vectors</span>
            <span className="block text-2xl font-bold text-slate-200">{summary.total_issues ?? 148}</span>
          </div>
        </div>
      </div>

      {/* Severe Filters Navigation Strip */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        <div className="flex justify-between items-center border-b border-slate-800 pb-4">
          <h2 className="text-xl font-semibold text-slate-200">Discovered Issues Pool</h2>
          <div className="flex gap-2">
            {["all", "error", "warning", "info"].map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all border ${
                  selectedSeverity === sev 
                    ? "bg-cyan-500 text-slate-950 border-cyan-500" 
                    : "bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700"
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* Dynamic Threat Cards Rendering Loop */}
        <div className="space-y-4">
          {filteredIssues.length === 0 ? (
            <p className="text-slate-500 font-mono text-sm text-center py-6">Clean sheet! No diagnostic issues found for the selected filter.</p>
          ) : (
            filteredIssues.map((issue, index) => {
              const isError = issue.severity.toLowerCase() === "error";
              const isWarning = issue.severity.toLowerCase() === "warning";

              return (
                <div 
                  key={issue.id || index}
                  className={`border rounded-xl p-5 bg-slate-950/40 transition-all ${
                    isError ? "border-red-500/20 hover:border-red-500/40" : isWarning ? "border-yellow-500/20 hover:border-yellow-500/40" : "border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                      <span className={`p-2 rounded-lg text-sm ${
                        isError ? "bg-red-500/10 text-red-400" : isWarning ? "bg-yellow-500/10 text-yellow-400" : "bg-cyan-500/10 text-cyan-400"
                      }`}>
                        {isError ? <FaShieldAlt /> : isWarning ? <FaExclamationTriangle /> : <FaInfoCircle />}
                      </span>
                      <div>
                        <span className="text-sm font-mono text-slate-200 block font-semibold">{issue.file} : Line {issue.line}</span>
                        <span className="text-xs text-slate-500 font-medium">Telemetry Source: <strong className="text-slate-400">{issue.tool || "Engine"}</strong></span>
                      </div>
                    </div>
                    
                    <span className={`px-2.5 py-1 rounded text-[10px] font-mono uppercase tracking-wider font-bold ${
                      isError ? "bg-red-500/20 text-red-400" : isWarning ? "bg-yellow-500/20 text-yellow-400" : "bg-cyan-500/20 text-cyan-400"
                    }`}>
                      {issue.severity}
                    </span>
                  </div>

                  <p className="text-slate-300 text-sm pl-10 mb-4 font-sans leading-relaxed">{issue.message}</p>

                  {/* Isolated Shell/Code Editor Mock block */}
                  {issue.code && (
                    <div className="pl-10">
                      <div className="bg-black/80 border border-slate-900 rounded-lg p-3 font-mono text-xs text-slate-400 overflow-x-auto shadow-inner">
                        <span className="text-slate-600 block mb-1 select-none">// Trace Context:</span>
                        <code className={isError ? "text-red-300/90" : isWarning ? "text-yellow-200/90" : "text-cyan-300/90"}>
                          {issue.code}
                        </code>
                      </div>
                    </div>
                  )}

                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}