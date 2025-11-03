import { useState } from 'react';
import { api } from '../api';

export default function ConceptDetails({ onMetadataUpdate }) {
  const [concept, setConcept] = useState('');
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showEdit, setShowEdit] = useState(false);
  const [editType, setEditType] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editExamples, setEditExamples] = useState('');

  const getConceptDetails = async () => {
    if (!concept) {
      setError('Please enter a concept name');
      return;
    }
    
    setLoading(true);
    setError(null);
    setShowEdit(false);
    try {
      const data = await api.getConcept(concept);
      if (data.error) {
        setError(data.error);
        setDetails(null);
      } else {
        setDetails(data);
        setEditType(data.metadata?.type || 'concept');
        setEditDesc(data.metadata?.description || '');
        setEditExamples(data.metadata?.examples?.join(', ') || '');
        setError(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      setDetails(null);
    } finally {
      setLoading(false);
    }
  };

  const submitMetadata = async () => {
    if (!concept) return;
    try {
      const examples = editExamples ? editExamples.split(',').map(s => s.trim()).filter(Boolean) : [];
      await api.updateMetadata(concept, editType || 'concept', editDesc, examples);
      setShowEdit(false);
      onMetadataUpdate && onMetadataUpdate();
      await getConceptDetails();
    } catch (err) {
      alert('Failed to update metadata: ' + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="query-section">
      <h2>Concept Details</h2>
      <div className="input-group">
        <input 
          type="text" 
          value={concept}
          onChange={(e) => setConcept(e.target.value)}
          placeholder="Enter concept name"
        />
        <button onClick={getConceptDetails} disabled={loading}>
          {loading ? 'Loading...' : 'Get Details'}
        </button>
      </div>
      <div className="results">
        {loading && <div className="loading">Loading details...</div>}
        {error && <div className="error">{error}</div>}
        {details && (
          <>
            <h3>{details.name}</h3>
            <div className="concept-card">
              <div className="concept-meta">Type: {details.metadata?.type || 'concept'}</div>
              {details.metadata?.description && (
                <p style={{ marginTop: '10px' }}>{details.metadata.description}</p>
              )}
              {details.metadata?.examples && details.metadata.examples.length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  <strong>Examples:</strong>
                  {details.metadata.examples.map((ex, idx) => (
                    <span key={idx} className="relation-badge" style={{ marginLeft: '5px' }}>{ex}</span>
                  ))}
                </div>
              )}
              <div style={{ marginTop: '12px' }}>
                <button onClick={() => setShowEdit(!showEdit)}>
                  {showEdit ? 'Cancel' : 'Edit Metadata'}
                </button>
              </div>
            </div>
            
            {showEdit && (
              <div className="concept-card" style={{ marginTop: '10px' }}>
                <div style={{ fontWeight: 600, color: '#667eea', marginBottom: '8px' }}>Edit Metadata</div>
                <div className="input-group">
                  <input 
                    value={editType}
                    onChange={(e) => setEditType(e.target.value)}
                    placeholder="type (e.g., concept, equation)"
                  />
                </div>
                <div className="input-group">
                  <input 
                    value={editDesc}
                    onChange={(e) => setEditDesc(e.target.value)}
                    placeholder="description"
                  />
                </div>
                <div className="input-group">
                  <input 
                    value={editExamples}
                    onChange={(e) => setEditExamples(e.target.value)}
                    placeholder="examples (comma-separated)"
                  />
                </div>
                <div className="input-group">
                  <button onClick={submitMetadata}>Save</button>
                  <button onClick={() => setShowEdit(false)} style={{ background: '#999' }}>Cancel</button>
                </div>
              </div>
            )}

            {details.outgoing && details.outgoing.length > 0 && (
              <div className="concept-card">
                <strong>Outgoing Relations:</strong><br />
                {details.outgoing.map((r, idx) => (
                  <span key={idx} className="relation-badge">{r}</span>
                ))}
              </div>
            )}
            
            {details.incoming && details.incoming.length > 0 && (
              <div className="concept-card">
                <strong>Incoming Relations:</strong><br />
                {details.incoming.map((r, idx) => (
                  <span key={idx} className="relation-badge">{r}</span>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

