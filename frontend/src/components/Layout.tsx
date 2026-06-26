import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../providers";
import { 
  LayoutDashboard, 
  FileText, 
  Users, 
  Download, 
  LogOut, 
  Sparkles,
  ShieldCheck,
  Heart
} from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { role, logout, isAuthenticated } = useAuth();

  React.useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth");
    }
  }, [isAuthenticated, navigate]);

  const navItems = [
    { name: "Dashboard 📊", href: "/dashboard", icon: LayoutDashboard },
    { name: "Job Analysis 📝", href: "/job-analysis", icon: FileText },
    { name: "Candidate Ranking 🏆", href: "/ranking", icon: Users },
    { name: "Saved Candidates ❤️", href: "/saved-candidates", icon: Heart },
    { name: "Submission Generator 📥", href: "/submission", icon: Download },
  ];


  if (!isAuthenticated) return null;

  return (
    <div className="flex h-screen bg-transparent overflow-hidden text-slate-100">
      {/* Sidebar (Glassmorphism) */}
      <aside className="w-64 bg-slate-900/40 border-r border-slate-800 flex flex-col backdrop-blur-xl">
        {/* Sidebar Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-semibold text-lg bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent leading-none">
              HIREMIND AI
            </h1>
            <span className="text-[10px] text-indigo-400 font-medium uppercase tracking-wider">
              Recruiter Copilot
            </span>
          </div>
        </div>

        {/* Sidebar Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group border ${
                  isActive
                    ? "bg-indigo-600/10 text-indigo-400 border-indigo-500/30 shadow-lg shadow-indigo-500/5"
                    : "text-slate-400 border-transparent hover:bg-slate-800/40 hover:text-slate-200"
                }`}
              >
                <item.icon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${
                  isActive ? "text-indigo-400" : "text-slate-400 group-hover:text-slate-300"
                }`} />
                <span className="font-medium text-sm">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/20">
          <div className="flex items-center justify-between px-3 py-2 bg-slate-950/40 border border-slate-800/50 rounded-xl mb-3">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-slate-300">Active Recruiter</span>
                <span className="text-[10px] text-slate-500 capitalize">{role || "recruiter"}</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="flex items-center justify-center w-full gap-2 px-4 py-2.5 bg-rose-600/10 text-rose-400 border border-rose-500/20 rounded-xl font-medium text-sm hover:bg-rose-600 hover:text-white transition-all duration-300"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out 🚪</span>
          </button>
        </div>
      </aside>

      {/* Main Content Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-900/20 flex items-center justify-between px-8 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-medium text-slate-400">Welcome to Recruiter workspace 👋</h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-slate-400">
              India Runs Challenge Mode 🏆
            </div>
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
          </div>
        </header>

        {/* Workspace Body */}
        <main className="flex-1 overflow-y-auto bg-transparent p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
