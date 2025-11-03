# Knowledge Graph Explorer - React Frontend

This is the React frontend for the Knowledge Graph Explorer application.

## Development Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (Vite's default port) and will proxy API requests to the Flask backend at `http://localhost:5000`.

3. Make sure the Flask backend is running:
```bash
cd ..
python kg_web_interface.py
```

## Building for Production

To build the React app for production:

```bash
npm run build
```

This will create a `dist` folder that the Flask backend can serve. The Flask backend is configured to automatically serve the React app if the `dist` folder exists.

## Project Structure

- `src/` - Source code
  - `App.jsx` - Main application component
  - `api.js` - API utility functions for communicating with the backend
  - `components/` - React components
    - `FileSelector.jsx` - File selection component
    - `StatsDisplay.jsx` - Graph statistics display
    - `TriplesBrowser.jsx` - Browse and manage triples
    - `FindNeighbors.jsx` - Find neighbors query
    - `FindPrerequisites.jsx` - Find prerequisites query
    - `FindPath.jsx` - Find path query
    - `ConceptDetails.jsx` - Concept details and metadata editor
    - `FindLoops.jsx` - Find loops query
    - `LoopSimilarities.jsx` - Loop similarities query
    - `Subgraph.jsx` - Subgraph extraction
    - `GraphVisualization.jsx` - D3.js interactive graph visualization
    - `GraphImage.jsx` - Static graph image display
  - `index.css` - Global styles
  - `App.css` - App-specific styles

## Features

All features from the original HTML interface are preserved:
- File loading and selection
- Statistics display
- Triples browser with pagination, add/remove
- Query operations (neighbors, prerequisites, path, concept details)
- Loop finding and similarity analysis
- Subgraph extraction
- Interactive D3.js graph visualization with zoom/pan
- Static graph image display

## API Communication

The frontend communicates with the Flask backend through the `/api` endpoints. During development, Vite proxies these requests. In production, the Flask backend serves both the static React app and the API endpoints.
