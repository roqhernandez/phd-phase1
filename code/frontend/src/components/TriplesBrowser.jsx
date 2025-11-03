import { useState, useEffect } from 'react';
import { api } from '../api';

export default function TriplesBrowser({ refreshTrigger, onTripleChange }) {
  const [triples, setTriples] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [relationFilter, setRelationFilter] = useState('');
  const [relations, setRelations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [subject, setSubject] = useState('');
  const [predicate, setPredicate] = useState('');
  const [object, setObject] = useState('');
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    loadTriples();
    loadRelations();
  }, [page, pageSize, relationFilter, refreshTrigger]);

  useEffect(() => {
    loadRelations();
  }, [refreshTrigger]);

  const loadRelations = async () => {
    try {
      const stats = await api.getStats();
      setRelations(stats.relations || []);
    } catch (error) {
      console.error('Failed to load relations:', error);
    }
  };

  const loadTriples = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      if (relationFilter) params.append('relation', relationFilter);
      
      const data = await api.getTriples(params.toString());
      setTriples(data.triples || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('Failed to load triples:', error);
    } finally {
      setLoading(false);
    }
  };

  const addTriple = async () => {
    if (!subject || !predicate || !object) {
      alert('Please fill subject, predicate, and object');
      return;
    }
    try {
      await api.addTriple(subject, predicate, object);
      setSubject('');
      setPredicate('');
      setObject('');
      onTripleChange && onTripleChange();
      await loadTriples();
    } catch (error) {
      alert('Failed to add triple: ' + (error.response?.data?.error || error.message));
    }
  };

  const removeTriple = async (s, p, o) => {
    if (!confirm(`Remove triple: ${s} ${p} ${o}?`)) return;
    try {
      await api.removeTriple(s, p, o);
      onTripleChange && onTripleChange();
      await loadTriples();
    } catch (error) {
      alert('Failed to remove triple: ' + (error.response?.data?.error || error.message));
    }
  };

  if (collapsed) {
    return (
      <div className="query-section">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
          <h2 style={{ margin: 0 }}>Browse Triples</h2>
          <button onClick={() => setCollapsed(false)}>Expand</button>
        </div>
      </div>
    );
  }

  return (
    <div className="query-section">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
        <h2 style={{ margin: 0 }}>Browse Triples</h2>
        <button onClick={() => setCollapsed(true)}>Collapse</button>
      </div>
      <div>
        <div className="input-group" style={{ marginTop: '12px' }}>
          <select 
            value={relationFilter} 
            onChange={(e) => { setRelationFilter(e.target.value); setPage(1); }}
          >
            <option value="">All relations</option>
            {relations.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          <input 
            type="number" 
            value={pageSize} 
            onChange={(e) => { setPageSize(parseInt(e.target.value) || 20); setPage(1); }}
            min="5" 
            max="200" 
            placeholder="Page size"
          />
          <button onClick={() => loadTriples()}>Refresh</button>
        </div>
        <div className="input-group" style={{ marginBottom: 0 }}>
          <input 
            type="text" 
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="subject"
          />
          <input 
            type="text" 
            value={predicate}
            onChange={(e) => setPredicate(e.target.value)}
            placeholder="predicate"
          />
          <input 
            type="text" 
            value={object}
            onChange={(e) => setObject(e.target.value)}
            placeholder="object"
          />
          <button onClick={addTriple}>Add</button>
        </div>
        {loading ? (
          <div className="loading">Loading triples...</div>
        ) : (
          <div className="results">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="muted">Total: {total} triples</div>
              <div className="pagination">
                <button 
                  disabled={page <= 1} 
                  onClick={() => setPage(page - 1)}
                >Prev</button>
                <span className="muted">Page {page} / {Math.max(1, Math.ceil(total / pageSize))}</span>
                <button 
                  disabled={page >= Math.ceil(total / pageSize)} 
                  onClick={() => setPage(page + 1)}
                >Next</button>
              </div>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Predicate</th>
                  <th>Object</th>
                  <th>Conf.</th>
                  <th>Source</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {triples.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="muted">No triples on this page.</td>
                  </tr>
                ) : (
                  triples.map((t, idx) => (
                    <tr key={idx}>
                      <td>{t.subject}</td>
                      <td><span className="relation-badge">{t.predicate}</span></td>
                      <td>{t.object}</td>
                      <td className="muted">{t.confidence ?? ''}</td>
                      <td className="muted">{t.source ?? ''}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button 
                          style={{ background: '#c0392b' }}
                          onClick={() => removeTriple(t.subject, t.predicate, t.object)}
                        >Remove</button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

