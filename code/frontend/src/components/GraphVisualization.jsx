import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { api } from '../api';

export default function GraphVisualization({ graphData, refreshTrigger }) {
  const svgRef = useRef(null);
  const simulationRef = useRef(null);
  const zoomBehaviorRef = useRef(null);
  const gLayerRef = useRef(null);
  const nodesRef = useRef(null);
  const linksRef = useRef(null);
  const linkLabelsRef = useRef(null);
  const nodeLabelsRef = useRef(null);
  const currentDataRef = useRef(null);

  useEffect(() => {
    if (graphData) {
      renderD3(graphData);
      currentDataRef.current = graphData;
    } else {
      loadAndRender();
    }
  }, [graphData, refreshTrigger]);

  useEffect(() => {
    const handleResize = () => {
      if (currentDataRef.current) {
        renderD3(currentDataRef.current);
      } else {
        loadAndRender();
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadAndRender = async () => {
    try {
      const data = await api.getGraph();
      renderD3(data);
      currentDataRef.current = data;
    } catch (error) {
      console.error('Failed to load graph:', error);
    }
  };

  const renderD3 = (data) => {
    const svg = d3.select(svgRef.current);
    if (!svg.node()) return;
    
    svg.selectAll('*').remove();
    const width = svg.node().clientWidth || 600;
    const height = svg.node().clientHeight || 500;

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Define zoom behavior
    zoomBehaviorRef.current = d3.zoom()
      .scaleExtent([0.2, 4])
      .on('zoom', (event) => {
        if (gLayerRef.current) {
          gLayerRef.current.attr('transform', event.transform);
        }
      });
    svg.call(zoomBehaviorRef.current);

    // Create a layer to pan/zoom
    gLayerRef.current = svg.append('g');

    // Create force simulation
    simulationRef.current = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(80).strength(0.6))
      .force('charge', d3.forceManyBody().strength(-250))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(24));

    // Create links
    linksRef.current = gLayerRef.current.append('g')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrow)');

    // Create nodes
    nodesRef.current = gLayerRef.current.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', 10)
      .attr('fill', d => color(d.group))
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Create labels
    nodeLabelsRef.current = gLayerRef.current.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .text(d => d.id)
      .attr('font-size', 11)
      .attr('fill', '#333')
      .attr('stroke', 'white')
      .attr('stroke-width', 3)
      .attr('paint-order', 'stroke')
      .attr('dx', 12)
      .attr('dy', 4);

    // Arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 18)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Relation labels
    linkLabelsRef.current = gLayerRef.current.append('g')
      .selectAll('text')
      .data(data.links)
      .enter().append('text')
      .text(d => d.relation)
      .attr('font-size', 10)
      .attr('fill', '#666');

    // Update positions on simulation tick
    simulationRef.current.on('tick', () => {
      if (linksRef.current) {
        linksRef.current
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);
      }

      if (nodesRef.current) {
        nodesRef.current
          .attr('cx', d => d.x)
          .attr('cy', d => d.y);
      }

      if (nodeLabelsRef.current) {
        nodeLabelsRef.current
          .attr('x', d => d.x)
          .attr('y', d => d.y);
      }

      if (linkLabelsRef.current) {
        linkLabelsRef.current
          .attr('x', d => (d.source.x + d.target.x) / 2)
          .attr('y', d => (d.source.y + d.target.y) / 2);
      }
    });

    // Drag handlers
    function dragstarted(event, d) {
      if (!event.active && simulationRef.current) {
        simulationRef.current.alphaTarget(0.3).restart();
      }
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active && simulationRef.current) {
        simulationRef.current.alphaTarget(0);
      }
      d.fx = null;
      d.fy = null;
    }

    // Fit to graph after initial layout
    setTimeout(() => fitToGraph(), 150);
  };

  const fitToGraph = (padding = 40) => {
    const svg = d3.select(svgRef.current);
    if (!svg.node() || !gLayerRef.current) return;
    
    const width = svg.node().clientWidth || 600;
    const height = svg.node().clientHeight || 500;
    
    // Compute bounds
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    gLayerRef.current.selectAll('circle').each(function(d) {
      if (d.x < minX) minX = d.x;
      if (d.y < minY) minY = d.y;
      if (d.x > maxX) maxX = d.x;
      if (d.y > maxY) maxY = d.y;
    });
    
    if (!isFinite(minX) || !isFinite(minY) || !isFinite(maxX) || !isFinite(maxY)) return;
    
    const dx = maxX - minX || 1;
    const dy = maxY - minY || 1;
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const scale = Math.min(3, 0.9 / Math.max(dx / (width - padding), dy / (height - padding)));
    
    const transform = d3.zoomIdentity
      .translate(width / 2, height / 2)
      .scale(scale)
      .translate(-cx, -cy);
    
    svg.transition().duration(400).call(zoomBehaviorRef.current.transform, transform);
  };

  const zoomIn = () => {
    const svg = d3.select(svgRef.current);
    if (zoomBehaviorRef.current) {
      svg.transition().duration(250).call(zoomBehaviorRef.current.scaleBy, 1.2);
    }
  };

  const zoomOut = () => {
    const svg = d3.select(svgRef.current);
    if (zoomBehaviorRef.current) {
      svg.transition().duration(250).call(zoomBehaviorRef.current.scaleBy, 1/1.2);
    }
  };

  const resetView = () => {
    const svg = d3.select(svgRef.current);
    if (zoomBehaviorRef.current) {
      svg.transition().duration(300).call(zoomBehaviorRef.current.transform, d3.zoomIdentity);
    }
  };

  // Expose methods globally for use by other components
  useEffect(() => {
    window.graphViz = {
      highlightLoop: (loop) => {
        if (!nodesRef.current || !linksRef.current || !linkLabelsRef.current) return;
        
        // Clear previous highlights
        nodesRef.current.attr('stroke', '#fff').attr('stroke-width', 1.5).attr('fill-opacity', 1);
        linksRef.current.attr('stroke', '#999').attr('stroke-width', 1.5);
        linkLabelsRef.current.attr('fill', '#666').attr('font-weight', null);
        
        // Highlight loop
        const nodeSet = new Set(loop.nodes);
        nodesRef.current
          .attr('fill-opacity', d => nodeSet.has(d.id) ? 1 : 0.25)
          .attr('stroke', d => nodeSet.has(d.id) ? '#ff9800' : '#fff')
          .attr('stroke-width', d => nodeSet.has(d.id) ? 3 : 1.5);
        
        // Build edge set for consecutive pairs
        const pairs = new Set();
        for (let i = 0; i < loop.nodes.length - 1; i++) {
          pairs.add(loop.nodes[i] + '||' + loop.nodes[i+1]);
        }
        
        linksRef.current
          .attr('stroke', d => pairs.has(d.source.id + '||' + d.target.id) ? '#ff9800' : '#999')
          .attr('stroke-width', d => pairs.has(d.source.id + '||' + d.target.id) ? 3 : 1.5);
        
        linkLabelsRef.current
          .attr('fill', d => pairs.has(d.source.id + '||' + d.target.id) ? '#ff9800' : '#666')
          .attr('font-weight', d => pairs.has(d.source.id + '||' + d.target.id) ? 'bold' : null);
      },
      clearHighlights: () => {
        if (!nodesRef.current || !linksRef.current || !linkLabelsRef.current) return;
        nodesRef.current.attr('stroke', '#fff').attr('stroke-width', 1.5).attr('fill-opacity', 1);
        linksRef.current.attr('stroke', '#999').attr('stroke-width', 1.5);
        linkLabelsRef.current.attr('fill', '#666').attr('font-weight', null);
      },
      fitToGraph,
      zoomIn,
      zoomOut,
      resetView,
    };
    
    return () => {
      delete window.graphViz;
    };
  }, []);

  return (
    <div className="graph-container">
      <div className="graph-controls">
        <div className="graph-title">Interactive Rendering (D3)</div>
        <div className="graph-buttons">
          <button onClick={zoomIn}>Zoom In</button>
          <button onClick={zoomOut}>Zoom Out</button>
          <button onClick={resetView}>Reset</button>
          <button onClick={fitToGraph}>Fit to Graph</button>
        </div>
      </div>
      <svg ref={svgRef} id="graphSvg"></svg>
    </div>
  );
}

