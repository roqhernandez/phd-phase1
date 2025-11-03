"""
Phase 1: Simple Web Interface for Knowledge Graph Queries
A minimal Flask application for exploring your scientific knowledge graph

Run with: python kg_web_interface.py
Then visit: http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify
from phase1_kg_starter import build_example_wave_kg
from classes.class_scientific_kg import ScientificKnowledgeGraph
import json
import os
import glob
import matplotlib.pyplot as plt

app = Flask(__name__)

# Global knowledge graph instance
kg = None
# Track the currently loaded JSON file
current_file = None

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Scientific Knowledge Graph Explorer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }

        /* Layout */
        .layout {
            display: grid;
            grid-template-rows: auto auto;
            gap: 20px;
        }
        .top-panels { display: block; }

        .panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }

        .panel h2 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .query-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .query-section h2 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        input, select {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            flex: 1;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .results {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            min-height: 100px;
        }
        
        .results h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .concept-card {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .concept-name {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        
        .concept-meta {
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
        }
        
        .relation-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            margin: 5px 5px 5px 0;
        }
        
        .path-arrow {
            color: #667eea;
            font-weight: bold;
            margin: 0 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 1em;
            opacity: 0.9;
        }
        
        .error {
            background: #fee;
            border: 2px solid #fcc;
            color: #c00;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        /* Triples table */
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: white;
        }
        .table th, .table td {
            border: 1px solid #eee;
            padding: 8px 10px;
            text-align: left;
            font-size: 14px;
        }
        .table th {
            background: #fafafa;
            color: #555;
        }
        .pagination {
            display: flex;
            gap: 8px;
            align-items: center;
            margin-top: 10px;
        }
        .muted {
            color: #777;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 Knowledge Graph Explorer</h1>
            <p class="subtitle">Query and explore scientific concepts</p>
        </header>
        
        <div class="content">
            <div class="layout">
                <div class="panel" style="margin-bottom:0;">
                    <div class="input-group" style="margin-bottom:0;">
                        <select id="file-select"></select>
                        <button onclick="selectFile()">Load</button>
                        <span id="current-file-label" class="muted"></span>
                    </div>
                </div>
                <div class="top-panels">
                    <div>
                        <!-- Triples Browser -->
                        <div class="query-section">
                            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                                <h2 style="margin:0;">🧾 Browse Triples</h2>
                                <button id="triples-toggle" onclick="toggleTriples()">Collapse</button>
                            </div>
                            <div id="triples-body">
                                <div class="input-group" style="margin-top:12px;">
                                    <select id="triples-relation-filter">
                                        <option value="">All relations</option>
                                    </select>
                                    <input type="number" id="triples-page-size" value="20" min="5" max="200" placeholder="Page size">
                                    <button onclick="loadTriples(1)">Refresh</button>
                                </div>
                                <div class="input-group" style="margin-bottom:0;">
                                    <input type="text" id="triples-add-subj" placeholder="subject">
                                    <input type="text" id="triples-add-pred" placeholder="predicate">
                                    <input type="text" id="triples-add-obj" placeholder="object">
                                    <button onclick="addTripleInline()">Add</button>
                                </div>
                                <div id="triples-stats" class="muted" style="margin:8px 0 0 2px;"></div>
                                <div id="triples-results" class="results">
                                    <div class="muted">Use controls above to list triples.</div>
                                </div>
                            </div>
                        </div>
                        <!-- Query 1: Find Neighbors -->
                        <div class="query-section">
                            <h2>🔍 Find Neighbors</h2>
                            <div class="input-group">
                                <input type="text" id="neighbor-concept" placeholder="Enter concept name (e.g., 'wave')">
                                <select id="neighbor-relation">
                                    <option value="">All relations</option>
                                </select>
                                <button onclick="findNeighbors()">Search</button>
                            </div>
                            <div id="neighbor-results" class="results"></div>
                        </div>

                        <!-- Query 2: Find Prerequisites -->
                        <div class="query-section">
                            <h2>📚 Find Prerequisites</h2>
                            <div class="input-group">
                                <input type="text" id="prereq-concept" placeholder="Enter concept name">
                                <input type="number" id="prereq-depth" placeholder="Max depth" value="3" min="1" max="10">
                                <button onclick="findPrerequisites()">Find Path</button>
                            </div>
                            <div id="prereq-results" class="results"></div>
                        </div>

                        <!-- Query 3: Find Path -->
                        <div class="query-section">
                            <h2>🛤️ Find Learning Path</h2>
                            <div class="input-group">
                                <input type="text" id="path-start" placeholder="Start concept">
                                <input type="text" id="path-end" placeholder="End concept">
                                <button onclick="findPath()">Find Path</button>
                            </div>
                            <div id="path-results" class="results"></div>
                        </div>

                        <!-- Query 4: Concept Details -->
                        <div class="query-section">
                            <h2>📖 Concept Details</h2>
                            <div class="input-group">
                                <input type="text" id="detail-concept" placeholder="Enter concept name">
                                <button onclick="getConceptDetails()">Get Details</button>
                            </div>
                            <div id="detail-results" class="results"></div>
                        </div>

                        <!-- Query 5: Find Loops -->
                        <div class="query-section">
                            <h2>♻️ Find Loops</h2>
                            <div class="input-group">
                                <input type="number" id="loops-max-length" placeholder="Max length (optional)">
                                <input type="number" id="loops-max-cycles" placeholder="Max cycles" value="200">
                                <button onclick="findLoops()">Find</button>
                            </div>
                            <div id="loops-results" class="results"></div>
                        </div>

                        <!-- Query 6: Loop Similarities -->
                        <div class="query-section">
                            <h2>🧩 Loop Similarities</h2>
                            <div class="input-group">
                                <input type="number" id="sim-node-j" placeholder="Min node Jaccard" value="0.5" step="0.05" min="0" max="1">
                                <input type="number" id="sim-rel-j" placeholder="Min relation Jaccard" value="0.5" step="0.05" min="0" max="1">
                            </div>
                            <div class="input-group">
                                <input type="number" id="sim-max-length" placeholder="Max loop length (optional)">
                                <input type="number" id="sim-max-cycles" placeholder="Max cycles" value="200">
                                <button onclick="findLoopSimilarities()">Compare</button>
                            </div>
                            <div id="loop-sim-results" class="results"></div>
                        </div>

                        <!-- Query 7: Subgraph Extraction -->
                        <div class="query-section">
                            <h2>🗺️ Subgraph</h2>
                            <div class="input-group">
                                <input type="text" id="subgraph-center" placeholder="Center concept (optional: leave empty for full)">
                                <input type="number" id="subgraph-radius" placeholder="Radius" value="2" min="0" max="10">
                            </div>
                            <div class="input-group">
                                <input type="text" id="subgraph-relations" placeholder="Relations filter (comma-separated, optional)">
                                <select id="subgraph-direction">
                                    <option value="both" selected>both</option>
                                    <option value="out">out</option>
                                    <option value="in">in</option>
                                </select>
                                <button onclick="renderSubgraph()">Render</button>
                                <button onclick="renderFullGraph()">Show Full</button>
                            </div>
                            <div id="subgraph-results" class="results"></div>
                        </div>
                    </div>
                </div>

                <!-- BOTTOM: D3 Rendering full width, Image below -->
                <div style="padding: 30px; background: #f8f9fa; margin-top: 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="font-weight:600; color:#667eea;">Interactive Rendering (D3)</div>
                        <div style="display:flex; gap:8px;">
                            <button id="btnZoomIn" onclick="zoomIn()">Zoom In</button>
                            <button id="btnZoomOut" onclick="zoomOut()">Zoom Out</button>
                            <button id="btnReset" onclick="resetView()">Reset</button>
                            <button id="btnFit" onclick="fitToGraph()">Fit to Graph</button>
                        </div>
                    </div>
                    <svg id="graphSvg" style="width:100%; height:560px; background:white; border-radius:10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);"></svg>
                    <div style="text-align:center; margin-top:20px;">
                        <div style="margin-bottom:10px; font-weight:600; color:#667eea;">Static Image</div>
                        <img id="graphImage" src="" alt="Knowledge Graph Visualization" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script>
        async function loadFiles() {
            try {
                const res = await fetch('/api/files');
                const data = await res.json();
                const sel = document.getElementById('file-select');
                sel.innerHTML = '';
                data.files.forEach((f) => {
                    const opt = document.createElement('option');
                    opt.value = f;
                    opt.textContent = f;
                    if (f === data.current) opt.selected = true;
                    sel.appendChild(opt);
                });
                const lbl = document.getElementById('current-file-label');
                if (lbl) lbl.textContent = `Current: ${data.current || 'None'}`;
            } catch (e) {
                const lbl = document.getElementById('current-file-label');
                if (lbl) lbl.textContent = `Error loading files: ${e.message}`;
            }
        }

        function toggleTriples() {
            const body = document.getElementById('triples-body');
            const btn = document.getElementById('triples-toggle');
            if (!body || !btn) return;
            const isHidden = body.style.display === 'none';
            body.style.display = isHidden ? '' : 'none';
            btn.textContent = isHidden ? 'Collapse' : 'Expand';
        }

        async function selectFile() {
            const sel = document.getElementById('file-select');
            const name = sel.value;
            try {
                const res = await fetch(`/api/select_file?name=${encodeURIComponent(name)}`);
                const data = await res.json();
                if (data.error) {
                    alert(data.error);
                    return;
                }
                await loadStats();
                await refreshRelations();
                refreshImage();
                await renderD3();
                const lbl = document.getElementById('current-file-label');
                if (lbl) lbl.textContent = `Current: ${name}`;
            } catch (e) {
                alert('Failed to load file: ' + e.message);
            }
        }

        function refreshImage() {
            const img = document.getElementById('graphImage');
            img.src = `/api/image?v=${Date.now()}`;
        }

        // Load initial statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('nodeCount').textContent = stats.nodes;
                document.getElementById('edgeCount').textContent = stats.edges;
                document.getElementById('relationTypeCount').textContent = stats.relation_types;
                
                // Populate relation dropdown
                const select = document.getElementById('neighbor-relation');
                select.innerHTML = '<option value="">All relations</option>';
                stats.relations.forEach(rel => {
                    const option = document.createElement('option');
                    option.value = rel;
                    option.textContent = rel;
                    select.appendChild(option);
                });
                const tSelect = document.getElementById('triples-relation-filter');
                if (tSelect) {
                    tSelect.innerHTML = '<option value="">All relations</option>';
                    stats.relations.forEach(rel => {
                        const opt = document.createElement('option');
                        opt.value = rel;
                        opt.textContent = rel;
                        tSelect.appendChild(opt);
                    });
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function refreshRelations() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                const select = document.getElementById('neighbor-relation');
                select.innerHTML = '<option value=\"\">All relations</option>';
                stats.relations.forEach(rel => {
                    const option = document.createElement('option');
                    option.value = rel;
                    option.textContent = rel;
                    select.appendChild(option);
                });
                const tSelect = document.getElementById('triples-relation-filter');
                if (tSelect) {
                    tSelect.innerHTML = '<option value=\"\">All relations</option>';
                    stats.relations.forEach(rel => {
                        const opt = document.createElement('option');
                        opt.value = rel;
                        opt.textContent = rel;
                        tSelect.appendChild(opt);
                    });
                }
            } catch (e) {}
        }
        
        async function findNeighbors() {
            const concept = document.getElementById('neighbor-concept').value;
            const relation = document.getElementById('neighbor-relation').value;
            const resultsDiv = document.getElementById('neighbor-results');
            
            if (!concept) {
                resultsDiv.innerHTML = '<div class="error">Please enter a concept name</div>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Searching...</div>';
            
            try {
                const response = await fetch(`/api/neighbors?concept=${encodeURIComponent(concept)}&relation=${encodeURIComponent(relation)}`);
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                if (data.neighbors.length === 0) {
                    resultsDiv.innerHTML = '<p>No neighbors found</p>';
                    return;
                }
                
                let html = '<h3>Connected Concepts:</h3>';
                data.neighbors.forEach(neighbor => {
                    html += `<div class="concept-card">
                        <div class="concept-name">${neighbor}</div>
                    </div>`;
                });
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function findPrerequisites() {
            const concept = document.getElementById('prereq-concept').value;
            const depth = document.getElementById('prereq-depth').value;
            const resultsDiv = document.getElementById('prereq-results');
            
            if (!concept) {
                resultsDiv.innerHTML = '<div class="error">Please enter a concept name</div>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Finding prerequisites...</div>';
            
            try {
                const response = await fetch(`/api/prerequisites?concept=${encodeURIComponent(concept)}&depth=${depth}`);
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                if (data.prerequisites.length === 0) {
                    resultsDiv.innerHTML = '<p>No prerequisites found</p>';
                    return;
                }
                
                let html = '<h3>Learning Prerequisites:</h3>';
                const byDepth = {};
                data.prerequisites.forEach(([prereq, d]) => {
                    if (!byDepth[d]) byDepth[d] = [];
                    byDepth[d].push(prereq);
                });
                
                Object.keys(byDepth).sort().forEach(d => {
                    html += `<div class="concept-card">
                        <div class="concept-meta">Level ${d}:</div>
                        ${byDepth[d].map(p => `<span class="relation-badge">${p}</span>`).join('')}
                    </div>`;
                });
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function findPath() {
            const start = document.getElementById('path-start').value;
            const end = document.getElementById('path-end').value;
            const resultsDiv = document.getElementById('path-results');
            
            if (!start || !end) {
                resultsDiv.innerHTML = '<div class="error">Please enter both start and end concepts</div>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Finding path...</div>';
            
            try {
                const response = await fetch(`/api/path?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                if (!data.path) {
                    resultsDiv.innerHTML = '<p>No path found between these concepts</p>';
                    return;
                }
                
                let html = '<h3>Learning Path:</h3><div class="concept-card">';
                html += data.path.map((step, i) => {
                    if (i === 0) return `<span class="concept-name">${step}</span>`;
                    return `<span class="path-arrow">→</span><span class="concept-name">${step}</span>`;
                }).join('');
                html += '</div>';
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function getConceptDetails() {
            const concept = document.getElementById('detail-concept').value;
            const resultsDiv = document.getElementById('detail-results');
            
            if (!concept) {
                resultsDiv.innerHTML = '<div class="error">Please enter a concept name</div>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Loading details...</div>';
            
            try {
                const response = await fetch(`/api/concept?name=${encodeURIComponent(concept)}`);
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                let html = `<h3>${data.name}</h3>`;
                html += `<div class="concept-card">`;
                html += `<div class="concept-meta">Type: ${data.metadata.type}</div>`;
                if (data.metadata.description) {
                    html += `<p style="margin-top: 10px;">${data.metadata.description}</p>`;
                }
                if (data.metadata.examples && data.metadata.examples.length > 0) {
                    html += `<div style="margin-top: 10px;"><strong>Examples:</strong></div>`;
                    data.metadata.examples.forEach(ex => {
                        html += `<div class="relation-badge">${ex}</div>`;
                    });
                }
                html += `<div style="margin-top:12px;"><button onclick="showMetaForm('${data.name}')">Edit Metadata</button></div>`;
                html += `</div>`;
                
                if (data.outgoing.length > 0) {
                    html += `<div class="concept-card">
                        <strong>Outgoing Relations:</strong><br>
                        ${data.outgoing.map(r => `<span class="relation-badge">${r}</span>`).join('')}
                    </div>`;
                }
                
                if (data.incoming.length > 0) {
                    html += `<div class="concept-card">
                        <strong>Incoming Relations:</strong><br>
                        ${data.incoming.map(r => `<span class="relation-badge">${r}</span>`).join('')}
                    </div>`;
                }
                
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        function showMetaForm(name) {
            const container = document.getElementById('detail-results');
            const existing = container.querySelector('#meta-edit-card');
            if (existing) existing.remove();
            const formHtml = `
                <div id="meta-edit-card" class="concept-card" style="margin-top:10px;">
                    <div style="font-weight:600; color:#667eea; margin-bottom:8px;">Edit Metadata</div>
                    <div class="input-group"><input id="meta-type" placeholder="type (e.g., concept, equation)"></div>
                    <div class="input-group"><input id="meta-desc" placeholder="description"></div>
                    <div class="input-group"><input id="meta-examples" placeholder="examples (comma-separated)"></div>
                    <div class="input-group">
                        <button onclick="submitMetadata('${name}')">Save</button>
                        <button onclick="getConceptDetails()" style="background:#999;">Cancel</button>
                    </div>
                </div>`;
            container.insertAdjacentHTML('beforeend', formHtml);
        }
        async function submitMetadata(name) {
            try {
                const type = document.getElementById('meta-type').value.trim() || 'concept';
                const description = document.getElementById('meta-desc').value.trim();
                const exStr = document.getElementById('meta-examples').value.trim();
                const examples = exStr ? exStr.split(',').map(s => s.trim()).filter(Boolean) : [];
                const res = await fetch('/api/update_metadata', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ node: name, type, description, examples })
                });
                const data = await res.json();
                if (data.error) { alert(data.error); return; }
                await loadStats();
                await getConceptDetails();
            } catch (e) { alert('Failed to update metadata: ' + e.message); }
        }
        async function loadTriples(page) {
            const relationSel = document.getElementById('triples-relation-filter');
            const relation = relationSel ? relationSel.value : '';
            const pageSizeEl = document.getElementById('triples-page-size');
            const pageSize = pageSizeEl ? parseInt(pageSizeEl.value || '20', 10) : 20;
            const resDiv = document.getElementById('triples-results');
            if (!resDiv) return;
            resDiv.innerHTML = '<div class=\"loading\">Loading triples...</div>';
            const params = new URLSearchParams({ page: page, page_size: pageSize });
            if (relation) params.append('relation', relation);
            try {
                const res = await fetch('/api/triples?' + params.toString());
                const data = await res.json();
                if (data.error) { resDiv.innerHTML = `<div class=\"error\">${data.error}</div>`; return; }
                const rows = data.triples.map(t => `<tr><td>${t.subject}</td><td><span class=\"relation-badge\">${t.predicate}</span></td><td>${t.object}</td><td class=\"muted\">${t.confidence ?? ''}</td><td class=\"muted\">${t.source ?? ''}</td><td style=\"text-align:right;\"><button style=\"background:#c0392b\" onclick=\"removeTriple('${t.subject}','${t.predicate}','${t.object}')\">Remove</button></td></tr>`).join('');
                const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));
                const html = `
                    <div style=\"display:flex; justify-content:space-between; align-items:center;\">`
                        + `<div class=\"muted\">Total: ${data.total} triples</div>`
                        + `<div class=\"pagination\">`
                            + `<button ${data.page <= 1 ? 'disabled' : ''} onclick=\"loadTriples(${data.page - 1})\">Prev</button>`
                            + `<span class=\"muted\">Page ${data.page} / ${totalPages}</span>`
                            + `<button ${data.page >= totalPages ? 'disabled' : ''} onclick=\"loadTriples(${data.page + 1})\">Next</button>`
                        + `</div>`
                    + `</div>`
                    + `<table class=\"table\">`
                        + `<thead><tr><th>Subject</th><th>Predicate</th><th>Object</th><th>Conf.</th><th>Source</th><th></th></tr></thead>`
                        + `<tbody>${rows || '<tr><td colspan=\"5\" class=\"muted\">No triples on this page.</td></tr>'}</tbody>`
                    + `</table>`;
                resDiv.innerHTML = html;
                try {
                    const statsRes = await fetch('/api/stats');
                    const stats = await statsRes.json();
                    const statsEl = document.getElementById('triples-stats');
                    if (statsEl) statsEl.textContent = `Concepts: ${stats.nodes}, Relations: ${stats.edges}, Relation Types: ${stats.relation_types}`;
                } catch (e) {}
            } catch (e) {
                resDiv.innerHTML = `<div class=\"error\">${e.message}</div>`;
            }
        }

        async function addTripleInline() {
            const s = document.getElementById('triples-add-subj').value.trim();
            const p = document.getElementById('triples-add-pred').value.trim();
            const o = document.getElementById('triples-add-obj').value.trim();
            if (!s || !p || !o) { alert('Please fill subject, predicate, and object'); return; }
            try {
                const res = await fetch('/api/add_triple', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ subject: s, predicate: p, object: o }) });
                const data = await res.json();
                if (data.error) { alert(data.error); return; }
                document.getElementById('triples-add-subj').value = '';
                document.getElementById('triples-add-pred').value = '';
                document.getElementById('triples-add-obj').value = '';
                await loadStats();
                await refreshRelations();
                refreshImage();
                await renderD3();
                await loadTriples(1);
            } catch (e) { alert('Failed to add triple: ' + e.message); }
        }

        async function removeTriple(s, p, o) {
            if (!confirm(`Remove triple: ${s} ${p} ${o}?`)) return;
            try {
                const res = await fetch('/api/remove_triple', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ subject: s, predicate: p, object: o }) });
                const data = await res.json();
                if (data.error) { alert(data.error); return; }
                await loadStats();
                await refreshRelations();
                refreshImage();
                await renderD3();
                await loadTriples(1);
            } catch (e) { alert('Failed to remove triple: ' + e.message); }
        }
        
        // removed left-side addTriple UI

        // Load on page start
        window.onload = async () => {
            await loadFiles();
            await loadStats();
            await refreshRelations();
            refreshImage();
            await renderD3();
            try { await loadTriples(1); } catch (e) {}
        };

        async function fetchGraphData() {
            const res = await fetch('/api/graph');
            if (!res.ok) throw new Error('Failed to fetch graph');
            return await res.json();
        }

        async function fetchSubgraph(params) {
            const res = await fetch('/api/subgraph?' + params.toString());
            if (!res.ok) throw new Error('Failed to fetch subgraph');
            return await res.json();
        }

        let zoomBehavior;
        let simulation;
        let gLayer; // The pan/zoom group wrapper
        let d3Nodes; // selection of nodes
        let d3Links; // selection of links
        let d3LinkLabels; // selection of link labels

        async function renderD3() {
            try {
                const data = await fetchGraphData();
                const svg = d3.select('#graphSvg');
                svg.selectAll('*').remove();
                const width = svg.node().clientWidth || 600;
                const height = svg.node().clientHeight || 500;

                const color = d3.scaleOrdinal(d3.schemeCategory10);

                // Define zoom behavior
                zoomBehavior = d3.zoom()
                    .scaleExtent([0.2, 4])
                    .on('zoom', (event) => {
                        gLayer.attr('transform', event.transform);
                    });
                svg.call(zoomBehavior);

                // Create a layer to pan/zoom
                gLayer = svg.append('g');

                simulation = d3.forceSimulation(data.nodes)
                    .force('link', d3.forceLink(data.links).id(d => d.id).distance(80).strength(0.6))
                    .force('charge', d3.forceManyBody().strength(-250))
                    .force('center', d3.forceCenter(width / 2, height / 2))
                    .force('collision', d3.forceCollide().radius(d => 24));

                const link = d3Links = gLayer.append('g')
                    .attr('stroke', '#999')
                    .attr('stroke-opacity', 0.6)
                    .selectAll('line')
                    .data(data.links)
                    .enter().append('line')
                    .attr('stroke-width', 1.5)
                    .attr('marker-end', 'url(#arrow)');

                const node = d3Nodes = gLayer.append('g')
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

                const labels = gLayer.append('g')
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
                const linkLabels = d3LinkLabels = gLayer.append('g')
                    .selectAll('text')
                    .data(data.links)
                    .enter().append('text')
                    .text(d => d.relation)
                    .attr('font-size', 10)
                    .attr('fill', '#666');

                simulation.on('tick', () => {
                    link
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);

                    node
                        .attr('cx', d => d.x)
                        .attr('cy', d => d.y);

                    labels
                        .attr('x', d => d.x)
                        .attr('y', d => d.y);

                    linkLabels
                        .attr('x', d => (d.source.x + d.target.x) / 2)
                        .attr('y', d => (d.source.y + d.target.y) / 2);
                });

                function dragstarted(event, d) {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x; d.fy = d.y;
                }
                function dragged(event, d) {
                    d.fx = event.x; d.fy = event.y;
                }
                function dragended(event, d) {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null; d.fy = null;
                }
                // After initial layout, fit view
                setTimeout(() => fitToGraph(), 150);

            } catch (e) {
                console.error('D3 render failed:', e);
            }
        }

        function clearHighlights() {
            if (d3Nodes) d3Nodes.attr('stroke', '#fff').attr('stroke-width', 1.5).attr('fill-opacity', 1);
            if (d3Links) d3Links.attr('stroke', '#999').attr('stroke-width', 1.5);
            if (d3LinkLabels) d3LinkLabels.attr('fill', '#666').attr('font-weight', null);
        }

        function highlightLoop(loop) {
            if (!d3Nodes || !d3Links) return;
            clearHighlights();
            const nodeSet = new Set(loop.nodes);
            d3Nodes
                .attr('fill-opacity', d => nodeSet.has(d.id) ? 1 : 0.25)
                .attr('stroke', d => nodeSet.has(d.id) ? '#ff9800' : '#fff')
                .attr('stroke-width', d => nodeSet.has(d.id) ? 3 : 1.5);
            // Build edge set for consecutive pairs
            const pairs = new Set();
            for (let i = 0; i < loop.nodes.length - 1; i++) {
                pairs.add(loop.nodes[i] + '||' + loop.nodes[i+1]);
            }
            d3Links
                .attr('stroke', d => pairs.has(d.source.id + '||' + d.target.id) ? '#ff9800' : '#999')
                .attr('stroke-width', d => pairs.has(d.source.id + '||' + d.target.id) ? 3 : 1.5);
            if (d3LinkLabels) {
                d3LinkLabels.attr('fill', d => pairs.has(d.source.id + '||' + d.target.id) ? '#ff9800' : '#666')
                    .attr('font-weight', d => pairs.has(d.source.id + '||' + d.target.id) ? 'bold' : null);
            }
        }

        function zoomIn() {
            const svg = d3.select('#graphSvg');
            svg.transition().duration(250).call(zoomBehavior.scaleBy, 1.2);
        }
        function zoomOut() {
            const svg = d3.select('#graphSvg');
            svg.transition().duration(250).call(zoomBehavior.scaleBy, 1/1.2);
        }
        function resetView() {
            const svg = d3.select('#graphSvg');
            svg.transition().duration(300).call(zoomBehavior.transform, d3.zoomIdentity);
        }
        function fitToGraph(padding = 40) {
            const svg = d3.select('#graphSvg');
            const width = svg.node().clientWidth || 600;
            const height = svg.node().clientHeight || 500;
            // compute bounds
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            gLayer.selectAll('circle').each(function(d){
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
            svg.transition().duration(400).call(zoomBehavior.transform, transform);
        }

        // Re-render D3 on window resize to keep within bounds
        window.addEventListener('resize', () => {
            renderD3();
        });

        async function findLoops() {
            const maxLen = document.getElementById('loops-max-length').value;
            const maxCycles = document.getElementById('loops-max-cycles').value || 200;
            const params = new URLSearchParams();
            if (maxLen) params.append('max_length', maxLen);
            if (maxCycles) params.append('max_cycles', maxCycles);
            const target = '/api/loops' + (params.toString() ? ('?' + params.toString()) : '');
            const resDiv = document.getElementById('loops-results');
            resDiv.innerHTML = '<div class="loading">Searching for loops...</div>';
            try {
                const res = await fetch(target);
                const data = await res.json();
                if (data.error) { resDiv.innerHTML = `<div class="error">${data.error}</div>`; return; }
                if (!data.loops || data.loops.length === 0) { resDiv.innerHTML = '<p>No loops found.</p>'; return; }
                let html = '<h3>Loops:</h3>';
                data.loops.forEach((lp, idx) => {
                    const nodesStr = lp.nodes.join(' → ');
                    const relsStr = (lp.relations || []).join(', ');
                    html += `<div class="concept-card">
                        <div><strong>#${idx+1}</strong> ${nodesStr}</div>
                        ${relsStr ? `<div class="concept-meta">Relations: ${relsStr}</div>` : ''}
                        <button style="margin-top:8px;" onclick='(function(){highlightLoop(${JSON.stringify(lp)}); fitToGraph();})()'>Highlight</button>
                    </div>`;
                });
                resDiv.innerHTML = html;
            } catch (e) {
                resDiv.innerHTML = `<div class="error">${e.message}</div>`;
            }
        }

        async function renderSubgraph() {
            const center = document.getElementById('subgraph-center').value.trim();
            const radius = document.getElementById('subgraph-radius').value || 2;
            const relations = document.getElementById('subgraph-relations').value.trim();
            const direction = document.getElementById('subgraph-direction').value;
            const resDiv = document.getElementById('subgraph-results');
            resDiv.innerHTML = '<div class="loading">Loading subgraph...</div>';
            try {
                const params = new URLSearchParams({ radius, direction });
                if (center) params.append('center', center);
                if (relations) params.append('relations', relations);
                const data = await fetchSubgraph(params);
                await renderD3FromData(data);
                resDiv.innerHTML = `<div>Nodes: ${data.nodes.length}, Links: ${data.links.length}</div>`;
            } catch (e) {
                resDiv.innerHTML = `<div class=\"error\">${e.message}</div>`;
            }
        }

        async function renderFullGraph() {
            try {
                const data = await fetchGraphData();
                await renderD3FromData(data);
                document.getElementById('subgraph-results').innerHTML = `<div>Showing full graph. Nodes: ${data.nodes.length}, Links: ${data.links.length}</div>`;
            } catch (e) {
                document.getElementById('subgraph-results').innerHTML = `<div class=\"error\">${e.message}</div>`;
            }
        }

        async function renderD3FromData(data) {
            try {
                const svg = d3.select('#graphSvg');
                svg.selectAll('*').remove();
                const width = svg.node().clientWidth || 600;
                const height = svg.node().clientHeight || 500;

                const color = d3.scaleOrdinal(d3.schemeCategory10);

                zoomBehavior = d3.zoom()
                    .scaleExtent([0.2, 4])
                    .on('zoom', (event) => {
                        gLayer.attr('transform', event.transform);
                    });
                svg.call(zoomBehavior);

                gLayer = svg.append('g');

                simulation = d3.forceSimulation(data.nodes)
                    .force('link', d3.forceLink(data.links).id(d => d.id).distance(80).strength(0.6))
                    .force('charge', d3.forceManyBody().strength(-250))
                    .force('center', d3.forceCenter(width / 2, height / 2))
                    .force('collision', d3.forceCollide().radius(d => 24));

                const link = d3Links = gLayer.append('g')
                    .attr('stroke', '#999')
                    .attr('stroke-opacity', 0.6)
                    .selectAll('line')
                    .data(data.links)
                    .enter().append('line')
                    .attr('stroke-width', 1.5)
                    .attr('marker-end', 'url(#arrow)');

                const node = d3Nodes = gLayer.append('g')
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

                const labels = gLayer.append('g')
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

                d3LinkLabels = gLayer.append('g')
                    .selectAll('text')
                    .data(data.links)
                    .enter().append('text')
                    .text(d => d.relation)
                    .attr('font-size', 10)
                    .attr('fill', '#666');

                simulation.on('tick', () => {
                    link
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);

                    node
                        .attr('cx', d => d.x)
                        .attr('cy', d => d.y);

                    labels
                        .attr('x', d => d.x)
                        .attr('y', d => d.y);

                    d3LinkLabels
                        .attr('x', d => (d.source.x + d.target.x) / 2)
                        .attr('y', d => (d.source.y + d.target.y) / 2);
                });

                setTimeout(() => fitToGraph(), 120);
            } catch (e) {
                console.error('D3 render (subgraph) failed:', e);
            }
        }

        async function findLoopSimilarities() {
            const minNode = document.getElementById('sim-node-j').value || 0.5;
            const minRel = document.getElementById('sim-rel-j').value || 0.5;
            const maxLen = document.getElementById('sim-max-length').value;
            const maxCycles = document.getElementById('sim-max-cycles').value || 200;
            const params = new URLSearchParams({ min_node_jaccard: minNode, min_relation_jaccard: minRel, max_cycles: maxCycles });
            if (maxLen) params.append('max_length', maxLen);
            const target = '/api/loop_similarities' + (params.toString() ? ('?' + params.toString()) : '');
            const resDiv = document.getElementById('loop-sim-results');
            resDiv.innerHTML = '<div class="loading">Computing similarities...</div>';
            try {
                const res = await fetch(target);
                const data = await res.json();
                if (data.error) { resDiv.innerHTML = `<div class="error">${data.error}</div>`; return; }
                if (!data.pairs || data.pairs.length === 0) { resDiv.innerHTML = '<p>No similar loop pairs found.</p>'; return; }
                let html = '<h3>Similar Loop Pairs:</h3>';
                data.pairs.forEach((p, idx) => {
                    const nscore = p.node_jaccard.toFixed(2);
                    const rscore = p.relation_jaccard.toFixed(2);
                    const l1 = p.loop_i.nodes.join(' → ');
                    const l2 = p.loop_j.nodes.join(' → ');
                    html += `<div class="concept-card">
                        <div><strong>#${idx+1}</strong> NodeJ=${nscore}, RelJ=${rscore}</div>
                        <div class="concept-meta">Loop A: ${l1}</div>
                        <div class="concept-meta">Loop B: ${l2}</div>
                        <div style="margin-top:8px; display:flex; gap:8px;">
                            <button onclick='(function(){highlightLoop(${JSON.stringify(p.loop_i)}); fitToGraph();})()'>Highlight A</button>
                            <button onclick='(function(){highlightLoop(${JSON.stringify(p.loop_j)}); fitToGraph();})()'>Highlight B</button>
                            <button onclick='clearHighlights()'>Clear</button>
                        </div>
                    </div>`;
                });
                resDiv.innerHTML = html;
            } catch (e) {
                resDiv.innerHTML = `<div class="error">${e.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def index():
    """Serve the main interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    """Get graph statistics."""
    return jsonify({
        'nodes': kg.graph.number_of_nodes(),
        'edges': kg.graph.number_of_edges(),
        'relation_types': len(kg.relation_types),
        'relations': list(kg.relation_types)
    })

