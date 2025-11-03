import { useState, useEffect } from 'react';
import { api } from '../api';

export default function FileSelector({ onFileChange }) {
  const [files, setFiles] = useState([]);
  const [current, setCurrent] = useState(null);
  const [selected, setSelected] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const data = await api.getFiles();
      setFiles(data.files || []);
      setCurrent(data.current || null);
      // Update selected value to match current file
      setSelected(data.current || (data.files && data.files.length > 0 ? data.files[0] : ''));
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const selectFile = async () => {
    if (!selected) return;
    
    setLoading(true);
    try {
      await api.selectFile(selected);
      setCurrent(selected);
      onFileChange && onFileChange();
      await loadFiles();
    } catch (error) {
      alert('Failed to load file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectChange = (e) => {
    setSelected(e.target.value);
  };

  return (
    <div className="panel" style={{ marginBottom: 0 }}>
      <div className="input-group" style={{ marginBottom: 0 }}>
        <select 
          id="file-select" 
          value={selected} 
          onChange={handleSelectChange}
          disabled={loading}
        >
          {files.map(f => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <button onClick={selectFile} disabled={loading || !selected}>
          {loading ? 'Loading...' : 'Load'}
        </button>
        <span className="muted">
          {current ? `Current: ${current}` : 'No file loaded'}
        </span>
      </div>
    </div>
  );
}

