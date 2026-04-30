import './App.css';

function App() {
  return (
    <div className="app-container">
      <div className="hero-section">
        <h1 className="title">LEIDINLEGT.IS</h1>
        <h2 className="subtitle">"Ertu klár?"</h2>
        
        <a href="/leikur/index.html" className="btn-start">BYRJA</a>
        
        <p className="small-text">
          10 spurningar.<br />
          Trump bíður.<br />
          Þorir þú?
        </p>
      </div>

      <div className="rules-section">
        <h2 className="rules-title">REGLURNAR</h2>
        <ul className="rules-list">
          <li>Reglurnar eru einfaldar...</li>
          <li>Ef þú nærð að svara 10 spurningum rétt í röð.. þá ertu búinn að vinna..</li>
          <li>Sá sem er fljótastur að svara 10 spurningum í maí fær 150 þúsund króna gjafabréf á Pablo Discobar</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
