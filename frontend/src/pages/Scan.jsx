import { useState, useEffect, useRef } from "react";
import {
  FaPlay,
  FaSpinner,
  FaShieldVirus,
  FaExclamationTriangle,
  FaCheckCircle,
  FaTimesCircle,
  FaBug,
} from "react-icons/fa";

import { triggerScan, getReport } from "../services/api";

export default function Scan({ projectPath = "." }) {
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);

  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const lastFetchedPathRef = useRef("");

  // ==========================================
  // Load Existing Report
  // ==========================================

  useEffect(() => {
    let mounted = true;

    async function fetchReport() {
      try {
        setLoading(true);

        const safePath = projectPath.replace(/\\/g, "/");

        if (lastFetchedPathRef.current === safePath) {
          return;
        }

        lastFetchedPathRef.current = safePath;

        const data = await getReport(safePath, true);

        if (!mounted) return;

        if (data) {
          setReport(data);
        }
      } catch (err) {
        console.warn("Report not available:", err);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    fetchReport();

    return () => {
      mounted = false;
    };
  }, [projectPath]);

  // ==========================================
  // Scan Handler
  // ==========================================
  const handleStartScan = async () => {
    if (scanning) return;

    const safePath = projectPath.replace(/\\/g, "/");

    try {
      setScanning(true);
      setLoading(true);

      setError(null);
      setReport(null);

      // Reset last fetched path so next report is always fresh
      lastFetchedPathRef.current = "";

      // Run scan
      await triggerScan(safePath);

      // Fetch latest report (ignore cache)
      const latestReport = await getReport(safePath, true);

      console.log("Latest Report:", latestReport);

      if (latestReport?.data) {
        setReport(latestReport.data);
    } else {
        setReport(latestReport);}
      alert("🎉 Scan completed successfully! Analysis metrics loaded.");

    } catch (err) {
      console.error("Scan Error:", err);

      setError(
        err?.response?.data?.detail ||
        "Failed to run scan pipeline."
      );
    } finally {
      setScanning(false);
      setLoading(false);
    }
  };

  // ==========================================
  // UI Helpers
  // ==========================================

  const totalIssues =
  report?.total_issues ??
  report?.issues?.length ??
  0;

  const isSafe = totalIssues === 0;

    return (
    <div className="space-y-6 text-white">

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900 p-6 rounded-xl border border-slate-800 gap-4">

        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <FaShieldVirus className="text-cyan-400" />
            Security Scanner Engine
          </h2>

          <p className="text-sm text-slate-400 mt-1 font-mono break-all">
            Target Workspace :
            <span className="text-yellow-400 ml-2">
              {projectPath}
            </span>
          </p>
        </div>

        <button
          onClick={handleStartScan}
          disabled={scanning}
          className="flex items-center gap-2 bg-linear-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium px-6 py-3 rounded-xl transition disabled:opacity-50"
        >
          {scanning ? (
            <>
              <FaSpinner className="animate-spin" />
              Running Scan...
            </>
          ) : (
            <>
              <FaPlay />
              Run Code Analysis
            </>
          )}
        </button>

      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-500 rounded-xl p-4 flex gap-3 items-center">
          <FaExclamationTriangle className="text-red-400 text-2xl" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">

        <h3 className="text-lg font-bold mb-4">
          Analysis Summary
        </h3>

        {loading ? (

          <div className="flex flex-col items-center justify-center py-10 gap-3 text-slate-400">
            <FaSpinner className="animate-spin text-3xl text-cyan-400" />
            <p>Synchronizing latest artifacts...</p>
          </div>

        ) : report ? (

          <div className="space-y-6">

            <div
              className={`p-5 rounded-xl border flex items-center gap-4 ${
                isSafe
                  ? "bg-green-900/20 border-green-500/50 text-green-400"
                  : "bg-red-900/20 border-red-500/50 text-red-400"
              }`}
            >
              {isSafe ? (
                <FaCheckCircle className="text-4xl" />
              ) : (
                <FaTimesCircle className="text-4xl" />
              )}

              <div>
                <h4 className="text-xl font-bold">
                  {isSafe
                    ? "Workspace is Secure"
                    : "Vulnerabilities Detected"}
                </h4>

                <p className="text-sm opacity-80">
                  {isSafe
                    ? "No security issues detected."
                    : `${totalIssues} issues found.`}
                </p>
              </div>

            </div>

            {!isSafe &&
              report?.by_tool &&
              Object.keys(report.by_tool).length > 0 && (

                <div>

                  <h4 className="text-sm font-bold uppercase text-slate-400 mb-3">
                    Tool Breakdown
                  </h4>

                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">

                    {Object.entries(report.by_tool).map(
                      ([tool, issues]) => (

                        <div
                          key={tool}
                          className="bg-slate-950 rounded-lg border border-slate-800 p-4"
                        >
                          <div className="flex justify-between items-center">

                            <span className="flex items-center gap-2 capitalize">
                              <FaBug className="text-red-400" />
                              {tool}
                            </span>

                            <span className="text-xs bg-red-500/10 border border-red-500/20 text-red-400 px-2 py-1 rounded">
                              {typeof issues === "number"
                                ? issues
                                : Array.isArray(issues)
                                ? issues.length
                                : 0}
                            </span>

                          </div>
                        </div>

                      )
                    )}

                  </div>

                </div>

              )}

          </div>

        ) : (

          <div className="text-center py-12 text-slate-500">
            No analysis available. Click
            <strong> Run Code Analysis </strong>
            to begin.
          </div>

        )}

      </div>

    </div>
  );
}