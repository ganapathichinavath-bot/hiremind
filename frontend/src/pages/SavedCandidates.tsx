import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../providers";
import { 
  Heart,
  MapPin, 
  ChevronLeft, 
  ChevronRight,
  Eye,
  Building,
  GraduationCap,
  Award,
  ListTodo,
  TrendingUp,
  AlertTriangle,
  Mail,
  Phone,
  UserCheck,
  X,
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

export default function SavedCandidates() {
  const { token } = useAuth();

  const [candidates, setCandidates] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Detailed Modal states
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [modalLoading, setModalLoading] = useState(false);

  const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/^http:\/\/(?!localhost|127\.0\.0\.1)/, "https://");

  const fetchSavedCandidates = async () => {
    if (!token) return;
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/candidates/saved?page=${page}&limit=10`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) {
        setCandidates(data.candidates || []);
        setTotal(data.total || 0);
        setPages(data.pages || 1);
      }
    } catch (e) {
      console.error("Failed to load saved candidates", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSavedCandidates();
  }, [token, page]);

  const handleUnsave = async (candidateId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!token) return;
    try {
      const response = await fetch(`${API_URL}/api/candidates/save/${candidateId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (response.ok) {
        // Refresh local list
        fetchSavedCandidates();
        if (selectedCandidateId === candidateId) {
          handleCloseDetail();
        }
      }
    } catch (e) {
      console.error("Failed to unsave candidate", e);
    }
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
      <div className="space-y-8 relative animate-fade-in">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
              Saved Candidates ❤️
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Your bookmarked candidates from the discovery process.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-xs text-indigo-400 font-semibold px-4 py-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
              {total} Bookmarked Candidates
            </div>
            <Link 
              to="/submission"
              className="py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition-all shadow-md shadow-indigo-600/20 flex items-center gap-2"
            >
              <span>Proceed to Export Submission</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Table View */}
        <div className="glass-card rounded-3xl border border-slate-800/80 overflow-hidden">
          {loading ? (
            <div className="py-24 flex justify-center">
              <div className="w-8 h-8 border-t-2 border-indigo-500 rounded-full animate-spin"></div>
            </div>
          ) : candidates.length === 0 ? (
            <div className="py-24 text-center text-slate-500 text-sm">
              You haven't saved any candidates yet. Go to <a href="/ranking" className="text-indigo-400 hover:underline">Candidate Ranking</a> to bookmark profiles.
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
                          cand.rank === 2 ? "bg-slate-300/10 text-slate-300 border border-slate-300/20" :
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
                      <td className="py-4 px-6 text-right">
                        <span className="text-xs font-extrabold text-indigo-400">
                          {(cand.score * 100).toFixed(0)}%
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
                            onClick={(e) => handleUnsave(cand.candidate_id, e)}
                            className="p-2 hover:bg-rose-500/10 text-rose-400 hover:text-rose-300 rounded-lg border border-transparent hover:border-rose-500/20 transition-all"
                            title="Unsave Candidate"
                          >
                            <Heart className="w-4 h-4 fill-rose-400 text-rose-400" />
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

        {/* Candidate Detail Modal Overlay */}
        {selectedCandidateId && (
          <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-950/80 backdrop-blur-sm transition-all duration-300">
            <div className="w-full max-w-2xl h-screen bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col justify-between relative z-50">
              
              {/* Modal Header */}
              <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950/40">
                <div className="flex items-center gap-3">
                  <UserCheck className="w-5 h-5 text-indigo-400" />
                  <h3 className="font-bold text-slate-200">Candidate Deep-dive</h3>
                </div>
                <button 
                  onClick={handleCloseDetail}
                  className="p-2 hover:bg-slate-850 text-slate-400 hover:text-white rounded-lg transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Modal Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {modalLoading || !selectedCandidate ? (
                  <div className="h-full flex flex-col justify-center items-center gap-3 py-24">
                    <div className="w-8 h-8 border-t-2 border-indigo-500 rounded-full animate-spin"></div>
                    <span className="text-xs text-slate-500 font-medium">Reconstructing profile vectors...</span>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Candidate Identity Header */}
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <h2 className="text-xl font-bold text-white">{selectedCandidate.candidate_id}</h2>
                          <span className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded border ${
                            selectedCandidate.is_disqualified
                              ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                              : "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
                          }`}>
                            {selectedCandidate.is_disqualified ? "Disqualified" : `Rank #${selectedCandidate.rank}`}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
                          <Building className="w-3.5 h-3.5 text-slate-500" />
                          <span>{selectedCandidate.profile_data.profile?.current_title} at {selectedCandidate.profile_data.profile?.current_company || "Unknown"}</span>
                        </p>
                        <p className="text-[10px] text-slate-500 mt-1 flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-slate-500" />
                          <span>{selectedCandidate.profile_data.profile?.location}, {selectedCandidate.profile_data.profile?.country}</span>
                        </p>
                      </div>
                      
                      <div className="text-right">
                        <span className="text-2xl font-extrabold text-indigo-400">
                          {(selectedCandidate.score * 100).toFixed(0)}%
                        </span>
                        <p className="text-[10px] text-slate-500 mt-0.5 font-semibold uppercase tracking-wider">Composite Score</p>
                      </div>
                    </div>

                    {/* Disqualification / Alert Warning */}
                    {selectedCandidate.is_disqualified && (
                      <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex gap-3 items-start">
                        <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <h4 className="text-xs font-bold text-rose-400">Isolated Candidate Penalty Triggered</h4>
                          <p className="text-[11px] text-rose-300/80 leading-relaxed mt-1">{selectedCandidate.disqualification_reason || "Penalized for honeypot match / impossible attributes."}</p>
                        </div>
                      </div>
                    )}

                    {/* Radar Chart */}
                    <div className="p-4 bg-slate-950/40 border border-slate-850 rounded-2xl">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Hybrid Match Vectors</h4>
                      <div className="h-[220px] w-full flex justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={getRadarData()}>
                            <PolarGrid stroke="rgba(255, 255, 255, 0.05)" />
                            <PolarAngleAxis dataKey="subject" stroke="#64748b" fontSize={9} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="rgba(255, 255, 255, 0.1)" fontSize={8} />
                            <Radar 
                              name="Candidate" 
                              dataKey="value" 
                              stroke="#6366f1" 
                              fill="#6366f1" 
                              fillOpacity={0.25} 
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Reasoning Section */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-indigo-400" />
                        <span>System Recommendation Logic</span>
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/30 p-4 border border-slate-850 rounded-2xl">
                        {selectedCandidate.reasoning || "No system reasoning generated yet."}
                      </p>
                    </div>

                    {/* Skills list */}
                    <div className="space-y-2.5">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <Award className="w-4 h-4 text-indigo-400" />
                        <span>Validated Skills Inventory</span>
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {selectedCandidate.profile_data.skills?.map((skill: any) => (
                          <span 
                            key={skill.name} 
                            className="px-2.5 py-1 bg-slate-950 text-slate-300 border border-slate-800 text-[10px] font-semibold rounded-md hover:border-indigo-500/40 transition-all"
                          >
                            {skill.name} ({skill.level || "Proficient"})
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Career History */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <ListTodo className="w-4 h-4 text-indigo-400" />
                        <span>Career History Timeline</span>
                      </h4>
                      <div className="space-y-3">
                        {selectedCandidate.profile_data.career_history?.map((role: any, idx: number) => (
                          <div key={idx} className="p-3 bg-slate-950/20 border border-slate-850 rounded-xl">
                            <div className="flex justify-between items-start">
                              <h5 className="font-semibold text-xs text-slate-200">{role.title}</h5>
                              <span className="text-[9px] text-slate-500">{role.start_date} - {role.end_date || "Present"}</span>
                            </div>
                            <p className="text-[10px] text-indigo-400/80 font-medium mt-0.5">{role.company}</p>
                            <p className="text-[10px] text-slate-400 mt-2 leading-relaxed">{role.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Education */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <GraduationCap className="w-4 h-4 text-indigo-400" />
                        <span>Education</span>
                      </h4>
                      <div className="space-y-2">
                        {selectedCandidate.profile_data.education?.map((edu: any, idx: number) => (
                          <div key={idx} className="p-3 bg-slate-950/20 border border-slate-850 rounded-xl flex justify-between items-center">
                            <div>
                              <h5 className="font-semibold text-xs text-slate-200">{edu.degree} in {edu.field_of_study}</h5>
                              <p className="text-[10px] text-slate-500 mt-0.5">{edu.school}</p>
                            </div>
                            <span className="text-[9px] text-slate-500">{edu.start_date} - {edu.end_date}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="h-16 border-t border-slate-800 bg-slate-950/40 flex items-center justify-between px-6">
                <div className="flex items-center gap-4 text-slate-450 text-[10px]">
                  <div className="flex items-center gap-1">
                    <Mail className="w-3.5 h-3.5" />
                    <span>{selectedCandidate?.profile_data.profile?.email || "N/A"}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Phone className="w-3.5 h-3.5" />
                    <span>{selectedCandidate?.profile_data.profile?.phone || "N/A"}</span>
                  </div>
                </div>
                
                <button
                  onClick={(e) => selectedCandidate && handleUnsave(selectedCandidate.candidate_id, e)}
                  className="px-4 py-2 bg-rose-600/10 text-rose-400 border border-rose-500/20 rounded-xl font-medium text-xs hover:bg-rose-600 hover:text-white transition-all flex items-center gap-2"
                >
                  <Heart className="w-3.5 h-3.5 fill-current" />
                  <span>Unsave Profile</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
