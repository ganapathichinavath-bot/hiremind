import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../providers";
import { 
  Search, 
  MapPin, 
  ChevronLeft, 
  ChevronRight,
  Eye,
  Building,
  Award,
  TrendingUp,
  UserCheck,
  X,
  Heart,
  ArrowRight
} from "lucide-react";
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer 
} from "recharts";

export default function Ranking() {
  const { token } = useAuth();

  const [candidates, setCandidates] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filter states
  const [search, setSearch] = useState("");
  const [minExp, setMinExp] = useState<string>("");
  const [maxExp, setMaxExp] = useState<string>("");
  const [location, setLocation] = useState("");

  // Detailed Modal states
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [modalLoading, setModalLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const fetchCandidates = async () => {
    if (!token) return;
    setLoading(true);

    let queryParams = `page=${page}&limit=10`;
    if (search) queryParams += `&search=${encodeURIComponent(search)}`;
    if (minExp) queryParams += `&min_experience=${minExp}`;
    if (maxExp) queryParams += `&max_experience=${maxExp}`;
    if (location) queryParams += `&location=${encodeURIComponent(location)}`;

    try {
      const response = await fetch(`${API_URL}/api/candidates?${queryParams}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) {
        setCandidates(data.candidates || []);
        setTotal(data.total || 0);
        setPages(data.pages || 1);
      }
    } catch (e) {
      console.error("Failed to load candidates", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [token, page]);

  const handleApplyFilters = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchCandidates();
  };

  const handleClearFilters = () => {
    setSearch("");
    setMinExp("");
    setMaxExp("");
    setLocation("");
    setPage(1);
    setTimeout(() => {
      fetchCandidates();
    }, 100);
  };

  // Fetch detailed info
  const handleOpenDetail = async (id: string) => {
    setSelectedCandidateId(id);
    setModalLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/candidates/detail/${id}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) {
        setSelectedCandidate(data);
      }
    } catch (e) {
      console.error("Failed to load candidate details", e);
    } finally {
      setModalLoading(false);
    }
  };

  const handleCloseDetail = () => {
    setSelectedCandidateId(null);
    setSelectedCandidate(null);
  };

  const handleToggleSave = async (candidateId: string, isCurrentlySaved: boolean, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token) return;
    try {
      const method = isCurrentlySaved ? "DELETE" : "POST";
      const response = await fetch(`${API_URL}/api/candidates/save/${candidateId}`, {
        method,
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (response.ok) {
        setCandidates(prev => prev.map(c => {
          if (c.candidate_id === candidateId) {
            return { ...c, is_saved: !isCurrentlySaved };
          }
          return c;
        }));
        if (selectedCandidate && selectedCandidate.candidate_id === candidateId) {
          setSelectedCandidate((prev: any) => ({ ...prev, is_saved: !isCurrentlySaved }));
        }
      }
    } catch (e) {
      console.error("Failed to toggle save status", e);
    }
  };


  function intSafe(val: any) {
    const parsed = parseInt(val);
    return isNaN(parsed) ? 0 : parsed;
  }

  // Prep Radar Data if candidate details exist
  const getRadarData = () => {
    if (!selectedCandidate) return [];
    return [
      { subject: "Semantic Match", value: intSafe(selectedCandidate.semantic_score * 100) },
      { subject: "Skill Coverage", value: intSafe(selectedCandidate.skill_score * 100) },
      { subject: "Experience Target", value: intSafe(selectedCandidate.experience_score * 100) },
      { subject: "Behavioral Signal", value: intSafe(selectedCandidate.behavioral_score * 100) },
      { subject: "Education Tier", value: intSafe(selectedCandidate.education_score * 100) },
    ];
  };

  return (
    <Layout>
      <div className="space-y-8 relative">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              Intelligent Candidate Discovery
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Search and filter matched candidate profiles based on hybrid scores
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-xs text-indigo-400 font-semibold px-4 py-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
              {total} Profiles Matched
            </div>
            <Link 
              to="/saved-candidates"
              className="py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition-all shadow-md shadow-indigo-600/20 flex items-center gap-2"
            >
              <span>Proceed to Step 4: Saved Candidates</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Filters Panel */}
        <div className="glass-card rounded-3xl p-6 border border-slate-800/80">
          <form onSubmit={handleApplyFilters} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Title / Keyword search
              </label>
              <div className="relative">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input 
                  type="text"
                  placeholder="e.g. AI Engineer"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 text-xs transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input 
                  type="text"
                  placeholder="e.g. Pune, Noida"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 text-xs transition-all"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Min YOE Target
                </label>
                <input 
                  type="number"
                  placeholder="Min"
                  value={minExp}
                  onChange={(e) => setMinExp(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 text-xs transition-all"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  Max YOE Target
                </label>
                <input 
                  type="number"
                  placeholder="Max"
                  value={maxExp}
                  onChange={(e) => setMaxExp(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 text-xs transition-all"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-semibold text-xs rounded-xl transition-all shadow-lg shadow-indigo-600/20"
              >
                Apply Filters
              </button>
              <button
                type="button"
                onClick={handleClearFilters}
                className="px-4 py-2.5 bg-slate-950 border border-slate-850 hover:bg-slate-900 text-slate-400 text-xs font-semibold rounded-xl transition-all"
              >
                Clear
              </button>
            </div>
          </form>
        </div>

        {/* Table View */}
        <div className="glass-card rounded-3xl border border-slate-800/80 overflow-hidden">
          {loading ? (
            <div className="py-24 flex justify-center">
              <div className="w-8 h-8 border-t-2 border-indigo-500 rounded-full animate-spin"></div>
            </div>
          ) : candidates.length === 0 ? (
            <div className="py-24 text-center text-slate-500 text-xs">
              No candidates found. Rank pool in "Job Analysis" page or adjust search filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left">
                <thead>
                  <tr className="border-b border-slate-800/80 bg-slate-900/10 text-slate-400 text-[10px] uppercase font-bold tracking-wider">
                    <th className="py-4 px-6">Rank</th>
                    <th className="py-4 px-6">Candidate</th>
                    <th className="py-4 px-6">Headline</th>
                    <th className="py-4 px-6">Experience</th>
                    <th className="py-4 px-4 text-center">Semantic</th>
                    <th className="py-4 px-4 text-center">Skill</th>
                    <th className="py-4 px-4 text-center">Behavioral</th>
                    <th className="py-4 px-6 text-right">Composite</th>
                    <th className="py-4 px-6 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-850">
                  {candidates.map((cand) => (
                    <tr 
                      key={cand.candidate_id} 
                      className={`hover:bg-slate-900/20 transition-all ${
                        cand.is_disqualified ? "opacity-60 bg-rose-950/5" : ""
                      }`}
                    >
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center justify-center h-7 w-7 rounded-lg font-bold text-xs ${
                          cand.rank === 1 ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                          cand.rank === 2 ? "bg-slate-355/10 text-slate-300 border border-slate-300/20" :
                          cand.rank === 3 ? "bg-amber-700/10 text-amber-600 border border-amber-700/20" :
                          "bg-slate-800/40 text-slate-400 border border-slate-850"
                        }`}>
                          #{cand.rank || "—"}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="font-bold text-slate-200">{cand.candidate_id}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5">{cand.location}</div>
                      </td>
                      <td className="py-4 px-6 max-w-xs truncate">
                        <div className="text-xs font-semibold text-slate-300 truncate">{cand.current_title}</div>
                        <div className="text-[10px] text-slate-500 mt-0.5 truncate">{cand.current_company || "Unknown"}</div>
                      </td>
                      <td className="py-4 px-6">
                        <span className="text-xs text-slate-300">{cand.years_of_experience} yrs</span>
                      </td>
                      <td className="py-4 px-4 text-center font-medium text-xs text-slate-400">
                        {cand.semantic_score ? `${(cand.semantic_score * 100).toFixed(0)}%` : "0%"}
                      </td>
                      <td className="py-4 px-4 text-center font-medium text-xs text-slate-400">
                        {cand.skill_score ? `${(cand.skill_score * 100).toFixed(0)}%` : "0%"}
                      </td>
                      <td className="py-4 px-4 text-center font-medium text-xs text-slate-400">
                        {cand.behavioral_score ? `${(cand.behavioral_score * 100).toFixed(0)}%` : "0%"}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <span className={`text-xs font-extrabold ${
                          cand.is_honeypot ? "text-amber-500" : "text-indigo-400"
                        }`}>
                          {cand.is_honeypot ? "Disqualified" : `${(cand.score * 100).toFixed(0)}%`}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-center">
                        <div className="flex justify-center items-center gap-2">
                          <button
                            onClick={() => handleOpenDetail(cand.candidate_id)}
                            className="p-2 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-lg border border-transparent hover:border-slate-700/50 transition-all"
                            title="View Profile"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => handleToggleSave(cand.candidate_id, !!cand.is_saved, e)}
                            className="p-2 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-lg border border-transparent hover:border-slate-700/50 transition-all"
                            title={cand.is_saved ? "Unsave Candidate" : "Save Candidate"}
                          >
                            <Heart className={`w-4 h-4 ${cand.is_saved ? "fill-rose-500 text-rose-500 pulse-heart" : "text-slate-400"}`} />
                          </button>
                        </div>
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Footer */}
          {pages > 1 && (
            <div className="flex justify-between items-center p-6 border-t border-slate-800/80 bg-slate-900/10">
              <span className="text-xs text-slate-400">
                Page {page} of {pages}
              </span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  className="p-2 bg-slate-950 border border-slate-850 hover:bg-slate-900 disabled:opacity-50 text-slate-400 rounded-lg transition-all"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={page >= pages}
                  onClick={() => setPage(page + 1)}
                  className="p-2 bg-slate-950 border border-slate-850 hover:bg-slate-900 disabled:opacity-50 text-slate-400 rounded-lg transition-all"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Detailed Modal Overlay (Glassmorphic Slider Drawer) */}
        {selectedCandidateId && (
          <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-md flex justify-end z-50 transition-all">
            <div className="w-full max-w-3xl bg-slate-900/90 border-l border-slate-800 h-full overflow-y-auto p-8 shadow-2xl relative flex flex-col justify-between">
              
              {/* Close Button */}
              <button 
                onClick={handleCloseDetail}
                className="absolute top-6 right-6 p-2 bg-slate-950/40 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-xl transition-all"
              >
                <X className="w-5 h-5" />
              </button>

              {modalLoading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="w-8 h-8 border-t-2 border-indigo-500 rounded-full animate-spin"></div>
                </div>
              ) : !selectedCandidate ? (
                <div className="text-center py-24 text-slate-500 text-sm">
                  Candidate profile not found.
                </div>
              ) : (() => {
                const profile = selectedCandidate.profile_data?.profile || {};
                const signals = selectedCandidate.profile_data?.redrob_signals || {};
                const matchPct = intSafe(selectedCandidate.score * 100);
                const explanation = selectedCandidate.reasoning || {};

                return (
                  <div className="space-y-8">
                    {/* Header */}
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Candidate Profile</span>
                          <span className="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-bold rounded">
                            Rank #{selectedCandidate.rank || "—"}
                          </span>
                        </div>
                        <h1 className="text-2xl font-extrabold text-white mt-1">{selectedCandidate.candidate_id}</h1>
                      </div>
                      
                      <button
                        onClick={(e) => handleToggleSave(selectedCandidate.candidate_id, !!selectedCandidate.is_saved, e)}
                        className="px-3 py-1.5 bg-slate-950/60 border border-slate-800 hover:bg-slate-800 text-slate-350 hover:text-slate-200 text-xs font-semibold rounded-xl transition-all flex items-center gap-2"
                      >
                        <Heart className={`w-4 h-4 ${selectedCandidate.is_saved ? "fill-rose-500 text-rose-500 pulse-heart" : "text-slate-400"}`} />
                        <span>{selectedCandidate.is_saved ? "Saved" : "Save Profile"}</span>
                      </button>
                    </div>


                    {/* Top Info Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="glass-card rounded-2xl p-5 border border-slate-800 lg:col-span-2 space-y-4">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Current Headline</span>
                          <p className="text-sm font-semibold text-slate-200 mt-1">{profile.headline || "Unknown Title"}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="flex items-start gap-2">
                            <MapPin className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                            <div>
                              <span className="text-[10px] text-slate-500 uppercase font-semibold">Location</span>
                              <p className="text-xs text-slate-300 font-medium mt-0.5">{profile.location || "India"}</p>
                            </div>
                          </div>
                          <div className="flex items-start gap-2">
                            <Building className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
                            <div>
                              <span className="text-[10px] text-slate-500 uppercase font-semibold">Company</span>
                              <p className="text-xs text-slate-300 font-medium mt-0.5">{profile.current_company || "Unknown"}</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl">
                          <span className="text-[10px] text-slate-500 uppercase font-semibold block">Summary</span>
                          <p className="text-[11px] text-slate-400 leading-relaxed mt-1">{profile.summary || "No summary provided."}</p>
                        </div>
                      </div>

                      {/* Score Circle */}
                      <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center justify-center text-center">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-4">Fit Match Score</span>
                        <div className="relative w-28 h-28 flex items-center justify-center bg-indigo-500/5 border border-indigo-500/20 rounded-full shadow-inner">
                          <div className="text-center">
                            <span className="text-2xl font-extrabold text-white">{matchPct}%</span>
                            <span className="text-[9px] text-indigo-400 block font-semibold uppercase mt-0.5">Match</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Breakdown section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      {/* Score Metrics Radar Chart */}
                      <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mb-4">Matching Vector Breakdown</span>
                        <div className="h-[200px] w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={getRadarData()}>
                              <PolarGrid stroke="rgba(255,255,255,0.05)" />
                              <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={9} />
                              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={8} />
                              <Radar name="Scoring" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} />
                            </RadarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Explainable AI block */}
                      <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4">
                        <div className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                          <TrendingUp className="w-4 h-4 text-indigo-400" />
                          <span>AI Decision Explanation</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed bg-indigo-950/20 border border-indigo-900/20 p-3 rounded-xl">
                          {explanation || "Generating decision explanation..."}
                        </p>
                      </div>
                    </div>

                    {/* Skills & Experience details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4">
                        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                          <Award className="w-4 h-4 text-indigo-400" />
                          <span>Candidate Skills</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {selectedCandidate.profile_data?.skills?.map((skill: any) => (
                            <span 
                              key={skill.name} 
                              className="px-2.5 py-1 bg-slate-950 border border-slate-800 text-[10px] font-semibold rounded text-slate-300"
                            >
                              {skill.name}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Platform activity */}
                      <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-4">
                        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                          <UserCheck className="w-4 h-4 text-indigo-400" />
                          <span>Platform Signals</span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs">
                          <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl">
                            <span className="text-[10px] text-slate-500 block">Notice Period Target</span>
                            <span className="font-semibold text-slate-200">{signals.notice_period_days || 0} Days Target</span>
                          </div>
                          <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl">
                            <span className="text-[10px] text-slate-500 block">Offer Acceptance Rate</span>
                            <span className="font-semibold text-slate-200">{(signals.offer_acceptance_rate || 0.0) * 100}% Rate</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
