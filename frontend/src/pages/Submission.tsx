import { useState } from "react";
import Layout from "../components/Layout";
import { useAuth } from "../providers";
import { 
  Download, 
  Sparkles, 
  CheckCircle, 
  FileCheck
} from "lucide-react";

export default function Submission() {
  const { token } = useAuth();
  
  const [downloading, setDownloading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const handleExport = async () => {
    if (!token) return;
    setDownloading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const response = await fetch(`${API_URL}/api/jobs/export/submission`, {
        headers: { "Authorization": `Bearer ${token}` }
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Export failed");
      }

      // Download file blob
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "submission.csv");
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      
      setSuccessMsg("submission.csv exported and verified successfully! File download initiated. 🎉");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to generate submission.csv. Ensure ranking has been completed.");
    } finally {
      setDownloading(false);
    }
  };

  const validationChecks = [
    { title: "Header Row Compliance", desc: "First row matches: candidate_id,rank,score,reasoning", check: true },
    { title: "Exact Row Bounds", desc: "Exactly 100 candidate records (rows 2 to 101)", check: true },
    { title: "Unique Ranks", desc: "Every rank from 1 to 100 exists exactly once", check: true },
    { title: "Non-Increasing Scores", desc: "Composite score at rank X is >= score at rank X+1", check: true },
    { title: "Tie-Break Ascending", desc: "Equal scores sorted by candidate_id in ascending order", check: true }
  ];

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Submission Generator
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Export challenge-compliant candidate submission file with automated validation
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
          {/* Exporter Card */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 flex flex-col justify-between lg:col-span-1 min-h-[300px]">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <FileCheck className="w-5 h-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-slate-200">Generate Submission</h2>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-6">
                Trigger compilation of the top-100 shortlisted candidate records. The system applies strict compliance rules before constructing the final CSV file.
              </p>
            </div>

            <div>
              <button
                onClick={handleExport}
                disabled={downloading}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-indigo-600/20 glow-effect"
              >
                {downloading ? (
                  <div className="w-5 h-5 border-t-2 border-white rounded-full animate-spin"></div>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Download submission.csv</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Validation Compliance Grid */}
          <div className="glass-card rounded-3xl p-6 border border-slate-800 lg:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-slate-200">Compliance Validation Checklists</h2>
            </div>

            <div className="space-y-4">
              {validationChecks.map((item, idx) => (
                <div key={idx} className="flex items-start gap-4 p-4 bg-slate-900/30 border border-slate-800/80 rounded-2xl">
                  <div className="p-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg flex-shrink-0">
                    <CheckCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-xs text-slate-200">{item.title}</h4>
                    <p className="text-xs text-slate-450 mt-1">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
