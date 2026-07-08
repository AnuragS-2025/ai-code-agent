import { NavLink } from "react-router-dom";
import {
  FaHome,
  FaSearch,
  FaFileAlt,
  FaShieldAlt,
  FaCog,
} from "react-icons/fa";

const menuItems = [
  {
    name: "Dashboard",
    path: "/",
    icon: <FaHome />,
  },
  {
    name: "Scan",
    path: "/scan",
    icon: <FaSearch />,
  },
  {
    name: "Reports",
    path: "/reports",
    icon: <FaFileAlt />,
  },
  {
    name: "Validation",
    path: "/validation",
    icon: <FaShieldAlt />,
  },
  {
    name: "Settings",
    path: "/settings",
    icon: <FaCog />,
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-700 text-white">
      <div className="text-2xl font-bold p-6 text-cyan-400">
        AI Code Agent
      </div>

      <nav className="flex flex-col gap-2 px-3">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? "bg-cyan-500 text-black"
                  : "hover:bg-slate-800"
              }`
            }
          >
            {item.icon}
            {item.name}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}