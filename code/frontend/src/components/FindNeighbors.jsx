import { useState } from 'react';
import { api } from '../api';

export default function FindNeighbors({ relations }) {
  const [concept, setConcept] = useState('');
  const [relation, setRelation] = useState('');
  const [neighbors, setNeighbors] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const findNeighbors = async () => {
    if (!concept) {
      setError('Please enter a concept name');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const data = await api.getNeighbors(concept, relation);
      if (data.error) {
        setError(data.error);
        setNeighbors(null);
      } else {
        setNeighbors(data.neighbors || []);
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setNeighbors(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-section">
      <h2>Find Neighbors</h2>
      <div className="input-group">
        <input 
          type="text" 
          value={concept}
          onChange={(e) => setConcept(e.target.value)}
          placeholder="Enter concept name (e.g., 'wave')"
        />
        <select value={relation} onChange={(e) => setRelation(e.target.value)}>
          <option value="">All relations</option>
          {relations.map(r => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <button onClick={findNeighbors} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Searching...</div>}
        {error && <div className="error">{error}</div>}
        {neighbors && neighbors.length === 0 && <p>No neighbors found</p>}
        {neighbors && neighbors.length > 0 && (
          <>
            <h3>Connected Concepts:</h3>
            {neighbors.map((n, idx) => (
              <div key={idx} className="concept-card">
                <div className="concept-name">{n}</div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}

