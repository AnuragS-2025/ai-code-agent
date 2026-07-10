import { useEffect, useMemo, useState, useCallback } from "react";
import {
  FaFolderOpen,
  FaBug,
  FaShieldAlt,
  FaCheckCircle,
  FaCloudUploadAlt,
  FaUndo,
  FaSave,
  FaHistory,
  FaSpinner,
} from "react-icons/fa";

import StatCard from "../components/dashboard/StatCard";
import Analytics from "../components/dashboard/Analytics";
import api from "../services/api";

export default function Dashboard({
  projectPath = ".",
  setProjectPath,
}) {
  const [dashboard, setDashboard] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const [isBackingUp, setIsBackingUp] = useState(false);
  const [isRollingBack, setIsRollingBack] = useState(false);

  // ==========================================
  // Dashboard Data Loader & Formatter
  // ==========================================

  const loadDashboard = useCallback(async (path = projectPath) => {
    const safePath = path ? path.replace(/\\/g, "/") : ".";

    try {
      const [dashboardRes, historyRes] = await Promise.all([
        api.get("/dashboard", {
          params: { project_path: safePath },
        }),
        api.get("/history"),
      ]);

      setDashboard(dashboardRes.data);

      const payload = historyRes.data;
      let rawHistory = [];

      if (Array.isArray(payload)) {
        rawHistory = payload;
      } else if (Array.isArray(payload?.history)) {
        rawHistory = payload.history;
      } else if (Array.isArray(payload?.recent_scans)) {
        rawHistory = payload.recent_scans;
      } else if (Array.isArray(payload?.scans)) {
        rawHistory = payload.scans;
      } else if (Array.isArray(payload?.data)) {
        rawHistory = payload.data;
      }

      // Format records dynamically to fix "System" string and return pure numbers
      const formattedHistory = rawHistory.map((scan) => {
        const fallbackProject = safePath !== "." ? safePath.split("/").pop() : "Root";
        
        // Pure number string fallback mechanism
        let cleanFilesCount = "1"; 
        if (scan.files_scanned && scan.files_scanned !== "System") {
          cleanFilesCount = String(scan.files_scanned).replace(/[^0-9]/g, "");
        } else if (dashboardRes.data?.summary?.total_scans) {
          cleanFilesCount = String(dashboardRes.data.summary.total_scans);
        }

        return {
          ...scan,
          files_scanned: cleanFilesCount || "1", // 🎯 FIXED: Sirf pure numbers dikhenge, "Files" nahi string se
          target_project: 
            scan.target_project === "System" || !scan.target_project
              ? fallbackProject
              : scan.target_project
        };
      });

      setHistory(formattedHistory);
    } catch (err) {
      console.error("Dashboard metric parser mapping error:", err);
    }
  }, [projectPath]);

  // ==========================================
  // Initial Load Trigger
  // ==========================================

  useEffect(() => {
    let mounted = true;

    async function init() {
      setLoading(true);
      try {
        if (mounted) {
          await loadDashboard();
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    init();

    return () => {
      mounted = false;
    };
  }, [loadDashboard]);

  // ==========================================
  // Dashboard Summary Metrics
  // ==========================================

  const summary = useMemo(() => {
    return {
      total_scans: dashboard?.summary?.total_scans ?? 0,
      total_issues: dashboard?.summary?.total_issues ?? 0,
      security_score: dashboard?.summary?.security_score ?? "A+",
      total_fixed: dashboard?.summary?.total_fixed ?? 0,
    };
  }, [dashboard]);

  const topRules = useMemo(() => {
    return (
      dashboard?.top_rules || {
        bandit: 0,
        ruff: 0,
        semgrep: 0,
      }
    );
  }, [dashboard]);

  // ==========================================
  // ZIP Upload Action
  // ==========================================

  const handleZipUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);

      const response = await api.post("/upload/zip", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = response.data;
      if (!data.success || !data.extract_path) {
        alert("❌ ZIP extraction failed.");
        return;
      }

      const extractedPath = data.extract_path.replace(/\\/g, "/");
      alert("✅ Project uploaded successfully.");
      setProjectPath(extractedPath);

    } catch (err) {
      console.error("Upload Error:", err);
      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  // ==========================================
  // Git Operations Pipeline
  // ==========================================

  const handleBackup = async () => {
    try {
      setIsBackingUp(true);
      const safePath = projectPath ? projectPath.replace(/\\/g, "/") : ".";
      await api.post("/git/backup", null, { params: { project_path: safePath } });
      alert("✅ Git backup created.");
    } catch (err) {
      console.error(err);
      alert("Backup failed.");
    } finally {
      setIsBackingUp(false);
    }
  };

  const handleRollback = async () => {
    if (!window.confirm("⚠️ Revert all project changes?")) return;

    try {
      setIsRollingBack(true);
      const safePath = projectPath ? projectPath.replace(/\\/g, "/") : ".";
      await api.post("/git/rollback", null, { params: { project_path: safePath } });
      alert("✅ Rollback completed.");

      setLoading(true);
      await loadDashboard(projectPath);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Rollback failed.");
    } finally {
      setIsRollingBack(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-cyan-400 font-mono">
        <FaSpinner className="animate-spin text-4xl" />
        <p>Syncing Workspace...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 text-white">
      
      {/* 🎯 FIXED: Header Container with accurate vertical midline flex alignment */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800/60 pb-6 mb-6 gap-4">
        
        {/* Left Side: Title & Project Context */}
        <div className="space-y-1">
          <h1 className="text-4xl font-extrabold tracking-tight bg-linear-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-slate-500">Active Project :</span>
            <span className="text-cyan-400 font-bold bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-900/50">
              {projectPath}
            </span>
          </div>
        </div>

        {/* Right Side: Aligned Interactive Actions */}
        <div className="flex items-center gap-3 self-end md:self-center">
          <button
            onClick={handleBackup}
            disabled={isBackingUp}
            className="flex items-center gap-2 bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-500/30 px-4 py-2.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 shadow-[0_0_15px_rgba(37,99,235,0.05)] hover:shadow-[0_0_15px_rgba(37,99,235,0.15)] active:scale-[0.98] disabled:opacity-50 cursor-pointer"
          >
            {isBackingUp ? <FaSpinner className="animate-spin" /> : <FaSave />} 
            <span>Create Backup</span>
          </button>

          <button
            onClick={handleRollback}
            disabled={isRollingBack}
            className="flex items-center gap-2 bg-rose-600/10 hover:bg-rose-600/20 text-rose-400 border border-rose-500/30 px-4 py-2.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 shadow-[0_0_15px_rgba(225,29,72,0.05)] hover:shadow-[0_0_15px_rgba(225,29,72,0.15)] active:scale-[0.98] disabled:opacity-50 cursor-pointer"
          >
            {isRollingBack ? <FaSpinner className="animate-spin" /> : <FaHistory />} 
            <span>Rollback</span>
          </button>

          {projectPath !== "." && (
            <button
              onClick={() => setProjectPath(".")}
              className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 px-4 py-2.5 rounded-xl text-sm font-semibold tracking-wide transition-all duration-200 cursor-pointer"
            >
              <FaUndo /> <span>Reset Path</span>
            </button>
          )}
        </div>
      </div>

      {/* Dropzone Pipeline */}
      <div className="relative bg-slate-900 border-2 border-dashed border-slate-700 hover:border-cyan-500 rounded-xl p-8 transition group">
        <input
          type="file"
          accept=".zip"
          onChange={handleZipUpload}
          disabled={uploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center gap-3">
          <FaCloudUploadAlt className={`text-5xl ${uploading ? "text-yellow-400 animate-pulse" : "text-slate-400 group-hover:text-cyan-400"}`} />
          <p className="text-sm font-medium">
            {uploading ? "Uploading project..." : "Drag & Drop or Click to Upload Python Project (.zip)"}
          </p>
        </div>
      </div>

      {/* Top Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Files Scanned" value={summary.total_scans} color="text-cyan-400" icon={<FaFolderOpen />} />
        <StatCard title="Issues Found" value={summary.total_issues} color={summary.total_issues > 0 ? "text-red-500" : "text-green-400"} icon={<FaBug />} />
        <StatCard title="Security Score" value={summary.security_score} color={summary.security_score === "A+" ? "text-green-400" : "text-yellow-400"} icon={<FaShieldAlt />} />
        <StatCard title="Critical Fixed" value={summary.total_fixed} color="text-amber-400" icon={<FaCheckCircle />} />
      </div>

      {/* TABLE: Targets with strict horizontal centering layout */}
      <div className="bg-slate-900/60 p-6 rounded-xl border border-slate-800 shadow-xl">
        <h3 className="text-xl font-bold mb-4 text-slate-100">Recent Scan History</h3>
        <div className="overflow-x-auto rounded-lg border border-slate-800/80">
          <table className="w-full text-sm table-fixed min-w-175">
            <thead className="text-xs uppercase bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-4 px-4 text-center font-semibold tracking-wider w-[22%]">Target Project</th>
                <th className="py-4 px-4 text-center font-semibold tracking-wider w-[18%]">Files Scanned</th>
                <th className="py-4 px-4 text-center font-semibold tracking-wider w-[18%]">Issues Found</th>
                <th className="py-4 px-4 text-center font-semibold tracking-wider w-[20%]">Status</th>
                <th className="py-4 px-4 text-center font-semibold tracking-wider w-[22%]">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 bg-slate-900/20">
              {history.length > 0 ? (
                history.map((scan, index) => (
                  <tr key={index} className="hover:bg-slate-800/30 transition-colors duration-150">
                    <td className="py-4 px-4 text-center font-mono text-cyan-400 font-medium truncate">{scan.target_project}</td>
                    <td className="py-4 px-4 text-center text-slate-100 font-mono font-bold text-base">{scan.files_scanned}</td>
                    <td className="py-4 px-4 text-center font-bold text-red-500 text-base">{scan.issues_found ?? scan.total_issues ?? 0}</td>
                    <td className="py-4 px-4">
                      <div className="flex justify-center items-center w-full">
                        <span className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider block text-center min-w-27.5 ${
                          scan.status === "VULNERABLE" 
                            ? "bg-red-500/10 text-red-500 border border-red-500/20" 
                            : "bg-green-500/10 text-green-400 border border-green-500/20"
                        }`}>
                          {scan.status}
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-center text-xs font-mono text-slate-400">{scan.timestamp}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="py-10 text-center text-sm font-mono text-slate-500">
                    No scan records available in global workspace log pipeline.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Analytics Module */}
      <Analytics topRules={topRules} summary={summary} />
    </div>
  );
}