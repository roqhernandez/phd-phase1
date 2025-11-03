import { useState } from 'react';
import { api } from '../api';

export default function Subgraph({ onRenderSubgraph }) {
  const [center, setCenter] = useState('');
  const [radius, setRadius] = useState(2);
  const [relations, setRelations] = useState('');
  const [direction, setDirection] = useState('both');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const renderSubgraph = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ radius: radius.toString(), direction });
      if (center) params.append('center', center);
      if (relations) params.append('relations', relations);
      
      const data = await api.getSubgraph(params.toString());
      setResult({ nodes: data.nodes.length, links: data.links.length });
      setError(null);
      onRenderSubgraph && onRenderSubgraph(data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const renderFullGraph = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getGraph();
      setResult({ nodes: data.nodes.length, links: data.links.length });
      setError(null);
      onRenderSubgraph && onRenderSubgraph(data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-section">
      <h2>Subgraph</h2>
      <div className="input-group">
        <input 
          type="text" 
          value={center}
          onChange={(e) => setCenter(e.target.value)}
          placeholder="Center concept (optional: leave empty for full)"
        />
        <input 
          type="number" 
          value={radius}
          onChange={(e) => setRadius(parseInt(e.target.value) || 2)}
          placeholder="Radius" 
          min="0" 
          max="10"
        />
      </div>
      <div className="input-group">
        <input 
          type="text" 
          value={relations}
          onChange={(e) => setRelations(e.target.value)}
          placeholder="Relations filter (comma-separated, optional)"
        />
        <select value={direction} onChange={(e) => setDirection(e.target.value)}>
          <option value="both">both</option>
          <option value="out">out</option>
          <option value="in">in</option>
        </select>
        <button onClick={renderSubgraph} disabled={loading}>
          {loading ? 'Rendering...' : 'Render'}
        </button>
        <button onClick={renderFullGraph} disabled={loading}>
          Show Full
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Loading subgraph...</div>}
        {error && <div className="error">{error}</div>}
        {result && (
          <div>Nodes: {result.nodes}, Links: {result.links}</div>
        )}
      </div>
    </div>
  );
}

