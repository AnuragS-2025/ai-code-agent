import { useState, useEffect, useCallback } from "react";
import { 
  FaWrench, FaSpinner, FaShieldAlt, FaTimesCircle, FaCheckCircle
} from "react-icons/fa";
import { getIssues, applyCodeFix } from "../services/api";

export default function Validation({ projectPath = "." }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fixing, setFixing] = useState(false);

  const fetchIssuesList = useCallback(async (isMounted) => {
    try {
      const safePath = projectPath ? projectPath.replace(/\\/g, "/") : ".";
      const filters = { project_path: safePath };
      
      const response = await getIssues(filters, true);
      
      if (isMounted) {
        if (Array.isArray(response)) {
          setIssues(response);
        } else if (response?.issues && Array.isArray(response.issues)) {
          setIssues(response.issues);
        } else {
          setIssues([]);
        }
      }
    } catch (error) {
      console.error("Failed to load validation hub parameters:", error);
    } finally {
      if (isMounted) setLoading(false);
    }
  }, [projectPath]);

  useEffect(() => {
    let isMounted = true;
    const timer = setTimeout(() => {
      if (isMounted) {
        setLoading(true);
        fetchIssuesList(isMounted);
      }
    }, 0);
    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [fetchIssuesList]);

  const handleApplyFixes = async () => {
    if (!window.confirm("Are you sure you want to trigger the AI patch pipeline? This will modify flawed source files.")) return;
    setFixing(true);
    try {
      const safePath = projectPath ? projectPath.replace(/\\/g, "/") : ".";
      const response = await applyCodeFix(safePath);
      alert(response?.message || "🎉 AI Code Fix Pipeline deployed successfully! Reloading status...");
      await fetchIssuesList(true);
    } catch (error) {
      console.error("Fix deployment pipeline error:", error);
      alert("Failed to apply source alterations automatically.");
    } finally {
      setFixing(false);
    }
  };

  const hasRealIssues = issues.length > 0 && !(issues.length === 1 && (issues[0].test_id === "SECURE" || issues[0].id === "clean-workspace-status"));

  return (
    <div className="space-y-6">
      {/* Updated Header Layout */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center bg-slate-900 p-6 rounded-xl border border-slate-800 gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <FaShieldAlt className="text-red-500" /> Validation Hub
            </h2>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Workspace Scope: <span className="text-cyan-400">{projectPath}</span>
            </p>
          </div>
        </div>

        {hasRealIssues && (
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleApplyFixes}
              disabled={fixing}
              className="flex items-center gap-2 bg-linear-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white text-sm font-medium px-5 py-3 rounded-xl transition shadow-lg shadow-emerald-500/20 disabled:opacity-50 cursor-pointer"
            >
              {fixing ? <FaSpinner className="animate-spin" /> : <FaWrench />} Auto-Fix All Flaws
            </button>
          </div>
        )}
      </div>

      {/* Issues Render Pipeline */}
      <div className="space-y-4">
        {loading ? (
          <p className="text-center p-10 font-mono text-slate-400 animate-pulse">Parsing target vulnerability vectors...</p>
        ) : issues.length > 0 ? (
          issues.map((issue, idx) => {
            const isSecureStatus = issue.test_id === "SECURE" || issue.id === "clean-workspace-status";
            
            if (isSecureStatus) {
              return (
                <div key={idx} className="bg-slate-900/40 border border-green-500/30 rounded-xl p-10 text-center space-y-2">
                  <FaCheckCircle className="text-emerald-400 text-5xl mx-auto mb-2 shadow-green-500" />
                  <p className="text-lg font-bold text-slate-200">System Validated & Secure</p>
                  <p className="text-sm text-slate-400 font-mono">No vulnerabilities require patching in the targeted workspace scope.</p>
                </div>
              );
            }

            const rule = issue.rule || issue.test_id || "";

            return (
              <div key={idx} className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-4 hover:border-red-500/30 transition">
                <div className="flex items-start gap-4 w-full">
                  <FaTimesCircle className="text-red-500 text-xl mt-1 shrink-0" />
                  <div className="space-y-1 w-full">
                    <div className="flex justify-between items-start md:items-center flex-col md:flex-row gap-2">
                      <h4 className="font-bold text-slate-200 text-base leading-snug">
                        {issue.issue_text || issue.message || issue.title || "Vulnerability Vector Discovered"}
                      </h4>
                      
                      {/* 🎯 FIXED: Tool Name & Rule ID now placed side-by-side using space-x/flex-row */}
                      <div className="flex items-center gap-2 shrink-0 flex-wrap">
                        {/* Tool Name Badge */}
                        <span className="bg-purple-900/20 text-purple-300 text-xs px-2 py-1 rounded uppercase font-bold tracking-wider">
                          {rule.startsWith("B")
                            ? "Bandit"
                            : rule.startsWith("F")
                            ? "Ruff"
                            : "Semgrep"}
                        </span>

                        {/* Rule Code Badge */}
                        <span className="bg-slate-800 text-cyan-400 text-xs px-2 py-1 rounded font-mono">
                          {rule || "UNKNOWN"}
                        </span>
                      </div>
                    </div>

                    {/* Meta Location Box */}
                    <p className="text-xs font-mono text-slate-400 bg-slate-950/50 inline-block px-2 py-1 rounded mt-1 border border-slate-800/50">
                      Location: <span className="text-cyan-400">{issue.filename || issue.file || "Unknown File"}</span> | Line <span className="text-yellow-400">{issue.line_number || issue.line || "N/A"}</span>
                    </p>

                    {issue.code && (
                      <pre className="bg-black/40 text-slate-300 p-3 rounded-lg text-xs font-mono mt-3 overflow-x-auto border border-slate-800">
                        {issue.code}
                      </pre>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-10 text-center space-y-2">
            <FaCheckCircle className="text-emerald-400 text-4xl mx-auto" />
            <p className="text-base font-medium">Clean Audit Workspace Status!</p>
            <p className="text-xs text-slate-500 font-mono">
              No vulnerabilities found in this directory.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}