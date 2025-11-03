import { useState, useEffect } from 'react';
import FileSelector from './components/FileSelector';
import StatsDisplay from './components/StatsDisplay';
import TriplesBrowser from './components/TriplesBrowser';
import FindNeighbors from './components/FindNeighbors';
import FindPrerequisites from './components/FindPrerequisites';
import FindPath from './components/FindPath';
import ConceptDetails from './components/ConceptDetails';
import FindLoops from './components/FindLoops';
import LoopSimilarities from './components/LoopSimilarities';
import Subgraph from './components/Subgraph';
import GraphVisualization from './components/GraphVisualization';
import GraphImage from './components/GraphImage';
import { api } from './api';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [relations, setRelations] = useState([]);
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    loadRelations();
    loadGraph();
  }, [refreshTrigger]);

  const loadRelations = async () => {
    try {
      const stats = await api.getStats();
      setRelations(stats.relations || []);
    } catch (error) {
      console.error('Failed to load relations:', error);
    }
  };

  const loadGraph = async () => {
    try {
      const data = await api.getGraph();
      setGraphData(data);
    } catch (error) {
      console.error('Failed to load graph:', error);
    }
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const handleHighlightLoop = (loop) => {
    if (window.graphViz && window.graphViz.highlightLoop) {
      window.graphViz.highlightLoop(loop);
      window.graphViz.fitToGraph();
    }
  };

  const handleClearHighlights = () => {
    if (window.graphViz && window.graphViz.clearHighlights) {
      window.graphViz.clearHighlights();
    }
  };

  const handleRenderSubgraph = (data) => {
    setGraphData(data);
  };

  return (
    <div className="container">
      <header>
        <h1>Knowledge Graph Explorer</h1>
        <p className="subtitle">Query and explore scientific concepts</p>
      </header>
      
      <div className="content">
        <FileSelector onFileChange={handleRefresh} />
        
        <StatsDisplay refreshTrigger={refreshTrigger} />
        
        <TriplesBrowser 
          refreshTrigger={refreshTrigger} 
          onTripleChange={handleRefresh}
        />
        
        <FindNeighbors relations={relations} />
        
        <FindPrerequisites />
        
        <FindPath />
        
        <ConceptDetails onMetadataUpdate={handleRefresh} />
        
        <FindLoops onHighlightLoop={handleHighlightLoop} />
        
        <LoopSimilarities 
          onHighlightLoop={handleHighlightLoop}
          onClearHighlights={handleClearHighlights}
        />
        
        <Subgraph onRenderSubgraph={handleRenderSubgraph} />
        
        <GraphVisualization 
          graphData={graphData}
          refreshTrigger={refreshTrigger}
        />
        
        <GraphImage refreshTrigger={refreshTrigger} />
      </div>
    </div>
  );
}

export default App;
