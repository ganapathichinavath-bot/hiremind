import { useNavigate } from "react-router-dom";
import { useAuth } from "../providers";
import { Sparkles, ArrowRight, Shield, Award, Zap, Cpu } from "lucide-react";

export default function Landing() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleCTA = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/auth");
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex flex-col justify-between relative overflow-hidden animate-fade-in">
      {/* Background Decorative Blobs */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header */}
      <header className="w-full max-w-7xl mx-auto px-6 h-20 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
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
        <button
          onClick={handleCTA}
          className="px-5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-bold rounded-xl text-slate-200 transition-all"
        >
          {isAuthenticated ? "Dashboard" : "Sign In"}
        </button>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-6 z-10 max-w-4xl mx-auto py-12">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-xs font-semibold text-indigo-450 mb-6">
          <Zap className="w-3.5 h-3.5" />
          <span>Next-Generation Candidate Scoring & Ranking</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent leading-[1.15] mb-6">
          Intelligent Talent Discovery <br/>
          Powered by Semantic Vectors
        </h1>

        <p className="text-slate-455 text-sm sm:text-md max-w-2xl leading-relaxed mb-8">
          Accelerate your screening process. Analyze job requirements, evaluate candidate capabilities with hybrid ML indicators, and instantly extract verified shortlists.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button
            onClick={handleCTA}
            className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm rounded-2xl transition-all shadow-lg shadow-indigo-600/20 flex items-center gap-2.5 glow-effect"
          >
            <span>{isAuthenticated ? "Go to Dashboard" : "Launch Recruiter Console"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full mt-16 max-w-5xl">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 text-left space-y-3">
            <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-450 w-fit">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-205 text-sm">Semantic Matching</h3>
            <p className="text-slate-400 text-xs leading-relaxed">
              Match candidate experience and career histories semantically beyond keyword searches.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 text-left space-y-3">
            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400 w-fit">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-205 text-sm">Interactive Radar Visuals</h3>
            <p className="text-slate-400 text-xs leading-relaxed">
              Deconstruct fit parameters across experience, behavior, education, and skills.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 text-left space-y-3">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 w-fit">
              <Shield className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-205 text-sm">Compliance Validation</h3>
            <p className="text-slate-400 text-xs leading-relaxed">
              Verify headers, limits, non-increasing scores, and tie-breakers before generating export CSV.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full h-16 flex items-center justify-center text-slate-500 text-xs z-10 border-t border-slate-900 bg-slate-950/20">
        <span>© 2026 HireMind AI. All rights reserved. India Runs Recruiter Platform.</span>
      </footer>
    </div>
  );
}
