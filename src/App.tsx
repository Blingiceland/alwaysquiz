import React from 'react';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <div className="background-gradient" />
      
      <div className="content-wrapper">
        <h1 className="title">leiðinlegt.is</h1>
        <p className="subtitle">Eitthvað alveg hræðilega leiðinlegt er í vinnslu...</p>
        
        <div className="game-placeholder">
          <span className="game-placeholder-text">Leikur Væntanlegur</span>
        </div>
      </div>
      
      <div className="footer">
        &copy; {new Date().getFullYear()} leiðinlegt.is
      </div>
    </div>
  );
}

export default App;
