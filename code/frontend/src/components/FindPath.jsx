import { useState } from 'react';
import { api } from '../api';

export default function FindPath() {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const findPath = async () => {
    if (!start || !end) {
      setError('Please enter both start and end concepts');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPath(start, end);
      if (data.error) {
        setError(data.error);
        setPath(null);
      } else if (!data.path) {
        setError('No path found between these concepts');
        setPath(null);
      } else {
        setPath(data.path);
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setPath(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-section">
      <h2>Find Learning Path</h2>
      <div className="input-group">
        <input 
          type="text" 
          value={start}
          onChange={(e) => setStart(e.target.value)}
          placeholder="Start concept"
        />
        <input 
          type="text" 
          value={end}
          onChange={(e) => setEnd(e.target.value)}
          placeholder="End concept"
        />
        <button onClick={findPath} disabled={loading}>
          {loading ? 'Finding...' : 'Find Path'}
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Finding path...</div>}
        {error && <div className="error">{error}</div>}
        {path && path.length > 0 && (
          <>
            <h3>Learning Path:</h3>
            <div className="concept-card">
              {path.map((step, i) => (
                <span key={i}>
                  {i > 0 && <span className="path-arrow">→</span>}
                  <span className="concept-name">{step}</span>
                </span>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

