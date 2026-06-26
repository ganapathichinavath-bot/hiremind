import React, { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { useAuth } from "../providers";
import { 
  Users, 
  Percent, 
  AlertTriangle, 
  Trash2, 
  UploadCloud, 
  FileCode,
  Sparkles,
  CheckCircle,
  ArrowRight
} from "lucide-react";
import { Link } from "react-router-dom";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";

export default function Dashboard() {
  const { token } = useAuth();
  
  const [stats, setStats] = useState<any>(null);
  const [topCandidates, setTopCandidates] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const fetchDashboardData = async () => {
    if (!token) return;
    try {
      setLoading(true);
      // Fetch stats
      const statsRes = await fetch(`${API_URL}/api/candidates/analytics`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const statsData = await statsRes.json();
      setStats(statsData);

      // Fetch top candidates
      const topRes = await fetch(`${API_URL}/api/jobs/top-candidates?limit=5`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const topData = await topRes.json();
      setTopCandidates(Array.isArray(topData) ? topData : []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !token) return;
    const file = e.target.files[0];
    
    setUploading(true);
    setUploadError(null);
    setUploadResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/candidates/upload`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Upload failed");
      
      setUploadResult(data);
      fetchDashboardData();
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  // Format Recharts data
  const experienceChartData = stats?.experience_distribution 
    ? Object.entries(stats.experience_distribution).map(([key, val]) => ({ name: key, value: val }))
    : [];

  const skillChartData = stats?.top_skills 
    ? Object.entries(stats.top_skills).map(([key, val]) => ({ name: key, count: val }))
    : [];

  const COLORS = ["#6366f1", "#a855f7", "#ec4899", "#f59e0b", "#10b981"];

  return (
    <Layout>
      <div className="space-y-8">
        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              Copilot Overview 📊
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Real-time intelligence dashboard showing candidate pool statistics 📈
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={fetchDashboardData}
              className="px-4 py-2 bg-slate-900 border border-slate-800 text-xs font-semibold rounded-xl text-slate-300 hover:bg-slate-850 hover:text-white transition-all"
            >
              Refresh Data 🔄
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1 */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800/80">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Ingested 👤</span>
                <h3 className="text-3xl font-bold mt-2 text-white">{stats?.total_candidates || 0}</h3>
              </div>
              <div className="p-3 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-xl">
                <Users className="w-5 h-5" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">Total candidate profiles in SQL database</p>
          </div>

          {/* Card 2 */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800/80">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Avg Fit Match ⚡</span>
                <h3 className="text-3xl font-bold mt-2 text-white">
                  {stats?.average_score ? `${(stats.average_score * 100).toFixed(1)}%` : "0.0%"}
                </h3>
              </div>
              <div className="p-3 bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded-xl">
                <Percent className="w-5 h-5" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">Average composite rank score of candidate pool</p>
          </div>

          {/* Card 3 */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800/80">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Disqualified 🛑</span>
                <h3 className="text-3xl font-bold mt-2 text-rose-400">{stats?.disqualified_count || 0}</h3>
              </div>
              <div className="p-3 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-xl">
                <Trash2 className="w-5 h-5" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">Candidates penalized for poor trajectory / consulting</p>
          </div>

          {/* Card 4 */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800/80">
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Honeypot Traps 🍯</span>
                <h3 className="text-3xl font-bold mt-2 text-amber-500">{stats?.honeypot_count || 0}</h3>
              </div>
              <div className="p-3 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-xl">
                <AlertTriangle className="w-5 h-5" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">Impossible profiles isolated (Tier 0 match)</p>
          </div>
        </div>

        {/* Mid Section: Upload & Top Shortlist */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Ingest Widget */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between lg:col-span-1 min-h-[300px]">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <UploadCloud className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-slate-200">Dataset Ingest 📤</h2>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-6">
                Upload new recruiter candidate pools in `.jsonl` format. The system will automatically validate the schema, calculate core vectors, and persist profiles.
              </p>

              {uploadError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs mb-4">
                  {uploadError}
                </div>
              )}

              {uploadResult && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs mb-4 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Ingested {uploadResult.imported} records successfully! 🎉</span>
                </div>
              )}
            </div>

            <div>
              <label className={`w-full flex flex-col items-center justify-center border-2 border-dashed rounded-2xl py-8 px-4 text-center cursor-pointer transition-all ${
                uploading 
                  ? "border-indigo-500/40 bg-indigo-500/5 cursor-not-allowed" 
                  : "border-slate-800 bg-slate-950 hover:border-slate-700 hover:bg-slate-900"
              }`}>
                {uploading ? (
                  <>
                    <div className="w-6 h-6 border-t-2 border-indigo-500 rounded-full animate-spin mb-3"></div>
                    <span className="text-xs font-medium text-slate-300">Processing vectors... ⚙️</span>
                  </>
                ) : (
                  <>
                    <FileCode className="w-8 h-8 text-slate-500 mb-3" />
                    <span className="text-xs font-semibold text-slate-300">Select candidates.jsonl</span>
                    <span className="text-[10px] text-slate-500 mt-1">Accepts UTF-8 JSON lines 📂</span>
                    <input 
                      type="file" 
                      accept=".jsonl,.json" 
                      onChange={handleFileUpload} 
                      className="hidden" 
                      disabled={uploading}
                    />
                  </>
                )}
              </label>
            </div>
          </div>

          {/* Top Shortlist Preview */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 lg:col-span-2">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-slate-200">Current Candidate Shortlist ✨</h2>
              </div>
              <Link 
                to="/ranking" 
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-all"
              >
                <span>View Full List</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {loading ? (
              <div className="py-12 flex justify-center">
                <div className="w-6 h-6 border-t-2 border-indigo-500 rounded-full animate-spin"></div>
              </div>
            ) : topCandidates.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-xs">
                No candidates scored yet. Run candidate ranking in "Job Analysis" or upload a dataset. 🕵️‍♂️
              </div>
            ) : (
              <div className="space-y-4">
                {topCandidates.map((cand) => (
                  <div 
                    key={cand.candidate_id} 
                    className="flex justify-between items-center p-4 bg-slate-900/30 border border-slate-800/60 rounded-2xl hover:border-slate-700/80 transition-all"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`h-9 w-9 rounded-lg flex items-center justify-center font-bold text-sm ${
                        cand.rank === 1 ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                        cand.rank === 2 ? "bg-slate-300/10 text-slate-300 border border-slate-300/20" :
                        cand.rank === 3 ? "bg-amber-700/10 text-amber-600 border border-amber-700/20" :
                        "bg-slate-800/40 text-slate-400 border border-slate-850"
                      }`}>
                        #{cand.rank}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-sm text-slate-200">{cand.candidate_id}</h4>
                          <span className="text-[10px] text-slate-500 px-2 py-0.5 bg-slate-800 border border-slate-800/80 rounded-md">
                            {cand.years_of_experience} yrs yoe
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">{cand.title} at {cand.company || "Unknown"}</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-sm font-extrabold text-indigo-400">{(cand.score * 100).toFixed(0)}% Match</span>
                      <p className="text-[10px] text-slate-500 mt-1">{cand.location}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recharts Analytics Zone */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Skill Distribution */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800">
            <h3 className="text-md font-bold text-slate-200 mb-6">Top Extracted Skills Distribution 🤹‍♂️</h3>
            <div className="h-[250px] w-full">
              {skillChartData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-slate-500 text-xs">No skill data available</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={skillChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} />
                    <YAxis stroke="#94a3b8" fontSize={10} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                      itemStyle={{ color: "#a5b4fc" }}
                    />
                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]}>
                      {skillChartData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Experience Distribution */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800">
            <h3 className="text-md font-bold text-slate-200 mb-6">Experience Level Distribution 📈</h3>
            <div className="h-[250px] w-full">
              {experienceChartData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-slate-500 text-xs">No experience data available</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={experienceChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {experienceChartData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                      itemStyle={{ color: "#a5b4fc" }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
            <div className="flex flex-wrap justify-center gap-4 text-xs mt-2 text-slate-400">
              {experienceChartData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                  <span>{entry.name} ({String(entry.value)})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