@app.route('/api/graph')
def api_graph():
    """Return the current graph in a D3-friendly format."""
    nodes = []
    node_set = set()
    for n in kg.graph.nodes():
        node_set.add(n)
        meta = kg.metadata.get(n, {})
        group = meta.get('type', 'concept')
        nodes.append({'id': n, 'group': group})
    links = []
    for u, v, d in kg.graph.edges(data=True):
        links.append({'source': u, 'target': v, 'relation': d.get('relation', '')})
    return jsonify({'nodes': nodes, 'links': links})

@app.route('/api/triples')
def api_triples():
    """Return triples with pagination and optional relation filter."""
    try:
        relation = request.args.get('relation', default='', type=str).strip()
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=20, type=int)
        page = max(1, page)
        page_size = max(5, min(200, page_size))
        triples = []
        for u, v, data in kg.graph.edges(data=True):
            rel = data.get('relation', '')
            if relation and rel != relation:
                continue
            triples.append({
                'subject': u,
                'predicate': rel,
                'object': v,
                'confidence': data.get('confidence', 1.0),
                'source': data.get('source', 'manual')
            })
        total = len(triples)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = triples[start:end]
        return jsonify({'triples': page_items, 'total': total, 'page': page, 'page_size': page_size})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/loops')
def api_loops():
    """Find loops in the current graph."""
    try:
        max_length = request.args.get('max_length', default=None, type=int)
        max_cycles = request.args.get('max_cycles', default=200, type=int)
        loops = kg.find_loops(max_length=max_length, max_cycles=max_cycles, include_relations=True)
        return jsonify({'loops': loops})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subgraph')
