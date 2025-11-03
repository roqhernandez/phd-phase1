import { useState } from 'react';
import { api } from '../api';

export default function FindPrerequisites() {
  const [concept, setConcept] = useState('');
  const [depth, setDepth] = useState(3);
  const [prerequisites, setPrerequisites] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const findPrerequisites = async () => {
    if (!concept) {
      setError('Please enter a concept name');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPrerequisites(concept, depth);
      if (data.error) {
        setError(data.error);
        setPrerequisites(null);
      } else {
        setPrerequisites(data.prerequisites || []);
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setPrerequisites(null);
    } finally {
      setLoading(false);
    }
  };

  const byDepth = {};
  if (prerequisites) {
    prerequisites.forEach(([prereq, d]) => {
      if (!byDepth[d]) byDepth[d] = [];
      byDepth[d].push(prereq);
    });
  }

  return (
    <div className="query-section">
      <h2>Find Prerequisites</h2>
      <div className="input-group">
        <input 
          type="text" 
          value={concept}
          onChange={(e) => setConcept(e.target.value)}
          placeholder="Enter concept name"
        />
        <input 
          type="number" 
          value={depth}
          onChange={(e) => setDepth(parseInt(e.target.value) || 3)}
          placeholder="Max depth" 
          min="1" 
          max="10"
        />
        <button onClick={findPrerequisites} disabled={loading}>
          {loading ? 'Finding...' : 'Find Path'}
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Finding prerequisites...</div>}
        {error && <div className="error">{error}</div>}
        {prerequisites && prerequisites.length === 0 && <p>No prerequisites found</p>}
        {prerequisites && prerequisites.length > 0 && (
          <>
            <h3>Learning Prerequisites:</h3>
            {Object.keys(byDepth).sort().map(d => (
              <div key={d} className="concept-card">
                <div className="concept-meta">Level {d}:</div>
                {byDepth[d].map((p, idx) => (
                  <span key={idx} className="relation-badge">{p}</span>
                ))}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}

