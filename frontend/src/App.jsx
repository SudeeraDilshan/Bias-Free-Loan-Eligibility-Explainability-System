import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import LoanApplication from './pages/LoanApplication';
import PredictionResults from './pages/PredictionResults';
import Explainability from './pages/Explainability';
import Fairness from './pages/Fairness';
import About from './pages/About';
import { useState } from 'react';

function App() {
  const [prediction, setPrediction] = useState(null);

  return (
    <Router>
      <div className="app-container animate-fade-in">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<LoanApplication setPrediction={setPrediction} />} />
            <Route path="/results" element={<PredictionResults prediction={prediction} setPrediction={setPrediction} />} />
            <Route path="/explainability" element={<Explainability prediction={prediction} />} />
            <Route path="/fairness" element={<Fairness />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
