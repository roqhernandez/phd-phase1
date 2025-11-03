import { useState, useEffect } from 'react';
import { api } from '../api';

export default function GraphImage({ refreshTrigger }) {
  const [imageSrc, setImageSrc] = useState('');

  useEffect(() => {
    refreshImage();
  }, [refreshTrigger]);

  const refreshImage = () => {
    setImageSrc(api.getImage());
  };

  return (
    <div className="graph-image-container">
      <div className="graph-image-title">Static Image</div>
      <img 
        id="graphImage" 
        src={imageSrc} 
        alt="Knowledge Graph Visualization" 
        className="graph-image"
      />
    </div>
  );
}

