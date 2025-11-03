import { useState, useEffect } from 'react';
import { api } from '../api';

export default function FileSelector({ onFileChange }) {
  const [files, setFiles] = useState([]);
  const [current, setCurrent] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const data = await api.getFiles();
      setFiles(data.files || []);
      setCurrent(data.current || null);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const selectFile = async () => {
    const select = document.getElementById('file-select');
    const name = select?.value;
    if (!name) return;
    
    setLoading(true);
    try {
      await api.selectFile(name);
      setCurrent(name);
      onFileChange && onFileChange();
      await loadFiles();
    } catch (error) {
      alert('Failed to load file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel" style={{ marginBottom: 0 }}>
      <div className="input-group" style={{ marginBottom: 0 }}>
        <select id="file-select" value={current || ''} onChange={(e) => {}}>
          {files.map(f => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <button onClick={selectFile} disabled={loading}>
          {loading ? 'Loading...' : 'Load'}
        </button>
        <span className="muted">
          {current ? `Current: ${current}` : 'No file loaded'}
        </span>
      </div>
    </div>
  );
}

