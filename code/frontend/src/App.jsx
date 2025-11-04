import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Tabs, { Tab } from './components/Tabs';
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
import { api } from './api';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [relations, setRelations] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [currentFile, setCurrentFile] = useState(null);

  useEffect(() => {
    loadRelations();
    loadGraph();
    loadCurrentFile();
  }, [refreshTrigger]);

  const loadCurrentFile = async () => {
    try {
      const data = await api.getFiles();
      setCurrentFile(data.current || null);
    } catch (error) {
      console.error('Failed to load current file:', error);
    }
  };

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

  const handleFileSelect = () => {
    handleRefresh();
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
    <div className="app-layout">
      <header className="app-header">
        <h1>Knowledge Graph Explorer</h1>
        <p className="subtitle">Query and explore scientific concepts</p>
      </header>
      
      <div className="app-body">
        <Sidebar currentFile={currentFile} onFileSelect={handleFileSelect} />
        
        <div className="app-main">
          <Tabs defaultTab={0}>
            <Tab label="Triples">
              <div className="tab-page">
                <div style={{ marginBottom: '16px' }}>
                  <StatsDisplay refreshTrigger={refreshTrigger} />
                </div>
                <TriplesBrowser 
                  refreshTrigger={refreshTrigger} 
                  onTripleChange={handleRefresh}
                />
              </div>
            </Tab>
            
            <Tab label="Visualization">
              <div className="tab-page">
                <GraphVisualization 
                  graphData={graphData}
                  refreshTrigger={refreshTrigger}
                />
              </div>
            </Tab>
            
            <Tab label="Queries">
              <div className="tab-page">
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
              </div>
            </Tab>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

export default App;
