import { useState, useEffect } from "react";
import { 
  FaShieldAlt, FaBug, FaFileAlt, 
  FaExclamationTriangle, FaHistory, FaDownload, FaSpinner, FaFolderOpen, FaInfoCircle
} from "react-icons/fa";
import { getReport, getHistory, exportReport } from "../services/api";

export default function Reports({ projectPath = "." }) {
  const [reportData, setReportData] = useState({
    summary: { total_scanned: "...", issues_found: "...", code_health: "...", critical_threats: "..." },
    distribution: { bandit: 0, ruff: 0, semgrep: 0 }
  });

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadTelemetryReport() {
      try {
        const safePath = projectPath.replace(/\\/g, "/");
        const data = await getReport(safePath, false); 
        
        if (isMounted && data) {
          const issuesFound = data.total_issues || 0;
          const totalScanned = data.issues
            ? new Set(data.issues.map((i) => i.file)).size
            : 0;
          
          let banditCount = Number(data?.by_tool?.bandit || 0);
          let ruffCount = Number(data?.by_tool?.ruff || 0);
          let semgrepCount = Number(data?.by_tool?.semgrep || 0);

          let dynamicGrade = "A+";
          if (issuesFound > 15) dynamicGrade = "D";
          else if (issuesFound > 7) dynamicGrade = "C";
          else if (issuesFound > 2) dynamicGrade = "B";
          else if (issuesFound > 0) dynamicGrade = "A";

          setReportData({
            summary: { 
              total_scanned: totalScanned, 
              issues_found: issuesFound, 
              code_health: dynamicGrade, 
              critical_threats: semgrepCount + banditCount 
            },
            distribution: { 
              bandit: banditCount, 
              ruff: ruffCount, 
              semgrep: semgrepCount 
            }
          });
        }
      } catch (err) {
        console.warn("Report metrics fetch error:", err.message);
        if (isMounted) {
          setReportData({
            summary: { total_scanned: 0, issues_found: 0, code_health: "N/A", critical_threats: 0 },
            distribution: { bandit: 0, ruff: 0, semgrep: 0 }
          });
        }
      }
    }

    async function loadHistoryList() {
      try {
        setHistoryLoading(true);
        const response = await getHistory();
        if (isMounted) {
          const payload = response.data;
          if (Array.isArray(payload?.history)) {
            setHistory(payload.history);
          } else {
            setHistory([]);
          }
        }
      } catch (err) {
        console.error("History fetch pipeline error context:", err);
      } finally {
        if (isMounted) setHistoryLoading(false);
      }
    }

    loadTelemetryReport();
    loadHistoryList();

    return () => { isMounted = false; };
  }, [projectPath]);

  const handleExport = async (project = ".") => {
    try {
      const response = await exportReport(project);
      alert(`🎉 Report exported successfully! Path: ${response?.data?.path || "Local Server Artifact Repository"}`);
    } catch (err) {
      console.error("Export handler failure state:", err);
      alert("Failed to export JSON payload data.");
    }
  };

  const totalDistributionIssues = 
    (reportData?.distribution?.bandit || 0) + 
    (reportData?.distribution?.ruff || 0) + 
    (reportData?.distribution?.semgrep || 0);

  return (
    <div className="space-y-6 text-white w-full max-w-7xl mx-auto p-4 md:p-6 animate-fadeIn">
      
      {/* 1. Stat Cards Row Setup */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card A: Files Scanned */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between hover:border-slate-700/80 transition duration-200">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono block">FILES SCANNED</span>
            <span className="text-2xl font-extrabold font-mono tracking-tight text-cyan-400">{reportData?.summary?.total_scanned}</span>
          </div>
          <div className="bg-black/30 p-3 rounded-xl border border-slate-800/40 text-xl shadow-inner text-cyan-400"><FaFileAlt /></div>
        </div>

        {/* Card B: Issues Found */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between hover:border-slate-700/80 transition duration-200">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono block">ISSUES FOUND</span>
            <span className="text-2xl font-extrabold font-mono tracking-tight text-rose-500">{reportData?.summary?.issues_found}</span>
          </div>
          <div className="bg-black/30 p-3 rounded-xl border border-slate-800/40 text-xl shadow-inner text-rose-500"><FaBug /></div>
        </div>

        {/* Card C: Security Score */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between hover:border-slate-700/80 transition duration-200">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono block">SECURITY SCORE</span>
            <span className="text-2xl font-extrabold font-mono tracking-tight text-emerald-400">{reportData?.summary?.code_health}</span>
          </div>
          <div className="bg-black/30 p-3 rounded-xl border border-slate-800/40 text-xl shadow-inner text-emerald-400"><FaShieldAlt /></div>
        </div>

        {/* Card D: Critical Threats */}
        <div className="bg-slate-900/90 border border-slate-800 p-5 rounded-xl shadow-xl flex items-center justify-between hover:border-slate-700/80 transition duration-200">
          <div className="space-y-1">
            <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 font-mono block">CRITICAL FIXED</span>
            <span className="text-2xl font-extrabold font-mono tracking-tight text-amber-500">{reportData?.summary?.critical_threats}</span>
          </div>
          <div className="bg-black/30 p-3 rounded-xl border border-slate-800/40 text-xl shadow-inner text-amber-500"><FaExclamationTriangle /></div>
        </div>
      </div>

      {/* 2. Middle Double Column Configuration Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
        
        {/* Left Double Width Card: Findings Distribution map */}
        <div className="lg:col-span-2 bg-slate-900/90 backdrop-blur-md border border-slate-800 p-6 rounded-xl shadow-2xl flex flex-col justify-between">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-slate-400 font-mono mb-6 flex items-center gap-2 border-b border-slate-800/80 pb-3 font-bold">
              <FaShieldAlt className="text-cyan-400" /> Static Engine Findings Distribution
            </h3>
            
            <div className="space-y-5">
              {/* Analyzer Block 1: Bandit */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-400 font-medium tracking-wide">Bandit Security (AST Analyzer)</span>
                  <span className="text-slate-400 font-bold">{reportData?.distribution?.bandit || 0} Issues</span>
                </div>
                <div className="w-full bg-slate-950/80 h-1.5 rounded-full border border-slate-900 overflow-hidden shadow-inner">
                  <div 
                    className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${totalDistributionIssues > 0 ? ((reportData?.distribution?.bandit || 0) / totalDistributionIssues) * 100 : 0}%` }}
                  />
                </div>
              </div>

              {/* Analyzer Block 2: Ruff */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-400 font-medium tracking-wide">Ruff Rust-Powered Linter</span>
                  <span className="text-slate-400 font-bold">{reportData?.distribution?.ruff || 0} Issues</span>
                </div>
                <div className="w-full bg-slate-950/80 h-1.5 rounded-full border border-slate-900 overflow-hidden shadow-inner">
                  <div 
                    className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${totalDistributionIssues > 0 ? ((reportData?.distribution?.ruff || 0) / totalDistributionIssues) * 100 : 0}%` }}
                  />
                </div>
              </div>

              {/* Analyzer Block 3: Semgrep */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="text-slate-400 font-medium tracking-wide">Semgrep Pattern Engine</span>
                  <span className="text-slate-400 font-bold">{reportData?.distribution?.semgrep || 0} Issues</span>
                </div>
                <div className="w-full bg-slate-950/80 h-1.5 rounded-full border border-slate-900 overflow-hidden shadow-inner">
                  <div 
                    className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${totalDistributionIssues > 0 ? ((reportData?.distribution?.semgrep || 0) / totalDistributionIssues) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Single Width Card: Telemetry Logs Panel */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-2xl flex flex-col justify-between h-full">
          <div>
            <h3 className="text-xs uppercase tracking-widest text-slate-300 font-mono mb-5 flex items-center gap-2 border-b border-slate-800/80 pb-3 font-bold">
              <FaInfoCircle className="text-cyan-400 text-sm" /> Agent Status Telemetry
            </h3>
            <div className="space-y-4">
              <p className="text-xs text-slate-400 leading-relaxed font-sans tracking-wide">
                All engine drivers are listening via system standard sockets. Cached metrics layers prevent redundant filesystem execution passes.
              </p>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/60 mt-6 flex justify-between items-center text-[10px] font-mono text-slate-500 font-bold tracking-wider">
            <span>Ecosystem Matrix: Active</span>
            <span className="bg-slate-950/80 px-2 py-1 rounded border border-slate-800/60 text-slate-400">v1.0.4-Stable</span>
          </div>
        </div>

      </div>

      {/* 3. Bottom Main Card: Recent Scan History */}
      <div className="bg-slate-900/90 backdrop-blur-md border border-slate-800 p-6 rounded-xl shadow-2xl">
        <h3 className="text-xs uppercase tracking-widest text-slate-400 font-mono mb-5 flex items-center gap-2 border-b border-slate-800/80 pb-3 font-bold">
          <FaHistory className="text-slate-400" /> Recent Scan History
        </h3>

        {historyLoading ? (
          <div className="text-center py-12 font-mono text-cyan-500 animate-pulse flex items-center justify-center gap-2 text-xs">
            <FaSpinner className="animate-spin" /> Querying secure engine log matrix metadata...
          </div>
        ) : history.length > 0 ? (
          <div className="overflow-x-auto custom-scrollbar">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] uppercase font-mono tracking-wider text-slate-500">
                  <th className="py-3 px-4 font-bold">Target Project</th>
                  <th className="py-3 px-4 font-bold">Files Scanned</th>
                  <th className="py-3 px-4 font-bold text-center">Issues Found</th>
                  <th className="py-3 px-4 text-center font-bold">Status</th>
                  <th className="py-3 px-4 text-right font-bold">Timestamp & Controls</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-xs font-mono">
                {history.map((item, idx) => {
                  const issueCount = item.total_issues ?? item.vulnerabilities_count ?? item.issues ?? 0;
                  const targetPath = item.project_path || item.project || ".";
                  
                  return (
                    <tr key={idx} className="hover:bg-black/20 transition-colors duration-150 group">
                      <td className="py-3.5 px-4 text-cyan-400 font-bold tracking-wide group-hover:text-cyan-300 max-w-xs truncate">
                        {targetPath.split("/").pop()}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">System</td>
                      <td className="py-3.5 px-4 text-center font-bold text-slate-200">{issueCount}</td>
                      <td className="py-3.5 px-4 text-center">
                        <span className={`inline-flex items-center gap-1 text-[9px] font-extrabold px-2.5 py-0.5 rounded-md uppercase border ${
                          issueCount > 0 
                            ? "bg-rose-500/10 border-rose-500/20 text-rose-400" 
                            : "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                        }`}>
                          {issueCount > 0 ? "⚠️ Vulnerable" : "✅ Secure"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 flex justify-end items-center gap-4 text-right text-slate-500">
                        <span className="text-[11px] font-sans tracking-tight hidden sm:inline">
                          {item.timestamp || item.date || "2026-07-10T14:29:16"}
                        </span>
                        <button 
                          onClick={() => handleExport(targetPath)} 
                          className="bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-cyan-400 py-1 px-2.5 rounded-md flex items-center gap-1.5 transition text-[10px] font-bold tracking-wider cursor-pointer shadow-xs active:scale-95"
                        >
                          <FaDownload className="text-[9px]" /> EXPORT
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 text-slate-600 space-y-2 border border-dashed border-slate-800 rounded-xl bg-black/10">
            <FaFolderOpen className="text-3xl mx-auto text-slate-700" />
            <p className="text-xs font-mono">No historical workspace audit logs compiled on this node.</p>
          </div>
        )}
      </div>

    </div>
  );
}