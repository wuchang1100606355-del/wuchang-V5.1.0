import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Homepage from './pages/Homepage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-stone-50 text-stone-900 font-sans">
        <Routes>
          <Route path="/" element={<Homepage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
