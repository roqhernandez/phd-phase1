"""
Phase 1: Simple Web Interface for Knowledge Graph Queries
A minimal Flask application for exploring your scientific knowledge graph

Run with: python kg_web_interface.py
Then visit: http://localhost:5000
"""

from flask import Flask, render_template_string, request, jsonify
from phase1_kg_starter import ScientificKnowledgeGraph, build_example_wave_kg
import json

app = Flask(__name__)

# Global knowledge graph instance
kg = None

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
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 Knowledge Graph Explorer</h1>
            <p class="subtitle">Query and explore scientific concepts</p>
        </header>
        
        <div class="content">
            <!-- Statistics -->
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="nodeCount">-</div>
                    <div class="stat-label">Concepts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="edgeCount">-</div>
                    <div class="stat-label">Relations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="relationTypeCount">-</div>
                    <div class="stat-label">Relation Types</div>
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
        </div>
    </div>
    
    <script>
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
                stats.relations.forEach(rel => {
                    const option = document.createElement('option');
                    option.value = rel;
                    option.textContent = rel;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading stats:', error);
            }
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
        
        // Load stats on page load
        window.onload = loadStats;
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

def main():
    """Initialize and run the web interface."""
    global kg
    
    print("=" * 60)
    print("KNOWLEDGE GRAPH WEB INTERFACE")
    print("=" * 60)
    print("\nInitializing knowledge graph...")
    
    # Try to load from JSON, otherwise create example
    try:
        kg = ScientificKnowledgeGraph()
        kg.load_from_json('wave_kg.json')
        print("✓ Loaded existing knowledge graph from wave_kg.json")
    except FileNotFoundError:
        print("Creating example wave physics knowledge graph...")
        kg = build_example_wave_kg()
        kg.save_to_json('wave_kg.json')
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
    
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()