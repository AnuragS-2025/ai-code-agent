import axios from "axios";

const API_BASE_URL = window.location.hostname === "localhost" 
  ? "http://localhost:8000" 
  : "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 1. DASHBOARD COUNTERS
export const getDashboardData = async () => {
  try {
    const response = await api.get("/dashboard");
    return response.data;
  } catch (error) {
    console.error("API Error [getDashboardData]:", error);
    throw error;
  }
};

// 2. DISCOVERED THREAT VECTORS
export const getReport = async () => {
  try {
    const response = await api.get("/report");
    return response.data;
  } catch (error) {
    console.error("API Error [getReport]:", error);
    throw error;
  }
};

// 3. VALIDATION HUB ISSUES LIST
export const getIssues = async () => {
  try {
    const response = await api.get("/issues");
    return response.data;
  } catch (error) {
    console.error("API Error [getIssues]:", error);
    throw error;
  }
};

// 4. START REPO CODE ANALYSIS SCAN (Dono names handle kar diye taaki crash na ho)
export const triggerScan = async (scanType = "all", targetPath = "") => {
  try {
    const response = await api.post("/scan", { 
      type: scanType, 
      target_path: targetPath 
    });
    return response.data;
  } catch (error) {
    console.error("API Error [triggerScan]:", error);
    throw error;
  }
};
// Aliasing startScan to point directly to triggerScan
export const startScan = triggerScan; 

// 5. APPLY PATCH FIX PIPELINE
export const applyCodeFix = async (issueId, contextFile) => {
  try {
    const response = await api.post("/fix", { 
      issue_id: issueId, 
      file: contextFile 
    });
    return response.data;
  } catch (error) {
    console.error("API Error [applyCodeFix]:", error);
    throw error;
  }
};

export default api;