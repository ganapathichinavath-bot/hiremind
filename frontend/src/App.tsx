import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Providers from './providers';
import Landing from './pages/Landing';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import JobAnalysis from './pages/JobAnalysis';
import Ranking from './pages/Ranking';
import Submission from './pages/Submission';
import SavedCandidates from './pages/SavedCandidates';

function App() {
  return (
    <Providers>
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/job-analysis" element={<JobAnalysis />} />
          <Route path="/ranking" element={<Ranking />} />
          <Route path="/submission" element={<Submission />} />
          <Route path="/saved-candidates" element={<SavedCandidates />} />
        </Routes>
      </Router>
    </Providers>
  );
}



export default App;
