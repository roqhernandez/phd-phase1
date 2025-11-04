import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // Files
  getFiles: () => axios.get(`${API_BASE}/files`).then(r => r.data),
  selectFile: (name) => axios.get(`${API_BASE}/select_file?name=${encodeURIComponent(name)}`).then(r => r.data),
  createFile: () => axios.post(`${API_BASE}/create_file`).then(r => r.data),
  renameFile: (oldName, newName) => axios.post(`${API_BASE}/rename_file`, { old_name: oldName, new_name: newName }).then(r => r.data),
  deleteFile: (name) => axios.post(`${API_BASE}/delete_file`, { name }).then(r => r.data),
  
  // Stats
  getStats: () => axios.get(`${API_BASE}/stats`).then(r => r.data),
  
  // Graph
  getGraph: () => axios.get(`${API_BASE}/graph`).then(r => r.data),
  getSubgraph: (params) => axios.get(`${API_BASE}/subgraph?${params}`).then(r => r.data),
  getImage: () => `${API_BASE}/image?v=${Date.now()}`,
  
  // Triples
  getTriples: (params) => axios.get(`${API_BASE}/triples?${params}`).then(r => r.data),
  addTriple: (subject, predicate, object) => 
    axios.post(`${API_BASE}/add_triple`, { subject, predicate, object }).then(r => r.data),
  removeTriple: (subject, predicate, object) => 
    axios.post(`${API_BASE}/remove_triple`, { subject, predicate, object }).then(r => r.data),
  
  // Queries
  getNeighbors: (concept, relation = '') => 
    axios.get(`${API_BASE}/neighbors?concept=${encodeURIComponent(concept)}&relation=${encodeURIComponent(relation)}`).then(r => r.data),
  getPrerequisites: (concept, depth) => 
    axios.get(`${API_BASE}/prerequisites?concept=${encodeURIComponent(concept)}&depth=${depth}`).then(r => r.data),
  getPath: (start, end) => 
    axios.get(`${API_BASE}/path?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`).then(r => r.data),
  getConcept: (name) => 
    axios.get(`${API_BASE}/concept?name=${encodeURIComponent(name)}`).then(r => r.data),
  updateMetadata: (node, type, description, examples) => 
    axios.post(`${API_BASE}/update_metadata`, { node, type, description, examples }).then(r => r.data),
  
  // Loops
  getLoops: (params) => axios.get(`${API_BASE}/loops?${params}`).then(r => r.data),
  getLoopSimilarities: (params) => axios.get(`${API_BASE}/loop_similarities?${params}`).then(r => r.data),
};

