import { FaCheckCircle, FaTimesCircle, FaFolderOpen } from "react-icons/fa";

export default function RecentScans({ scans = [] }) {
  // 🎯 FIX: Completely safe array extraction for structural changes
  const validScans = Array.isArray(scans) 
    ? scans 
    : (Array.isArray(scans?.data) ? scans.data : []);

  return (
    <div className="bg-slate-900 rounded-xl p-6 mt-8 border border-slate-800 overflow-hidden flex flex-col">
      <h2 className="text-xl font-bold mb-6 text-slate-200">Recent Scan History</h2>

      <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        <table className="w-full text-left border-collapse min-w-150">
          <thead>
            <tr className="text-slate-400 border-b border-slate-800 text-xs uppercase tracking-wider font-mono">
              <th className="py-3 px-4">Target Project</th>
              <th className="py-3 px-4">Files Scanned</th>
              <th className="py-3 px-4">Issues Found</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Timestamp</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800/40 text-sm">
            {validScans.length === 0 ? (
              <tr>
                <td colSpan="5" className="text-center py-12 text-slate-500">
                  <div className="flex flex-col items-center justify-center gap-3">
                    <FaFolderOpen className="text-4xl text-slate-800" />
                    <span className="font-mono text-xs text-slate-500">
                      No historical scan artifacts available in runtime logs.
                    </span>
                  </div>
                </td>
              </tr>
            ) : (
              validScans.map((scan, index) => {
                // Safely trace total vulnerabilities across varying Pydantic structures
                const issuesCount = scan?.vulnerabilities_count ?? scan?.issues ?? scan?.total_issues ?? 0;
                const isPassed = issuesCount === 0;
                
                // Fallback statuses
                const displayStatus = scan?.status || (isPassed ? "Secure" : "Vulnerable");

                // Extrapolate and clean target directory naming conversions
                const rawProject = scan?.project_path || scan?.project || scan?.project_name || "Root Workspace";
                const cleanProjectName = rawProject.includes("\\") || rawProject.includes("/")
                  ? rawProject.split(/[\\/]/).filter(Boolean).pop()
                  : rawProject;

                return (
                  <tr
                    key={scan?.id || `scan-matrix-${index}`}
                    className="hover:bg-slate-800/30 transition-colors group"
                  >
                    <td className="py-4 px-4 font-mono font-medium text-cyan-400 max-w-50 truncate" title={rawProject}>
                      {cleanProjectName === "." ? "Root-Workspace" : cleanProjectName}
                    </td>
                    
                    <td className="py-4 px-4 text-slate-300 font-mono">
                      {scan?.files ?? scan?.total_files ?? scan?.total_scanned_files ?? "System"}
                    </td>
                    
                    <td className="py-4 px-4">
                      <span className={`font-mono font-bold ${issuesCount > 0 ? "text-red-400" : "text-emerald-400"}`}>
                        {issuesCount}
                      </span>
                    </td>
                    
                    <td className="py-4 px-4">
                      <span
                        className={`px-2.5 py-1 rounded flex items-center w-max gap-1.5 text-xs font-bold uppercase tracking-wider font-mono border ${
                          isPassed
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/25"
                            : "bg-red-500/10 text-red-400 border-red-500/25"
                        }`}
                      >
                        {isPassed ? <FaCheckCircle className="text-emerald-400" /> : <FaTimesCircle className="text-red-400" />}
                        {displayStatus}
                      </span>
                    </td>
                    
                    <td className="py-4 px-4 text-slate-400 text-xs font-mono whitespace-nowrap">
                      {scan?.timestamp || scan?.date || scan?.created_at || "Just now"}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}