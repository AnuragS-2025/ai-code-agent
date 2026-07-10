import { useState } from "react"; 
import { BrowserRouter, Routes, Route } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import Dashboard from "../pages/Dashboard";
import Scan from "../pages/Scan";
import Reports from "../pages/Reports";
import IssueExplorer from "../pages/IssueExplorer"; 
import Validation from "../pages/Validation";
import ToolsConfig from "../pages/ToolsConfig"; // 🎯 Settings wala import completely removed!

export default function AppRoutes() {
  // Global state jo saare pages me data share karega
  const [globalPath, setGlobalPath] = useState(".");

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          {/* Dashboard path change kar sakta hai, isliye isko setter bhi diya */}
          <Route path="/" element={<Dashboard projectPath={globalPath} setProjectPath={setGlobalPath} />} />
          
          {/* Baaki sab pages isi naye path ko read karenge */}
          <Route path="/scan" element={<Scan projectPath={globalPath} />} />
          <Route path="/reports" element={<Reports projectPath={globalPath} />} />
          <Route path="/issues" element={<IssueExplorer projectPath={globalPath} />} /> 
          <Route path="/validation" element={<Validation projectPath={globalPath} />} />
          
          {/* 🎯 FIX: Settings wala Route yahan se poora remove kar diya gaya hai */}
          <Route path="/tools" element={<ToolsConfig />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}