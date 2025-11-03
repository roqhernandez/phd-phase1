import { useState } from 'react';
import { api } from '../api';

export default function LoopSimilarities({ onHighlightLoop, onClearHighlights }) {
  const [minNodeJ, setMinNodeJ] = useState(0.5);
  const [minRelJ, setMinRelJ] = useState(0.5);
  const [maxLength, setMaxLength] = useState('');
  const [maxCycles, setMaxCycles] = useState(200);
  const [pairs, setPairs] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const findLoopSimilarities = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        min_node_jaccard: minNodeJ.toString(),
        min_relation_jaccard: minRelJ.toString(),
        max_cycles: maxCycles.toString(),
      });
      if (maxLength) params.append('max_length', maxLength);
      
      const data = await api.getLoopSimilarities(params.toString());
      if (data.error) {
        setError(data.error);
        setPairs(null);
      } else {
        setPairs(data.pairs || []);
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setPairs(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-section">
      <h2>Loop Similarities</h2>
      <div className="input-group">
        <input 
          type="number" 
          value={minNodeJ}
          onChange={(e) => setMinNodeJ(parseFloat(e.target.value) || 0.5)}
          placeholder="Min node Jaccard" 
          step="0.05" 
          min="0" 
          max="1"
        />
        <input 
          type="number" 
          value={minRelJ}
          onChange={(e) => setMinRelJ(parseFloat(e.target.value) || 0.5)}
          placeholder="Min relation Jaccard" 
          step="0.05" 
          min="0" 
          max="1"
        />
      </div>
      <div className="input-group">
        <input 
          type="number" 
          value={maxLength}
          onChange={(e) => setMaxLength(e.target.value)}
          placeholder="Max loop length (optional)"
        />
        <input 
          type="number" 
          value={maxCycles}
          onChange={(e) => setMaxCycles(parseInt(e.target.value) || 200)}
          placeholder="Max cycles" 
        />
        <button onClick={findLoopSimilarities} disabled={loading}>
          {loading ? 'Computing...' : 'Compare'}
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Computing similarities...</div>}
        {error && <div className="error">{error}</div>}
        {pairs && pairs.length === 0 && <p>No similar loop pairs found.</p>}
        {pairs && pairs.length > 0 && (
          <>
            <h3>Similar Loop Pairs:</h3>
            {pairs.map((p, idx) => {
              const nscore = p.node_jaccard.toFixed(2);
              const rscore = p.relation_jaccard.toFixed(2);
              const l1 = p.loop_i.nodes.join(' → ');
              const l2 = p.loop_j.nodes.join(' → ');
              return (
                <div key={idx} className="concept-card">
                  <div><strong>#{idx+1}</strong> NodeJ={nscore}, RelJ={rscore}</div>
                  <div className="concept-meta">Loop A: {l1}</div>
                  <div className="concept-meta">Loop B: {l2}</div>
                  <div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
                    <button onClick={() => onHighlightLoop && onHighlightLoop(p.loop_i)}>Highlight A</button>
                    <button onClick={() => onHighlightLoop && onHighlightLoop(p.loop_j)}>Highlight B</button>
                    <button onClick={() => onClearHighlights && onClearHighlights()}>Clear</button>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>
    </div>
  );
}

