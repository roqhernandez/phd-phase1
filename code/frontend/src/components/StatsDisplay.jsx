import { useState, useEffect } from 'react';
import { api } from '../api';

export default function StatsDisplay({ refreshTrigger }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
  }, [refreshTrigger]);

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  if (!stats) return <div className="loading">Loading statistics...</div>;

  return (
    <div className="stats">
      <div className="stat-card">
        <div className="stat-number" id="nodeCount">{stats.nodes}</div>
        <div className="stat-label">Nodes</div>
      </div>
      <div className="stat-card">
        <div className="stat-number" id="edgeCount">{stats.edges}</div>
        <div className="stat-label">Edges</div>
      </div>
      <div className="stat-card">
        <div className="stat-number" id="relationTypeCount">{stats.relation_types}</div>
        <div className="stat-label">Relation Types</div>
      </div>
    </div>
  );
}

