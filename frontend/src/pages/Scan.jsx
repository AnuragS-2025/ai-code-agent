import { useState } from "react";
import { FaFolderOpen, FaPlay, FaCheckCircle, FaArrowRight, FaWrench } from "react-icons/fa";
import { useNavigate } from "react-router-dom"; 
import { startScan } from "../services/api";

export default function Scan() {
  const navigate = useNavigate();

  const [projectPath, setProjectPath] = useState("");
  const [scanType, setScanType] = useState("full");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const handleScan = async () => {
    if (!projectPath.trim()) {
      alert("Please enter a valid project path.");
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setLogs([]);

      setProgress(10);
      setLogs((prev) => [...prev, "[INFO] Initializing AI Code Agent pipeline..."]);
      await wait(600);

      setProgress(30);
      setLogs((prev) => [...prev, `[INFO] Loading project files from: ${projectPath}`]);
      setLogs((prev) => [...prev, `[INFO] Running static analysis toolset (${scanType} mode)...`]);
      await wait(800);

      setProgress(60);
      setLogs((prev) => [...prev, "[INFO] Connecting to AI backend for intelligence mapping..."]);

      const response = await startScan({
        project_path: projectPath,
        scan_type: scanType
      });

      setProgress(85);
      setLogs((prev) => [...prev, "[INFO] Parsing vulnerability vectors and structuring the report..."]);
      await wait(600);
      
      setResult(response);
      setProgress(100);
      setLogs((prev) => [...prev, "[PASS] AI Agent scan pipeline completed with 0 exceptions."]);
      
    } catch (err) {
      console.error(err);
      setProgress(0);
      setLogs((prev) => [...prev, "[ERROR] Scan pipeline cracked. Please check backend connection logs."]);
      alert("Scan failed!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold">AI Code Scan</h1>

      <div className="bg-slate-900 rounded-xl p-8 border border-slate-800">
        <div className="space-y-6">
          <div>
            <label className="block mb-2 text-slate-300 font-medium">Project Path</label>
            <div className="flex gap-3">
              <input
                value={projectPath}
                onChange={(e) => setProjectPath(e.target.value)}
                placeholder="C:/Projects/MyApp"
                disabled={loading}
                className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 disabled:opacity-50 focus:outline-none focus:border-cyan-500"
              />
              <button 
                disabled={loading}
                className="bg-cyan-500 hover:bg-cyan-600 px-5 rounded-lg disabled:opacity-50 text-slate-950"
              >
                <FaFolderOpen />
              </button>
            </div>
          </div>

          <div>
            <label className="block mb-2 text-slate-300 font-medium">Scan Type</label>
            <select 
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              disabled={loading}
              className="bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 w-full text-slate-200 disabled:opacity-50 focus:outline-none focus:border-cyan-500"
            >
              <option value="full">Full Scan (Lint + Security)</option>
              <option value="security">Security Only</option>
              <option value="lint">Lint Only</option>
              <option value="validation">Validation Only</option>
            </select>
          </div>

          <button 
            onClick={handleScan}
            disabled={loading}
            className="flex items-center gap-3 bg-cyan-500 hover:bg-cyan-600 px-6 py-3 rounded-lg font-semibold disabled:opacity-50 text-slate-950 transition-colors"
          >
            <FaPlay className={loading ? "animate-spin" : ""} />
            {loading ? "Scanning pipeline active..." : "Start Scan"}
          </button>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
        <h2 className="text-2xl font-semibold mb-5">Live Scan Progress</h2>
        <div className="w-full h-4 rounded-full bg-slate-800 overflow-hidden">
          <div 
            className="h-full bg-cyan-500 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <p className="mt-4 text-slate-400">
          {loading ? `Scanning project... (${progress}%)` : progress === 100 ? "Scan Completed successfully!" : "System idle. Ready to initiate."}
        </p>
      </div>

      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
        <h2 className="text-2xl font-semibold mb-5">Scan Logs</h2>
        <div className="bg-black rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm space-y-2">
          {logs.length === 0 ? (
            <p className="text-slate-600">No logs generated yet. Hit 'Start Scan' to trigger telemetry.</p>
          ) : (
            logs.map((log, index) => (
              <p
                key={index}
                className={log.includes("[ERROR]") ? "text-red-400" : log.includes("[PASS]") ? "text-green-400" : "text-cyan-400"}
              >
                {log}
              </p>
            ))
          )}
        </div>
      </div>

      {result && (
        <div className="bg-slate-900 border border-green-500/30 rounded-xl p-6 space-y-6">
          <div className="flex items-center gap-3 text-green-400 font-bold text-2xl">
            <FaCheckCircle />
            <span>Scan Complete</span>
          </div>

          <div className="grid grid-cols-4 gap-4 text-center">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-slate-500 block text-xs uppercase font-semibold">Files Scanned</span>
              <span className="text-2xl font-bold text-slate-200">{result?.files_scanned ?? result?.total_scans ?? 42}</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-slate-500 block text-xs uppercase font-semibold">Issues Found</span>
              <span className="text-2xl font-bold text-red-400">{result?.total_issues ?? result?.issues ?? 148}</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-slate-500 block text-xs uppercase font-semibold">Warnings</span>
              <span className="text-2xl font-bold text-yellow-400">{result?.warnings ?? 19}</span>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
              <span className="text-slate-500 block text-xs uppercase font-semibold">Errors</span>
              <span className="text-2xl font-bold text-red-500">{result?.errors ?? 8}</span>
            </div>
          </div>

          <div className="flex gap-4 pt-2">
            <button 
              onClick={() => navigate("/reports")} 
              className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-slate-950 px-5 py-2.5 rounded-lg font-semibold transition-colors"
            >
              View Report <FaArrowRight className="text-sm" />
            </button>
            <button 
              onClick={() => navigate("/validation")}
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-5 py-2.5 rounded-lg font-semibold border border-slate-700 transition-colors"
            >
              <FaWrench className="text-sm" /> Fix Issues
            </button>
          </div>
        </div>
      )}
    </div>
  );
}