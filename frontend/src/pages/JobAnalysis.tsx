import React, { useState } from "react";
import Layout from "../components/Layout";
import { useAuth } from "../providers";
import { useNavigate } from "react-router-dom";
import { 
  FileText, 
  UploadCloud, 
  Sparkles, 
  Briefcase, 
  Cpu, 
  GraduationCap, 
  Award,
  ListTodo,
  CheckCircle,
  Play
} from "lucide-react";

export default function JobAnalysis() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [jdData, setJdData] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [ranking, setRanking] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/^http:\/\/(?!localhost|127\.0\.0\.1)/, "https://");

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !token) return;
    const file = e.target.files[0];

    setUploading(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    setJdData(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/jobs/upload`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Failed to upload JD");

      setJdData(data);
      setSuccessMsg("Job description parsed successfully! 🎉");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process job description");
    } finally {
      setUploading(false);
    }
  };

  const handleRunRanker = async () => {
    if (!token) return;
    setRanking(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const response = await fetch(`${API_URL}/api/jobs/rank`, {
        method: "POST",
        headers: { 
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ top_k: 100 }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Ranking failed");

      setSuccessMsg(`Ranked ${data.total_candidates} candidates! Redirecting... 🚀`);
      setTimeout(() => {
        navigate("/ranking");
      }, 1500);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to rank candidates");
    } finally {
      setRanking(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Job Description Analysis
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Ingest and parse target job requirements to generate semantic anchors
          </p>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {errorMsg}
          </div>
        )}

        {successMsg && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>{successMsg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Widget */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between lg:col-span-1 min-h-[300px]">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <UploadCloud className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-slate-200">Ingest Job Profile</h2>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-6">
                Upload target job profile (DOCX or text). The system will extract semantic markers, skills taxonomy, experience targets, and certification requirements.
              </p>
            </div>

            <div className="space-y-4">
              <label className={`w-full flex flex-col items-center justify-center border-2 border-dashed rounded-2xl py-8 px-4 text-center cursor-pointer transition-all ${
                uploading 
                  ? "border-indigo-500/40 bg-indigo-500/5 cursor-not-allowed" 
                  : "border-slate-800 bg-slate-950 hover:border-slate-700 hover:bg-slate-900"
              }`}>
                {uploading ? (
                  <>
                    <div className="w-6 h-6 border-t-2 border-indigo-500 rounded-full animate-spin mb-3"></div>
                    <span className="text-xs font-medium text-slate-300">Extracting syntax...</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-8 h-8 text-slate-500 mb-3" />
                    <span className="text-xs font-semibold text-slate-300">Select job_description.docx</span>
                    <span className="text-[10px] text-slate-500 mt-1">DOCX, Text format accepted</span>
                    <input 
                      type="file" 
                      accept=".docx,.txt" 
                      onChange={handleFileUpload} 
                      className="hidden" 
                      disabled={uploading}
                    />
                  </>
                )}
              </label>

              {jdData && (
                <button
                  onClick={handleRunRanker}
                  disabled={ranking}
                  className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/20 glow-effect"
                >
                  {ranking ? (
                    <div className="w-5 h-5 border-t-2 border-white rounded-full animate-spin"></div>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-white" />
                      <span>Rank Candidate Pool</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>

          {/* Analysis View Panel */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 lg:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-slate-200">Extracted System Criteria</h2>
            </div>

            {!jdData ? (
              <div className="py-24 text-center text-slate-500 text-xs">
                No job description uploaded yet. Use the left widget to ingest a job description file.
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Job Title</span>
                  <h3 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-indigo-400" />
                    <span>{jdData.title}</span>
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Experience */}
                  <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl">
                    <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      <Cpu className="w-4 h-4 text-indigo-400" />
                      <span>Experience Band Target</span>
                    </div>
                    <p className="text-sm font-semibold text-slate-200">{jdData.extracted_experience || "None parsed"}</p>
                  </div>

                  {/* Education */}
                  <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-2xl">
                    <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      <GraduationCap className="w-4 h-4 text-indigo-400" />
                      <span>Education Requirements</span>
                    </div>
                    <p className="text-sm font-semibold text-slate-200 truncate">{jdData.extracted_education || "None parsed"}</p>
                  </div>
                </div>

                {/* Skills Grid */}
                <div>
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    <Award className="w-4 h-4 text-indigo-400" />
                    <span>Extracted Core Skills</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {jdData.extracted_skills?.map((skill: string) => (
                      <span 
                        key={skill} 
                        className="px-3 py-1.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-semibold rounded-lg"
                      >
                        {skill}
                      </span>
                    ))}
                    {(!jdData.extracted_skills || jdData.extracted_skills.length === 0) && (
                      <span className="text-xs text-slate-500">None parsed</span>
                    )}
                  </div>
                </div>

                {/* Responsibilities list */}
                <div>
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    <ListTodo className="w-4 h-4 text-indigo-400" />
                    <span>Extracted Roles & Responsibilities</span>
                  </div>
                  <ul className="space-y-2">
                    {jdData.extracted_responsibilities?.map((item: string, idx: number) => (
                      <li key={idx} className="flex gap-2.5 items-start text-xs text-slate-400 leading-relaxed">
                        <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-1.5 flex-shrink-0"></span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
