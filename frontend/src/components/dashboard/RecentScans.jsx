export default function RecentScans({ scans = [] }) {
  return (
    <div className="bg-slate-900 rounded-xl p-6 mt-8 border border-slate-800">
      <h2 className="text-2xl font-semibold mb-6">Recent Scans</h2>

      <table className="w-full">
        <thead>
          <tr className="text-slate-400 border-b border-slate-700 text-sm">
            <th className="text-left py-3">Project</th>
            <th className="text-left">Files</th>
            <th className="text-left">Issues</th>
            <th className="text-left">Status</th>
            <th className="text-left">Date</th>
          </tr>
        </thead>

        <tbody>
          {scans.length === 0 ? (
            <tr>
              <td colSpan="5" className="text-center py-8 text-slate-500">
                No recent scans found.
              </td>
            </tr>
          ) : (
            scans.map((scan, index) => {
              // Backend strings ko check karke safe color extraction
              const currentStatus = (scan.status || "Passed").toLowerCase();
              const isPassed = currentStatus === "passed" || currentStatus === "success";

              return (
                <tr
                  key={scan.id || index}
                  className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors"
                >
                  <td className="py-4 font-medium text-slate-200">
                    {scan.project || scan.project_name || "App-Repo"}
                  </td>
                  <td className="text-slate-300">
                    {scan.files ?? scan.total_files ?? 120}
                  </td>
                  <td className="text-slate-300">
                    {scan.issues ?? scan.total_issues ?? 0}
                  </td>
                  <td>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        isPassed
                          ? "bg-green-500/10 text-green-400 border border-green-500/20"
                          : "bg-red-500/10 text-red-400 border border-red-500/20"
                      }`}
                    >
                      {scan.status || "Passed"}
                    </span>
                  </td>
                  <td className="text-slate-400 text-sm">
                    {scan.date || scan.created_at || "Just now"}
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}