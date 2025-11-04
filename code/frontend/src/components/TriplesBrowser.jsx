import { useState, useEffect, useMemo } from 'react';
import { api } from '../api';
import TagSelector from './TagSelector';
import PredicateTag from './PredicateTag';

export default function TriplesBrowser({ refreshTrigger, onTripleChange }) {
  const [triples, setTriples] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [pageSize, setPageSize] = useState(50);
  const [relations, setRelations] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Sorting
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  
  // Filtering
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    subject: '',
    predicate: '',
    object: '',
    confidence: '',
    source: ''
  });
  
  // Add row
  const [editingRow, setEditingRow] = useState(false);
  const [newSubject, setNewSubject] = useState('');
  const [newPredicate, setNewPredicate] = useState('');
  const [newObject, setNewObject] = useState('');

  useEffect(() => {
    loadTriples();
    loadRelations();
  }, [page, pageSize, filters, refreshTrigger]);

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
      if (filters.predicate) params.append('relation', filters.predicate);
      
      const data = await api.getTriples(params.toString());
      let loadedTriples = data.triples || [];
      
      // Apply client-side filters (subject, object, confidence, source)
      if (filters.subject) {
        loadedTriples = loadedTriples.filter(t => 
          t.subject.toLowerCase().includes(filters.subject.toLowerCase())
        );
      }
      if (filters.object) {
        loadedTriples = loadedTriples.filter(t => 
          t.object.toLowerCase().includes(filters.object.toLowerCase())
        );
      }
      if (filters.confidence) {
        loadedTriples = loadedTriples.filter(t => 
          String(t.confidence || '').includes(filters.confidence)
        );
      }
      if (filters.source) {
        loadedTriples = loadedTriples.filter(t => 
          (t.source || '').toLowerCase().includes(filters.source.toLowerCase())
        );
      }
      
      setTriples(loadedTriples);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('Failed to load triples:', error);
    } finally {
      setLoading(false);
    }
  };

  // Sort triples
  const sortedTriples = useMemo(() => {
    if (!sortColumn) return triples;
    
    return [...triples].sort((a, b) => {
      let aVal = a[sortColumn] || '';
      let bVal = b[sortColumn] || '';
      
      // Handle numeric sorting for confidence
      if (sortColumn === 'confidence') {
        aVal = parseFloat(aVal) || 0;
        bVal = parseFloat(bVal) || 0;
      } else {
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
      }
      
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [triples, sortColumn, sortDirection]);

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (column) => {
    if (sortColumn !== column) return '↕';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const handleCreatePredicate = (newPredicate) => {
    // Add new predicate to relations list
    if (!relations.includes(newPredicate)) {
      setRelations([...relations, newPredicate]);
    }
  };

  const addTriple = async () => {
    if (!newSubject || !newPredicate || !newObject) {
      alert('Please fill subject, predicate, and object');
      return;
    }
    try {
      await api.addTriple(newSubject, newPredicate, newObject);
      setNewSubject('');
      setNewPredicate('');
      setNewObject('');
      setEditingRow(false);
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

  const clearFilters = () => {
    setFilters({
      subject: '',
      predicate: '',
      object: '',
      confidence: '',
      source: ''
    });
    setPage(1);
  };

  return (
    <div className="notion-table-container">
      {/* Filter Bar */}
      <div className="notion-table-toolbar">
        <div className="notion-table-toolbar-left">
          <button 
            className={`notion-table-filter-button ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filter
          </button>
          <span className="notion-table-count">{total} triples</span>
        </div>
        <div className="notion-table-toolbar-right">
          <input 
            type="number" 
            value={pageSize} 
            onChange={(e) => { setPageSize(parseInt(e.target.value) || 50); setPage(1); }}
            min="10" 
            max="200"
            className="notion-table-page-size"
            title="Rows per page"
          />
        </div>
      </div>

      {/* Expandable Filters */}
      {showFilters && (
        <div className="notion-table-filters">
          <div className="notion-filter-row">
            <div className="notion-filter-field">
              <label>Subject</label>
              <input 
                type="text"
                value={filters.subject}
                onChange={(e) => { setFilters({...filters, subject: e.target.value}); setPage(1); }}
                placeholder="Filter by subject..."
              />
            </div>
            <div className="notion-filter-field">
              <label>Predicate</label>
              <TagSelector
                value={filters.predicate}
                options={relations}
                onChange={(val) => { setFilters({...filters, predicate: val || ''}); setPage(1); }}
                onCreate={handleCreatePredicate}
                placeholder="All predicates"
              />
            </div>
            <div className="notion-filter-field">
              <label>Object</label>
              <input 
                type="text"
                value={filters.object}
                onChange={(e) => { setFilters({...filters, object: e.target.value}); setPage(1); }}
                placeholder="Filter by object..."
              />
            </div>
            <div className="notion-filter-field">
              <label>Confidence</label>
              <input 
                type="text"
                value={filters.confidence}
                onChange={(e) => { setFilters({...filters, confidence: e.target.value}); setPage(1); }}
                placeholder="Filter by confidence..."
              />
            </div>
            <div className="notion-filter-field">
              <label>Source</label>
              <input 
                type="text"
                value={filters.source}
                onChange={(e) => { setFilters({...filters, source: e.target.value}); setPage(1); }}
                placeholder="Filter by source..."
              />
            </div>
            <div className="notion-filter-actions">
              <button onClick={clearFilters}>Clear</button>
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="notion-table-wrapper">
        <table className="notion-table">
          <thead>
            <tr>
              <th 
                className={`notion-table-header sortable ${sortColumn === 'subject' ? 'active' : ''}`}
                onClick={() => handleSort('subject')}
              >
                <div className="notion-table-header-content">
                  <span>Subject</span>
                  <span className="sort-icon">{getSortIcon('subject')}</span>
                </div>
              </th>
              <th 
                className={`notion-table-header sortable ${sortColumn === 'predicate' ? 'active' : ''}`}
                onClick={() => handleSort('predicate')}
              >
                <div className="notion-table-header-content">
                  <span>Predicate</span>
                  <span className="sort-icon">{getSortIcon('predicate')}</span>
                </div>
              </th>
              <th 
                className={`notion-table-header sortable ${sortColumn === 'object' ? 'active' : ''}`}
                onClick={() => handleSort('object')}
              >
                <div className="notion-table-header-content">
                  <span>Object</span>
                  <span className="sort-icon">{getSortIcon('object')}</span>
                </div>
              </th>
              <th 
                className={`notion-table-header sortable ${sortColumn === 'confidence' ? 'active' : ''}`}
                onClick={() => handleSort('confidence')}
              >
                <div className="notion-table-header-content">
                  <span>Confidence</span>
                  <span className="sort-icon">{getSortIcon('confidence')}</span>
                </div>
              </th>
              <th 
                className={`notion-table-header sortable ${sortColumn === 'source' ? 'active' : ''}`}
                onClick={() => handleSort('source')}
              >
                <div className="notion-table-header-content">
                  <span>Source</span>
                  <span className="sort-icon">{getSortIcon('source')}</span>
                </div>
              </th>
              <th className="notion-table-header">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="6" className="notion-table-loading">
                  <div className="loading">Loading triples...</div>
                </td>
              </tr>
            ) : sortedTriples.length === 0 ? (
              <tr>
                <td colSpan="6" className="notion-table-empty">
                  <div className="muted">No triples found.</div>
                </td>
              </tr>
            ) : (
              sortedTriples.map((t, idx) => (
                <tr key={idx} className="notion-table-row">
                  <td>{t.subject}</td>
                  <td>
                    <PredicateTag predicate={t.predicate} />
                  </td>
                  <td>{t.object}</td>
                  <td className="muted">{t.confidence ?? ''}</td>
                  <td className="muted">{t.source ?? ''}</td>
                  <td className="notion-table-actions">
                    <button 
                      className="notion-table-delete-button"
                      onClick={() => removeTriple(t.subject, t.predicate, t.object)}
                      title="Delete"
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))
            )}
            
            {/* Add Row */}
            {editingRow ? (
              <tr className="notion-table-row notion-table-add-row">
                <td>
                  <input 
                    type="text"
                    value={newSubject}
                    onChange={(e) => setNewSubject(e.target.value)}
                    placeholder="Subject"
                    className="notion-table-input"
                    autoFocus
                  />
                </td>
                <td>
                  <TagSelector
                    value={newPredicate}
                    options={relations}
                    onChange={(val) => setNewPredicate(val)}
                    onCreate={handleCreatePredicate}
                    placeholder="Select or create predicate..."
                  />
                </td>
                <td>
                  <input 
                    type="text"
                    value={newObject}
                    onChange={(e) => setNewObject(e.target.value)}
                    placeholder="Object"
                    className="notion-table-input"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        addTriple();
                      } else if (e.key === 'Escape') {
                        setEditingRow(false);
                        setNewSubject('');
                        setNewPredicate('');
                        setNewObject('');
                      }
                    }}
                  />
                </td>
                <td></td>
                <td></td>
                <td className="notion-table-actions">
                  <button 
                    className="notion-table-save-button"
                    onClick={addTriple}
                    title="Save"
                  >
                    ✓
                  </button>
                  <button 
                    className="notion-table-cancel-button"
                    onClick={() => {
                      setEditingRow(false);
                      setNewSubject('');
                      setNewPredicate('');
                      setNewObject('');
                    }}
                    title="Cancel"
                  >
                    ×
                  </button>
                </td>
              </tr>
            ) : (
              <tr className="notion-table-row notion-table-add-row">
                <td colSpan="6" className="notion-table-add-cell">
                  <button 
                    className="notion-table-add-button"
                    onClick={() => setEditingRow(true)}
                  >
                    + Add a row
                  </button>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > pageSize && (
        <div className="notion-table-pagination">
          <button 
            disabled={page <= 1} 
            onClick={() => setPage(page - 1)}
            className="notion-table-pagination-button"
          >
            Previous
          </button>
          <span className="muted">
            Page {page} of {Math.max(1, Math.ceil(total / pageSize))}
          </span>
          <button 
            disabled={page >= Math.ceil(total / pageSize)} 
            onClick={() => setPage(page + 1)}
            className="notion-table-pagination-button"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
