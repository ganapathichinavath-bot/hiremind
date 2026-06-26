import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../providers";
import { Sparkles, User, Lock, ArrowRight, Eye, EyeOff } from "lucide-react";

export default function Auth() {
  const navigate = useNavigate();
  const { login, isAuthenticated, loginWithGoogle } = useAuth();
  
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("recruiter");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/^http:\/\/(?!localhost|127\.0\.0\.1)/, "https://");
    const endpoint = isLogin ? "/api/auth/login" : "/api/auth/signup";

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(isLogin ? { username, password } : { username, password, role }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed");
      }

      if (isLogin) {
        login(data.access_token, data.role);
        navigate("/dashboard");
      } else {
        setIsLogin(true);
        setPassword("");
        setError("Account created! Please sign in with your credentials. 🎉");
      }
    } catch (err: any) {
      setError(err.message || "An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      await loginWithGoogle();
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Google authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>

      {/* Main Container */}
      <div className="w-full max-w-md relative z-10">
        {/* Brand / Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 bg-indigo-600/20 text-indigo-400 rounded-2xl border border-indigo-500/30 mb-4 shadow-lg shadow-indigo-500/10">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
            HIREMIND AI
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            Production-grade candidate intelligence portal
          </p>
        </div>

        {/* Glass Box */}
        <div className="glass-card rounded-3xl p-8 border border-slate-800 shadow-2xl relative">
          <div className="flex border-b border-slate-800/80 mb-6">
            <button
              onClick={() => { setIsLogin(true); setError(null); }}
              className={`flex-1 pb-3 text-sm font-semibold transition-all border-b-2 ${
                isLogin ? "border-indigo-500 text-indigo-400" : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsLogin(false); setError(null); }}
              className={`flex-1 pb-3 text-sm font-semibold transition-all border-b-2 ${
                !isLogin ? "border-indigo-500 text-indigo-400" : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className={`p-4 rounded-xl text-xs mb-4 border ${
              error.includes("created") || error.includes("🎉")
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                : "bg-rose-500/10 text-rose-400 border-rose-500/20"
            }`}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Username
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-slate-950/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 text-sm transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-11 py-3 bg-slate-950/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 text-sm transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  System Role
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setRole("recruiter")}
                    className={`py-2 px-4 rounded-xl border text-xs font-semibold transition-all ${
                      role === "recruiter"
                        ? "bg-indigo-600/20 text-indigo-400 border-indigo-500"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900"
                    }`}
                  >
                    Recruiter
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole("admin")}
                    className={`py-2 px-4 rounded-xl border text-xs font-semibold transition-all ${
                      role === "admin"
                        ? "bg-indigo-600/20 text-indigo-400 border-indigo-500"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900"
                    }`}
                  >
                    Administrator
                  </button>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/20 mt-4 glow-effect"
            >
              {loading ? (
                <div className="w-5 h-5 border-t-2 border-white rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>{isLogin ? "Sign In to Copilot" : "Register Credentials"}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="relative flex py-4 items-center">
            <div className="flex-grow border-t border-slate-800"></div>
            <span className="flex-shrink mx-4 text-slate-500 text-xs uppercase tracking-wider">Or</span>
            <div className="flex-grow border-t border-slate-800"></div>
          </div>

          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 bg-slate-900 hover:bg-slate-800 active:bg-slate-950 disabled:opacity-50 text-slate-200 border border-slate-800 font-semibold text-sm rounded-xl transition-all"
          >
            <svg className="w-5 h-5 mr-1" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </button>
        </div>
      </div>
    </div>
  );
}
