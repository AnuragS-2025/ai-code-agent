import { useState, useEffect } from "react";
import { FaBug, FaSpinner, FaFolderOpen, FaExclamationCircle, FaCheckCircle, FaShieldAlt, FaBrain } from "react-icons/fa";
import { getIssues, askAIExplanation } from "../services/api";

export default function IssueExplorer({ projectPath = "." }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);

  // AI Insights States
  const [explanations, setExplanations] = useState({});
  const [explainingId, setExplainingId] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function fetchAllIssues() {
      try {
        setLoading(true);
        
        // Convert backslashes safely
        const safePath = projectPath.replace(/\\/g, "/");

        const data = await getIssues({ project_path: safePath }, true);
        if (isMounted) {
          setIssues(Array.isArray(data) ? data : data?.issues || []);
        }
      } catch (err) {
        console.error("Failed to load issues:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchAllIssues();
    return () => { isMounted = false; };
  }, [projectPath]);

  // Handle Ask AI triggering
  const handleExplainAI = async (idx, issue) => {
    if (explanations[idx]) {
      const newExps = { ...explanations };
      delete newExps[idx];
      setExplanations(newExps);
      return;
    }

    setExplainingId(idx);
    try {
      const payload = {
        rule: issue.rule || issue.test_id || "Unknown",
        message: issue.message || issue.issue_text || "",
        file: issue.file || issue.filename || "",
        line: Number(issue.line || issue.line_number || 0),
      };
      
      const response = await askAIExplanation(payload);
      const data = response.data;
      
      setExplanations(prev => ({
        ...prev,
        [idx]: `${data.explanation}

Recommendation:${data.recommendation}

Example:${data.example_fix}`
      }));
    } catch (error) {
      console.error("AI Explanation Error:", error);
      console.error(error.response?.data);

      alert(
        error.response?.data?.detail ||
        error.message ||
        "Failed to connect to AI Explanation engine."
      );
    } finally {
      setExplainingId(null);
    }
  };

  return (
    <div className="space-y-6 text-white">
      <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <FaBug className="text-red-500" /> Global Issue Explorer
        </h2>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Workspace Scope: <span className="text-cyan-400">{projectPath}</span>
        </p>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
        {loading ? (
          <div className="text-center py-12 font-mono text-slate-400 flex flex-col items-center gap-3">
            <FaSpinner className="animate-spin text-3xl text-cyan-500" />
            <p>Decoding system vulnerabilities...</p>
          </div>
        ) : issues.length > 0 ? (
          <div className="grid gap-4">
            {issues.map((issue, idx) => {
              const isSecureStatus = issue.test_id === "SECURE" || issue.id === "clean-workspace-status";

              if (isSecureStatus) {
                return (
                  <div key={idx} className="bg-green-900/20 border border-green-500/50 rounded-lg p-6 flex gap-4 items-center">
                    <FaCheckCircle className="text-green-400 text-3xl shrink-0" />
                    <div>
                      <h3 className="font-bold text-green-400 text-lg">System Secure</h3>
                      <p className="text-sm text-slate-300 mt-1">{issue.issue_text}</p>
                    </div>
                  </div>
                );
              }

              const severity =
                issue.issue_severity ||
                issue.severity ||
                (
                  issue.rule === "B602" ? "HIGH" :
                  issue.rule === "B404" ? "LOW" :
                  issue.rule?.startsWith("F") ? "LOW" :
                  "LOW"
                );

              const severityColor =
                severity === "HIGH"
                  ? "text-red-500 border-red-500/30 bg-red-500/10"
                  : severity === "MEDIUM"
                  ? "text-yellow-500 border-yellow-500/30 bg-yellow-500/10"
                  : "text-blue-400 border-blue-400/30 bg-blue-400/10";

              return (
                <div key={idx} className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex flex-col gap-4 hover:border-red-500/30 transition">
                  <div className="flex items-start gap-4 w-full">
                    <FaExclamationCircle className={`text-xl shrink-0 mt-1 ${severity === "HIGH" ? "text-red-500" : "text-yellow-500"}`} />
                    
                    <div className="space-y-1 w-full">
                      {/* Main Split Body */}
                      <div className="flex justify-between items-start gap-4 w-full">
                        
                        {/* LEFT SIDE: Title + Ask AI Button inline */}
                        <div className="space-y-2 flex-1">
                          <div className="flex flex-wrap items-center gap-3">
                            <h4 className="font-bold text-slate-200 text-base leading-snug">
                              {issue.message || issue.issue_text || issue.title || "Unknown Issue"}
                            </h4>
                            
                            <button 
                              onClick={() => handleExplainAI(idx, issue)}
                              disabled={explainingId === idx}
                              className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider font-bold text-purple-400 hover:text-purple-300 bg-purple-900/20 px-2 py-1 rounded border border-purple-800/40 transition cursor-pointer disabled:opacity-50 shrink-0"
                            >
                              {explainingId === idx ? <FaSpinner className="animate-spin" /> : <FaBrain />} 
                              {explanations[idx] ? "Hide Details" : "Ask AI"}
                            </button>
                          </div>

                          {/* Location Box */}
                          <p className="text-xs font-mono text-slate-400 bg-slate-950/50 inline-block px-2 py-1 rounded border border-slate-800/50">
                            Location: <span className="text-cyan-400">{issue.filename || issue.file || "Unknown"}</span> | Line <span className="text-yellow-400">{issue.line_number || issue.line || "N/A"}</span>
                          </p>
                        </div>

                        {/* RIGHT SIDE: Custom Hierarchy Stacking */}
                        <div className="flex flex-col items-end gap-2 shrink-0">
                          
                          {/* 🎯 Row 1: Severity (LOW) and Scanner (Bandit/Ruff) side-by-side */}
                          <div className="flex items-center gap-2">
                            <span className={`text-xs font-mono px-2.5 py-1 rounded border uppercase ${severityColor}`}>
                              {severity}
                            </span>

                            <span className="bg-purple-900/20 text-purple-300 text-xs px-2 py-1 rounded uppercase font-bold tracking-wider">
                              {(() => {
                                const ruleId = issue.rule || issue.test_id || "";
                                if (ruleId.startsWith("B")) return "Bandit";
                                if (ruleId.startsWith("F")) return "Ruff";
                                return "Semgrep";
                              })()}
                            </span>
                          </div>
                          
                          {/* 🎯 Row 2: Rule Badge directly underneath them */}
                          <span className="bg-slate-800 text-cyan-400 text-xs px-2 py-1 rounded font-mono flex items-center gap-1">
                            <FaShieldAlt className="text-[10px]" /> {issue.test_id || issue.rule || "RULE"}
                          </span>

                        </div>

                      </div>

                      {/* AI Explanation Insights */}
                      {explanations[idx] && (
                        <div className="mt-4 bg-purple-950/40 border-l-2 border-purple-500 p-3 rounded-r-lg shadow-inner">
                          <p className="text-xs text-purple-200 leading-relaxed whitespace-pre-wrap">
                            <strong className="text-purple-400 text-sm block mb-1">🤖 AI Engine Insight:</strong> 
                            {explanations[idx]}
                          </p>
                        </div>
                      )}

                      {/* Code Snippet */}
                      {issue.code && (
                        <pre className="bg-black/40 text-slate-300 p-3 rounded-lg text-xs font-mono mt-3 overflow-x-auto border border-slate-800">
                          {issue.code}
                        </pre>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-16 text-slate-500 space-y-3">
            <FaFolderOpen className="text-5xl mx-auto text-slate-700" />
            <p className="font-mono text-sm">No vulnerabilities found in this directory.</p>
          </div>
        )}
      </div>
    </div>
  );
}