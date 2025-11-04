import { useState, useEffect, useRef } from 'react';
import { api } from '../api';

export default function Sidebar({ currentFile, onFileSelect }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [openMenu, setOpenMenu] = useState(null); // Track which file's menu is open
  const [renamingFile, setRenamingFile] = useState(null); // Track which file is being renamed
  const [renameValue, setRenameValue] = useState('');
  const menuRef = useRef(null);
  const renameInputRef = useRef(null);

  useEffect(() => {
    loadFiles();
  }, [currentFile]);

  useEffect(() => {
    // Close menu when clicking outside
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpenMenu(null);
      }
    };
    if (openMenu !== null) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [openMenu]);

  useEffect(() => {
    // Focus rename input when entering rename mode
    if (renamingFile && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [renamingFile]);

  const loadFiles = async () => {
    try {
      const data = await api.getFiles();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const selectFile = async (filename) => {
    if (!filename || filename === currentFile || renamingFile) return;
    
    setLoading(true);
    try {
      await api.selectFile(filename);
      onFileSelect && onFileSelect();
      await loadFiles();
    } catch (error) {
      alert('Failed to load file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleAddFile = async () => {
    setLoading(true);
    try {
      const result = await api.createFile();
      await loadFiles();
      // Automatically select the new file
      if (result.filename) {
        await api.selectFile(result.filename);
        onFileSelect && onFileSelect();
      }
    } catch (error) {
      alert('Failed to create file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleMenuClick = (e, filename) => {
    e.stopPropagation(); // Prevent file selection
    setOpenMenu(openMenu === filename ? null : filename);
  };

  const handleRename = async (oldName) => {
    if (!renameValue.trim()) {
      setRenamingFile(null);
      setRenameValue('');
      return;
    }
    
    // Remove .json extension if user typed it
    let newName = renameValue.trim();
    if (newName.endsWith('.json')) {
      newName = newName.slice(0, -5);
    }
    
    setLoading(true);
    try {
      await api.renameFile(oldName, newName);
      await loadFiles();
      // Update current file if it was renamed
      if (currentFile === oldName) {
        onFileSelect && onFileSelect();
      }
    } catch (error) {
      alert('Failed to rename file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      setRenamingFile(null);
      setRenameValue('');
      setOpenMenu(null);
    }
  };

  const handleDelete = async (filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }
    
    setLoading(true);
    try {
      await api.deleteFile(filename);
      await loadFiles();
      // If deleted file was current, refresh
      if (currentFile === filename) {
        onFileSelect && onFileSelect();
      }
    } catch (error) {
      alert('Failed to delete file: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
      setOpenMenu(null);
    }
  };

  const startRename = (filename) => {
    const nameWithoutExt = filename.replace(/\.json$/, '');
    setRenameValue(nameWithoutExt);
    setRenamingFile(filename);
    setOpenMenu(null);
  };

  const handleRenameKeyDown = (e, oldName) => {
    if (e.key === 'Enter') {
      handleRename(oldName);
    } else if (e.key === 'Escape') {
      setRenamingFile(null);
      setRenameValue('');
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-title-row">
          <div className="sidebar-title">KG Files</div>
          <button 
            className="sidebar-add-button"
            onClick={handleAddFile}
            title="Add new file"
            disabled={loading}
          >
            +
          </button>
        </div>
      </div>
      <div className="sidebar-content">
        {files.length === 0 ? (
          <div className="sidebar-empty">No files available</div>
        ) : (
          <div className="file-list">
            {files.map((file) => (
              <div
                key={file}
                className={`file-item ${file === currentFile ? 'active' : ''}`}
                onClick={() => !renamingFile && selectFile(file)}
              >
                {renamingFile === file ? (
                  <input
                    ref={renameInputRef}
                    type="text"
                    className="file-item-rename-input"
                    value={renameValue}
                    onChange={(e) => setRenameValue(e.target.value)}
                    onBlur={() => handleRename(file)}
                    onKeyDown={(e) => handleRenameKeyDown(e, file)}
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <>
                    <div className="file-item-name">{file}</div>
                    <div className="file-item-actions">
                      {file === currentFile && (
                        <div className="file-item-check">✓</div>
                      )}
                      <button
                        className="file-item-menu-button"
                        onClick={(e) => handleMenuClick(e, file)}
                        title="File options"
                      >
                        ⋯
                      </button>
                      {openMenu === file && (
                        <div 
                          ref={menuRef}
                          className="file-item-menu"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            className="file-item-menu-option"
                            onClick={() => startRename(file)}
                          >
                            Rename
                          </button>
                          <button
                            className="file-item-menu-option file-item-menu-option-danger"
                            onClick={() => handleDelete(file)}
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
        {loading && (
          <div className="sidebar-loading">Loading...</div>
        )}
      </div>
    </div>
  );
}

