import { useState } from 'react';
import { api } from '../api';

export default function FindLoops({ onHighlightLoop }) {
  const [maxLength, setMaxLength] = useState('');
  const [maxCycles, setMaxCycles] = useState(200);
  const [loops, setLoops] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const findLoops = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (maxLength) params.append('max_length', maxLength);
      if (maxCycles) params.append('max_cycles', maxCycles);
      
      const data = await api.getLoops(params.toString());
      if (data.error) {
        setError(data.error);
        setLoops(null);
      } else {
        setLoops(data.loops || []);
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setLoops(null);
    } finally {
      setLoading(false);
    }
  };

  const handleHighlight = (loop) => {
    onHighlightLoop && onHighlightLoop(loop);
  };

  return (
    <div className="query-section">
      <h2>Find Loops</h2>
      <div className="input-group">
        <input 
          type="number" 
          value={maxLength}
          onChange={(e) => setMaxLength(e.target.value)}
          placeholder="Max length (optional)"
        />
        <input 
          type="number" 
          value={maxCycles}
          onChange={(e) => setMaxCycles(parseInt(e.target.value) || 200)}
          placeholder="Max cycles" 
        />
        <button onClick={findLoops} disabled={loading}>
          {loading ? 'Finding...' : 'Find'}
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Searching for loops...</div>}
        {error && <div className="error">{error}</div>}
        {loops && loops.length === 0 && <p>No loops found.</p>}
        {loops && loops.length > 0 && (
          <>
            <h3>Loops:</h3>
            {loops.map((lp, idx) => {
              const nodesStr = lp.nodes.join(' → ');
              const relsStr = (lp.relations || []).join(', ');
              return (
                <div key={idx} className="concept-card">
                  <div><strong>#{idx+1}</strong> {nodesStr}</div>
                  {relsStr && <div className="concept-meta">Relations: {relsStr}</div>}
                  <button 
                    style={{ marginTop: '8px' }}
                    onClick={() => handleHighlight(lp)}
                  >Highlight</button>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}

