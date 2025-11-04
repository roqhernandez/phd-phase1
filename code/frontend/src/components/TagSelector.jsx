import { useState, useEffect, useRef } from 'react';

// Notion's color palette for tags/labels
const NOTION_COLORS = [
  { name: 'gray', bg: 'rgba(235, 236, 237, 1)', text: 'rgba(55, 53, 47, 0.8)', border: 'rgba(55, 53, 47, 0.16)' },
  { name: 'brown', bg: 'rgba(238, 224, 218, 1)', text: 'rgba(141, 103, 71, 1)', border: 'rgba(141, 103, 71, 0.3)' },
  { name: 'orange', bg: 'rgba(250, 222, 201, 1)', text: 'rgba(217, 115, 13, 1)', border: 'rgba(217, 115, 13, 0.3)' },
  { name: 'yellow', bg: 'rgba(253, 236, 200, 1)', text: 'rgba(203, 145, 47, 1)', border: 'rgba(203, 145, 47, 0.3)' },
  { name: 'green', bg: 'rgba(219, 237, 219, 1)', text: 'rgba(68, 131, 97, 1)', border: 'rgba(68, 131, 97, 0.3)' },
  { name: 'blue', bg: 'rgba(211, 229, 239, 1)', text: 'rgba(30, 102, 140, 1)', border: 'rgba(30, 102, 140, 0.3)' },
  { name: 'purple', bg: 'rgba(232, 222, 238, 1)', text: 'rgba(133, 96, 136, 1)', border: 'rgba(133, 96, 136, 0.3)' },
  { name: 'pink', bg: 'rgba(245, 224, 233, 1)', text: 'rgba(193, 76, 138, 1)', border: 'rgba(193, 76, 138, 0.3)' },
  { name: 'red', bg: 'rgba(255, 226, 221, 1)', text: 'rgba(225, 97, 89, 1)', border: 'rgba(225, 97, 89, 0.3)' },
];

// Assign color to a tag based on its hash
const getTagColor = (tagName) => {
  if (!tagName) return NOTION_COLORS[0];
  // Simple hash function to consistently assign colors
  let hash = 0;
  for (let i = 0; i < tagName.length; i++) {
    hash = tagName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % NOTION_COLORS.length;
  return NOTION_COLORS[index];
};

export default function TagSelector({ value, options = [], onChange, onCreate, placeholder = "Select or create..." }) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [inputValue, setInputValue] = useState(value || '');
  const containerRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen, searchTerm]);

  const filteredOptions = options.filter(opt => 
    opt.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const canCreate = searchTerm && !options.includes(searchTerm) && !filteredOptions.includes(searchTerm);

  const handleSelect = (option) => {
    setInputValue(option);
    setSearchTerm('');
    setIsOpen(false);
    onChange && onChange(option);
  };

  const handleCreate = () => {
    if (canCreate && onCreate) {
      onCreate(searchTerm);
      setInputValue(searchTerm);
      setSearchTerm('');
      setIsOpen(false);
      onChange && onChange(searchTerm);
    }
  };

  const handleClear = () => {
    setInputValue('');
    setSearchTerm('');
    setIsOpen(false);
    onChange && onChange('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredOptions.length > 0) {
        handleSelect(filteredOptions[0]);
      } else if (canCreate) {
        handleCreate();
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setSearchTerm('');
      if (!inputValue) {
        handleClear();
      }
    } else if (e.key === 'Backspace' && !searchTerm && inputValue) {
      // If backspace on empty search, clear the value
      handleClear();
    }
  };

  const currentColor = getTagColor(inputValue);

  return (
    <div className="tag-selector" ref={containerRef}>
      {!isOpen && inputValue && inputValue.trim() ? (
        <div 
          className="tag-selector-tag"
          style={{
            backgroundColor: currentColor.bg,
            color: currentColor.text,
            borderColor: currentColor.border,
          }}
          onClick={() => setIsOpen(true)}
        >
          <span>{inputValue}</span>
          <button 
            className="tag-selector-clear"
            onClick={(e) => {
              e.stopPropagation();
              handleClear();
            }}
            title="Clear"
          >
            ×
          </button>
        </div>
      ) : (
        <input
          ref={inputRef}
          type="text"
          className="tag-selector-input"
          value={isOpen ? searchTerm : inputValue}
          onChange={(e) => {
            const val = e.target.value;
            if (!isOpen) {
              setIsOpen(true);
            }
            setSearchTerm(val);
            setInputValue(val);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
        />
      )}
      
      {isOpen && (
        <div className="tag-selector-dropdown">
          {filteredOptions.length > 0 && (
            <div className="tag-selector-options">
              {filteredOptions.map((option) => {
                const color = getTagColor(option);
                return (
                  <div
                    key={option}
                    className="tag-selector-option"
                    onClick={() => handleSelect(option)}
                  >
                    <span 
                      className="tag-selector-option-color"
                      style={{
                        backgroundColor: color.bg,
                        borderColor: color.border,
                      }}
                    />
                    <span>{option}</span>
                  </div>
                );
              })}
            </div>
          )}
          
          {canCreate && (
            <div className="tag-selector-create">
              <div 
                className="tag-selector-create-option"
                onClick={handleCreate}
              >
                <span className="tag-selector-create-icon">+</span>
                <span>Create "{searchTerm}"</span>
              </div>
            </div>
          )}
          
          {filteredOptions.length === 0 && !canCreate && searchTerm && (
            <div className="tag-selector-empty">
              <span className="muted">No matches found</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