def api_subgraph():
    """Return a D3-friendly subgraph based on center/radius and relation filters."""
    try:
        center = request.args.get('center', default=None, type=str)
        radius = request.args.get('radius', default=2, type=int)
        relations_str = request.args.get('relations', default='', type=str)
        direction = request.args.get('direction', default='both', type=str)
        relations = None
        if relations_str:
            relations = set([r.strip() for r in relations_str.split(',') if r.strip()])
        data = kg.export_subgraph(center=center if center else None,
                                  radius=radius,
                                  relations=relations,
                                  direction=direction)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/loop_similarities')
def api_loop_similarities():
    """Compute loop similarities in the current graph."""
    try:
        min_node_jaccard = request.args.get('min_node_jaccard', default=0.5, type=float)
        min_relation_jaccard = request.args.get('min_relation_jaccard', default=0.5, type=float)
        max_length = request.args.get('max_length', default=None, type=int)
        max_cycles = request.args.get('max_cycles', default=200, type=int)
        pairs = kg.find_loop_similarities(
            min_node_jaccard=min_node_jaccard,
            min_relation_jaccard=min_relation_jaccard,
            max_length=max_length,
            max_cycles=max_cycles
        )
        return jsonify({'pairs': pairs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def api_files():
    """List available KG JSON files in data directory and current selection."""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    files = []
    if os.path.isdir(data_dir):
        for path in sorted(glob.glob(os.path.join(data_dir, '*.json'))):
            files.append(os.path.basename(path))
    return jsonify({'files': files, 'current': os.path.basename(current_file) if current_file else None})

@app.route('/api/select_file')
def api_select_file():
    """Select and load a KG JSON file as the active graph."""
    global kg, current_file
    name = request.args.get('name', '').strip()
    if not name:
        return jsonify({'error': 'File name required'}), 400
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    target = os.path.join(data_dir, os.path.basename(name))
    if not os.path.isfile(target):
        return jsonify({'error': f'File not found: {name}'}), 404
    try:
        kg = ScientificKnowledgeGraph()
        kg.load_from_json(target)
        current_file = target
        _save_visualization()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/neighbors')
def api_neighbors():
    """Find neighbors of a concept."""
    concept = request.args.get('concept', '').strip()
    relation = request.args.get('relation', '').strip()
    
    if not concept:
        return jsonify({'error': 'Concept name required'}), 400
    
    if concept not in kg.graph.nodes():
        return jsonify({'error': f'Concept "{concept}" not found in graph'}), 404
    
    neighbors = kg.get_neighbors(
        concept,
        relation=relation if relation else None,
        direction='both'
    )
    
    return jsonify({'neighbors': neighbors})

@app.route('/api/prerequisites')
def api_prerequisites():
    """Find prerequisites for a concept."""
    concept = request.args.get('concept', '').strip()
    depth = request.args.get('depth', '3')
    
    if not concept:
        return jsonify({'error': 'Concept name required'}), 400
    
    if concept not in kg.graph.nodes():
        return jsonify({'error': f'Concept "{concept}" not found in graph'}), 404
    
    try:
        depth_int = int(depth) if depth else None
    except ValueError:
        return jsonify({'error': 'Invalid depth value'}), 400
    
    prerequisites = kg.get_prerequisites(concept, depth=depth_int)
    
    return jsonify({'prerequisites': prerequisites})

@app.route('/api/path')
def api_path():
    """Find path between two concepts."""
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    
    if not start or not end:
        return jsonify({'error': 'Both start and end concepts required'}), 400
    
    if start not in kg.graph.nodes():
        return jsonify({'error': f'Start concept "{start}" not found'}), 404
    
    if end not in kg.graph.nodes():
        return jsonify({'error': f'End concept "{end}" not found'}), 404
    
    path = kg.find_path(start, end)
    
    return jsonify({'path': path})

@app.route('/api/concept')
def api_concept():
    """Get detailed information about a concept."""
    name = request.args.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Concept name required'}), 400
    
    if name not in kg.graph.nodes():
        return jsonify({'error': f'Concept "{name}" not found'}), 404
    
    outgoing = kg.get_neighbors(name, direction='out')
    incoming = kg.get_neighbors(name, direction='in')
    metadata = kg.metadata.get(name, {})
    
    return jsonify({
        'name': name,
        'metadata': metadata,
        'outgoing': outgoing,
        'incoming': incoming
    })

@app.route('/api/add_triple', methods=['POST'])
def api_add_triple():
    """Add a triple to the current KG and persist to the selected file."""
    global kg, current_file
    if kg is None:
        return jsonify({'error': 'Knowledge graph not initialized'}), 500
    try:
        data = request.get_json(silent=True) or {}
        s = (data.get('subject') or '').strip()
        p = (data.get('predicate') or '').strip()
        o = (data.get('object') or '').strip()
        if not s or not p or not o:
            return jsonify({'error': 'subject, predicate, and object are required'}), 400
        kg.add_triple(s, p, o)
        if current_file:
            kg.save_to_json(current_file)
        _save_visualization()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove_triple', methods=['POST'])
def api_remove_triple():
    """Remove a triple from the current KG and persist to the selected file."""
    global kg, current_file
    if kg is None:
        return jsonify({'error': 'Knowledge graph not initialized'}), 500
    try:
        data = request.get_json(silent=True) or {}
        s = (data.get('subject') or '').strip()
        p = (data.get('predicate') or '').strip()
        o = (data.get('object') or '').strip()
        if not s or not p or not o:
            return jsonify({'error': 'subject, predicate, and object are required'}), 400
        # Remove matching edges between s and o with relation p
        if kg.graph.has_edge(s, o):
            edges = list(kg.graph.get_edge_data(s, o).items())
            for key, edata in edges:
                if edata.get('relation') == p:
                    kg.graph.remove_edge(s, o, key=key)
        if current_file:
            kg.save_to_json(current_file)
        _save_visualization()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_metadata', methods=['POST'])
def api_update_metadata():
    """Update metadata for a node and persist to the selected file."""
    global kg, current_file
    if kg is None:
        return jsonify({'error': 'Knowledge graph not initialized'}), 500
    try:
        data = request.get_json(silent=True) or {}
        node = (data.get('node') or '').strip()
        node_type = (data.get('type') or 'concept').strip() or 'concept'
        description = (data.get('description') or '').strip()
        examples = data.get('examples') or []
        if not node:
            return jsonify({'error': 'node is required'}), 400
        if node not in kg.graph.nodes():
            # If metadata is set for a non-existent node, create isolated node
            kg.graph.add_node(node)
        kg.add_node_metadata(node, node_type=node_type, description=description, examples=examples)
        if current_file:
            kg.save_to_json(current_file)
        _save_visualization()
        return jsonify({'ok': True, 'metadata': kg.metadata.get(node, {})})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image')
def api_image():
    """Serve (and if needed regenerate) the visualization for the current KG."""
    from flask import send_file
    if kg is None:
        return "Graph not initialized", 500
    image_path = _get_image_path()
    if not os.path.exists(image_path):
        try:
            _save_visualization()
        except Exception:
            return "Image generation failed", 500
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    return "Image not found", 404

def _get_image_path():
    base_dir = os.path.dirname(current_file) if current_file else os.path.dirname(__file__)
    base_name = os.path.splitext(os.path.basename(current_file) if current_file else 'wave_kg')[0]
    return os.path.join(base_dir, f"{base_name}_visualization.png")

def _save_visualization():
    """Save a visualization image for the current KG to the dataset-specific file."""
    if kg is None:
        return
    image_path = _get_image_path()
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    kg.visualize(concept="", radius=2)
    plt.savefig(image_path, dpi=150, bbox_inches='tight')
    plt.close()

def main():
    """Initialize and run the web interface."""
    global kg, current_file
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH WEB INTERFACE")
    print("=" * 60)
    print("\nInitializing knowledge graph...")
    
    # Try to load from JSON, otherwise create example
    try:
        default_path = os.path.join(os.path.dirname(__file__), 'data', 'wave_kg.json')
        kg = ScientificKnowledgeGraph()
        kg.load_from_json(default_path)
        current_file = default_path
        print("✓ Loaded existing knowledge graph from data/wave_kg.json")
    except FileNotFoundError:
        print("Creating example wave physics knowledge graph...")
        kg = build_example_wave_kg()
        default_path = os.path.join(os.path.dirname(__file__), 'data', 'wave_kg.json')
        os.makedirs(os.path.dirname(default_path), exist_ok=True)
        kg.save_to_json(default_path)
        current_file = default_path
        print("✓ Created and saved example graph")
    
    print(f"\nGraph Statistics:")
    print(f"  Nodes: {kg.graph.number_of_nodes()}")
    print(f"  Edges: {kg.graph.number_of_edges()}")
    print(f"  Relations: {kg.relation_types}")
    
    print("\n" + "=" * 60)
    print("Starting web server...")
    print("Visit: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    _save_visualization()
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()