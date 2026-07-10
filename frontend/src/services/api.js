import axios from "axios";

// 🎯 Port configuration matching active FastAPI Swagger deployment
const API_BASE_URL = window.location.hostname === "localhost" 
  ? "http://localhost:8000" 
  : "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Use let to allow cache invalidation during real-time scan overrides
export let cachedIssues = null;
export let cachedReport = null;

// Helper function to safely clean paths for query params & bodies
const formatPath = (path) => {
  if (!path) return ".";
  return path.replace(/\\/g, "/");
};

// ==========================================
// 1. CORE SYSTEM & DASHBOARD DATA
// ==========================================
export const getDashboardData = async (projectPath = ".") => {
  try {
    const safePath = formatPath(projectPath);
    const response = await api.get("/dashboard", {
      params: { project_path: safePath }
    });
    return response.data;
  } catch (error) {
    console.error("API Error [getDashboardData]:", error);
    throw error;
  }
};

export const getHealth = () => api.get("/health");
export const getConfig = () => api.get("/config");
export const getTools = () => api.get("/tools");

// ==========================================
// 2. SCAN ENGINE & REPORT PIPELINES
// ==========================================
export const getReport = async (projectPath = ".", forceRefresh = false) => {
  try {
    if (cachedReport && !forceRefresh) return cachedReport;
    const safePath = formatPath(projectPath);
    const response = await api.get("/report", { params: { project_path: safePath } });
    cachedReport = response.data;
    return cachedReport;
  } catch (error) {
    console.error("API Error [getReport]:", error);
    throw error;
  }
};

// 🔥 FIXED FOR FASTAPI STRICTNESS BYPASS WITH AUTO-CACHE BREAKER 🔥
export const triggerScan = async (projectPath = ".") => {
  try {
    // 🎯 CACHE BREAKER TRICK: Scan trigger hotey hi purane references null karo
    cachedIssues = null;
    cachedReport = null;
    
    const safePath = formatPath(projectPath);
    window.lastScannedPath = safePath; // Global reference for issue page fallback context
    
    // Send path inside the Request Body (JSON) instead of URL params
    const response = await api.post("/scan", { 
      project_path: safePath 
    });
    
    return response.data;
  } catch (error) {
    console.error("API Error [triggerScan]:", error);
    throw error;
  }
};
export const startScan = triggerScan;

export const getHtmlReport = (projectPath = ".") => {
  return api.get("/report/html", { params: { project_path: formatPath(projectPath) } });
};

export const exportReport = (projectPath = ".") => {
  return api.get("/report/export", { params: { project_path: formatPath(projectPath) } });
};

export const getHistory = () => api.get("/history");

// ==========================================
// 3. VULNERABILITY ISSUES & DISCOVERY
// ==========================================
export const getIssues = async (filters = {}, forceRefresh = false) => {
  try {
    if (cachedIssues && !forceRefresh && cachedIssues.length > 0) {
      return cachedIssues; 
    }
    
    let rawPath = ".";
    if (typeof filters === "string") {
      rawPath = filters;
    } else if (filters?.project_path) {
      rawPath = filters.project_path;
    } else if (window.lastScannedPath) { 
      rawPath = window.lastScannedPath;
    }

    const safePath = rawPath.replace(/\\/g, "/");
    console.log("🚀 Fetching report data to sync issues for target:", safePath);

    const response = await api.get("/report", {
      params: { project_path: safePath }
    });
    
    console.log("Raw Report Stream Received:", response.data);

    let issuesList = [];
    if (response.data) {
      if (Array.isArray(response.data)) {
        issuesList = response.data;
      } else if (Array.isArray(response.data.issues)) {
        issuesList = response.data.issues;
      } else if (Array.isArray(response.data.findings)) {
        issuesList = response.data.findings;
      } else if (Array.isArray(response.data.results)) {
        issuesList = response.data.results;
      } else if (response.data.success && response.data.total_issues > 0) {
        // Handle fallback parsing if there are actual issues inside sub-objects
        if (response.data.by_tool) {
          issuesList = Object.keys(response.data.by_tool).flatMap(tool => response.data.by_tool[tool] || []);
        }
      }
    }

    // 🎯 CRITICAL FIX FOR 0 FINDINGS LOGS:
    // Agar report successful hai par array zero hai (Clean code), toh explicit item return karo 
    // jisse frontend loader instantly break hokar solid state render kare.
    if (issuesList.length === 0) {
      issuesList = [{
        id: "clean-workspace-status",
        test_id: "SECURE",
        issue_severity: "LOW",
        issue_confidence: "HIGH",
        filename: "All Scanned Targets",
        issue_text: "✅ Great job! No security issues or vulnerabilities found in this workspace directory.",
        line_number: 0
      }];
    }

    cachedIssues = issuesList;
    return cachedIssues;
  } catch (error) {
    console.error("API Redirect Patch Error [getIssues]:", error);
    return [];
  }
};

// ==========================================
// 4. AUTOMATED PATCH OPERATIONS & JOBS
// ==========================================
export const applyCodeFix = async (projectPath = ".") => {
  try {
    cachedIssues = null;
    cachedReport = null;
    const safePath = formatPath(projectPath);
    const response = await api.post("/fix", {
      project_path: safePath,
    });
    return response.data;
  } catch (error) {
    console.error("API Error [applyCodeFix]:", error);
    throw error;
  }
};

export const createFixJob = (projectPath = ".") => {
  return api.post("/jobs/fix", {
    project_path: formatPath(projectPath),
  });
};

export const getJobStatus = (jobId) => api.get(`/jobs/${jobId}`);

// ==========================================
// 5. AI EXPLANATION, DIFFS & BACKUPS
// ==========================================
export const previewFix = (payload) => api.post("/preview", payload);

export const getCodeDiff = (projectPath = ".") => {
  return api.post("/diff", {
    project_path: formatPath(projectPath),
  });
};

export const askAIExplanation = (payload) => api.post("/explain", payload);

export const createGitBackup = (projectPath = ".") => {
  return api.post("/git/backup", {
    project_path: formatPath(projectPath),
  });
};

export const triggerGitRollback = (projectPath = ".") => {
  return api.post("/git/rollback", null, { params: { project_path: formatPath(projectPath) } });
};

export default api;