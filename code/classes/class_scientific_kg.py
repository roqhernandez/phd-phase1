import networkx as nx
import json
from typing import List, Tuple, Optional, Set
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import warnings

# Suppress matplotlib warnings:
# - Legend warnings when no labeled artists exist
# - Axes3D warnings (we don't use 3D plotting)
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

class ScientificKnowledgeGraph:
    """
    A simple knowledge graph for scientific concepts.
    
    The graph stores triples: (subject, predicate, object)
    where subject and object are concepts, and predicate is a relation type.
    """
    
    def __init__(self):
        # Use MultiDiGraph to allow multiple relations between same nodes
        self.graph = nx.MultiDiGraph()
        self.relation_types = set()
        self.metadata = {}  # Store additional info about nodes
        
    def add_triple(self, subject: str, predicate: str, obj: str, 
                   confidence: float = 1.0, source: str = "manual"):
        """
        Add a knowledge triple to the graph.
        
        Args:
            subject: Source concept
            predicate: Relationship type (e.g., 'is_a', 'prerequisite_of')
            obj: Target concept
            confidence: Confidence score (0-1)
            source: Where this triple came from
        """
        self.graph.add_edge(
            subject, obj,
            relation=predicate,
            confidence=confidence,
            source=source
        )
        self.relation_types.add(predicate)
        
        # Initialize metadata if needed
        for node in [subject, obj]:
            if node not in self.metadata:
                self.metadata[node] = {
                    'type': 'concept',
                    'description': '',
                    'examples': []
                }
    
    def add_node_metadata(self, node: str, node_type: str = 'concept',
                         description: str = '', examples: List[str] = None):
        """Add descriptive metadata to a node."""
        self.metadata[node] = {
            'type': node_type,
            'description': description,
            'examples': examples or []
        }
    
    def get_neighbors(self, node: str, relation: Optional[str] = None,
                     direction: str = 'out') -> List[str]:
        """
        Get neighboring concepts.
        
        Args:
            node: The concept to query
            relation: Filter by specific relation type (optional)
            direction: 'out' for outgoing, 'in' for incoming, 'both' for all
        
        Returns:
            List of neighboring concept names
        """
        neighbors = []
        
        if direction in ['out', 'both']:
            for successor in self.graph.successors(node):
                edges = self.graph.get_edge_data(node, successor)
                for edge_key, edge_data in edges.items():
                    if relation is None or edge_data.get('relation') == relation:
                        neighbors.append(successor)
                        break
        
        if direction in ['in', 'both']:
            for predecessor in self.graph.predecessors(node):
                edges = self.graph.get_edge_data(predecessor, node)
                for edge_key, edge_data in edges.items():
                    if relation is None or edge_data.get('relation') == relation:
                        neighbors.append(predecessor)
                        break
        
        return list(set(neighbors))  # Remove duplicates
    
    def find_path(self, start: str, end: str, max_length: int = 5) -> Optional[List[str]]:
        """
        Find shortest path between two concepts.
        
        Args:
            start: Starting concept
            end: Target concept
            max_length: Maximum path length to consider
        
        Returns:
            List of concepts forming the path, or None if no path exists
        """
        try:
            path = nx.shortest_path(self.graph, start, end)
            if len(path) <= max_length + 1:
                return path
            return None
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def get_prerequisites(self, concept: str, depth: int = None) -> List[Tuple[str, int]]:
        """
        Get all prerequisites for a concept.
        
        Args:
            concept: The concept to find prerequisites for
            depth: Maximum depth to traverse (None = unlimited)
        
        Returns:
            List of (prerequisite_concept, depth) tuples
        """
        prerequisites = []
        visited = set()
        queue = [(concept, 0)]
        
        while queue:
            current, d = queue.pop(0)
            
            if current in visited:
                continue
            visited.add(current)
            
            if depth is not None and d >= depth:
                continue
            
            # Find concepts that are prerequisites of current
            prereq_neighbors = self.get_neighbors(current, relation='prerequisite_of', direction='in')
            
            for prereq in prereq_neighbors:
                if prereq != concept:  # Don't include the original concept
                    prerequisites.append((prereq, d + 1))
                    queue.append((prereq, d + 1))
        
        return prerequisites
    
    def query_by_relation(self, relation: str) -> List[Tuple[str, str]]:
        """
        Get all (subject, object) pairs connected by a specific relation.
        """
        results = []
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if data.get('relation') == relation:
                results.append((u, v))
        return results
    
    def get_concept_neighborhood(self, concept: str, radius: int = 1) -> Set[str]:
        """
        Get all concepts within a certain radius.
        
        Args:
            concept: Central concept
            radius: How many hops away to include
        
        Returns:
            Set of concept names
        """
        neighborhood = {concept}
        current_level = {concept}
        
        for _ in range(radius):
            next_level = set()
            for node in current_level:
                next_level.update(self.get_neighbors(node, direction='both'))
            neighborhood.update(next_level)
            current_level = next_level
        
        return neighborhood
    
    def find_loops(self, max_length: int = None, max_cycles: int = 1000, include_relations: bool = True) -> List[dict]:
        """Find directed cycles (loops) in the knowledge graph.
        
        Args:
            max_length: If provided, only return cycles with length <= max_length
            max_cycles: Safety cap to avoid excessive runtime on large graphs
            include_relations: If True, include the relation label along each edge of the loop
        
        Returns:
            List of cycles as dicts: { 'nodes': [n1, n2, ..., n1], 'relations': [r12, r23, ... , r_last_first] }
            The loop is closed by repeating the first node at the end of the list.
        """
        # Convert to a simple DiGraph for cycle detection (ignore parallel edges)
        G = nx.DiGraph()
        for u, v, data in self.graph.edges(data=True):
            # Keep one representative relation for u->v if multiple exist
            if not G.has_edge(u, v):
                G.add_edge(u, v, relation=data.get('relation'))
        
        cycles = []
        for idx, cycle in enumerate(nx.simple_cycles(G)):
            if max_cycles is not None and idx >= max_cycles:
                break
            if max_length is not None and len(cycle) > max_length:
                continue
            # Close the cycle: repeat the first node at the end for clearer rendering
            closed_nodes = list(cycle) + [cycle[0]]
            if include_relations:
                rels = []
                for i in range(len(cycle)):
                    u = cycle[i]
                    v = cycle[(i + 1) % len(cycle)]
                    rel = None
                    # If original multigraph had multiple edges, pick the first relation label
                    data_uv = self.graph.get_edge_data(u, v)
                    if data_uv:
                        # data_uv is a dict of keys -> edge data
                        first_key = next(iter(data_uv))
                        rel = data_uv[first_key].get('relation')
                    else:
                        # Fallback to relation stored in simplified graph, if any
                        rel = G.get_edge_data(u, v).get('relation') if G.has_edge(u, v) else None
                    rels.append(rel)
                cycles.append({'nodes': closed_nodes, 'relations': rels})
            else:
                cycles.append({'nodes': closed_nodes})
        return cycles

    def find_loop_similarities(self, min_node_jaccard: float = 0.5, min_relation_jaccard: float = 0.5,
                               max_length: int = None, max_cycles: int = 500) -> List[dict]:
        """Compute similarities between detected loops based on nodes and relations.
        
        The similarity metric is Jaccard similarity:
        - node_jaccard: J(nodes_i, nodes_j) using sets of nodes (ignoring the repeated closing node)
        - relation_jaccard: J(relation_multiset_i, relation_multiset_j) approximated by set Jaccard; if you
          want multiset-aware similarity, replace with an overlap based on Counters.
        
        Args:
            min_node_jaccard: Minimum node overlap to include a pair
            min_relation_jaccard: Minimum relation overlap to include a pair
            max_length: Only consider loops up to this length (optional)
            max_cycles: Maximum number of cycles to consider for pairing
        
        Returns:
            List of dicts with fields: { 'i': int, 'j': int, 'node_jaccard': float,
              'relation_jaccard': float, 'len_i': int, 'len_j': int, 'loop_i': {...}, 'loop_j': {...} }
            Sorted by combined score (average of both Jaccards) descending.
        """
        loops = self.find_loops(max_length=max_length, max_cycles=max_cycles, include_relations=True)
        results: List[dict] = []
        
        def jaccard_set(a: Set, b: Set) -> float:
            if not a and not b:
                return 1.0
            inter = len(a & b)
            union = len(a | b)
            return inter / union if union else 0.0
        
        for i in range(len(loops)):
            nodes_i = set(loops[i]['nodes'][:-1])  # drop closing node
            rels_i = set(loops[i].get('relations', []))
            for j in range(i + 1, len(loops)):
                nodes_j = set(loops[j]['nodes'][:-1])
                rels_j = set(loops[j].get('relations', []))
                node_j = jaccard_set(nodes_i, nodes_j)
                rel_j = jaccard_set(rels_i, rels_j)
                if node_j >= min_node_jaccard and rel_j >= min_relation_jaccard:
                    results.append({
                        'i': i,
                        'j': j,
                        'node_jaccard': round(node_j, 4),
                        'relation_jaccard': round(rel_j, 4),
                        'len_i': len(nodes_i),
                        'len_j': len(nodes_j),
                        'loop_i': loops[i],
                        'loop_j': loops[j]
                    })
        # Sort by average of jaccards desc
        results.sort(key=lambda x: (x['node_jaccard'] + x['relation_jaccard']) / 2, reverse=True)
        return results
    
    def save_to_json(self, filename: str):
        """Export the knowledge graph to JSON format."""
        data = {
            'nodes': [],
            'edges': [],
            'metadata': self.metadata
        }
        
        # Add nodes
        for node in self.graph.nodes():
            data['nodes'].append({
                'id': node,
                'metadata': self.metadata.get(node, {})
            })
        
        # Add edges
        for u, v, key, edge_data in self.graph.edges(keys=True, data=True):
            data['edges'].append({
                'source': u,
                'target': v,
                'relation': edge_data.get('relation'),
                'confidence': edge_data.get('confidence', 1.0),
                'source_type': edge_data.get('source', 'manual')
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_json(self, filename: str):
        """Import a knowledge graph from JSON format."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        
        for edge in data['edges']:
            self.add_triple(
                edge['source'],
                edge['relation'],
                edge['target'],
                confidence=edge.get('confidence', 1.0),
                source=edge.get('source_type', 'manual')
            )
    
    def visualize(self, concept: str = None, radius: int = 2, figsize=(12, 8)):
        """
        Create a simple visualization of the graph.
        
        Args:
            concept: If provided, show neighborhood around this concept
            radius: Size of neighborhood to show
            figsize: Figure size
        """
        if concept:
            nodes_to_show = self.get_concept_neighborhood(concept, radius)
            subgraph = self.graph.subgraph(nodes_to_show)
        else:
            subgraph = self.graph

        # Adaptive figure size based on number of nodes
        n_nodes = subgraph.number_of_nodes()
        if n_nodes == 0:
            # Empty graph - just show message
            plt.figure(figsize=figsize)
            plt.text(0.5, 0.5, 'Empty graph', ha='center', va='center', transform=plt.gca().transAxes)
            return
        
        if n_nodes > 0:
            w = max(figsize[0], min(24, 10 + n_nodes * 0.4))
            h = max(figsize[1], min(18, 6 + n_nodes * 0.3))
            plt.figure(figsize=(w, h))
        else:
            plt.figure(figsize=figsize)

        # Create layout with increased spacing to reduce overlap
        try:
            if n_nodes == 1:
                # Single node - place it in the center
                pos = {list(subgraph.nodes())[0]: (0, 0)}
            elif n_nodes <= 50 and n_nodes > 1:
                # Kamada-Kawai spreads small graphs nicely
                try:
                    pos = nx.kamada_kawai_layout(subgraph)
                except (ValueError, Exception) as e:
                    # Fallback if kamada_kawai fails (e.g., disconnected components)
                    import math
                    sqrt_n = math.sqrt(n_nodes) if n_nodes > 0 else 1.0
                    k = 2.0 / sqrt_n + 0.15
                    pos = nx.spring_layout(subgraph, k=k, iterations=300, seed=42)
            else:
                # Tune spring layout: larger k => more spacing
                import math
                sqrt_n = math.sqrt(n_nodes) if n_nodes > 0 else 1.0
                k = 2.0 / sqrt_n + 0.15
                pos = nx.spring_layout(subgraph, k=k, iterations=300, seed=42)
        except Exception as e:
            # Final fallback: use default spring layout
            print(f"Warning: Layout algorithm failed, using default spring layout: {e}")
            pos = nx.spring_layout(subgraph, seed=42)

        # Node/label sizing scales with graph size
        node_size = max(600, 3000 - n_nodes * 30)
        font_size = max(6, 12 - int(n_nodes * 0.1))

        # Draw nodes
        nx.draw_networkx_nodes(
            subgraph,
            pos,
            node_color='lightblue',
            node_size=node_size,
            alpha=0.9
        )

        # Draw edges with different colors for different relations
        edge_colors = {
            'is_a': 'blue',
            'part_of': 'green',
            'prerequisite_of': 'red',
            'related_to': 'gray',
            'has_equation': 'purple'
        }
        
        has_labeled_edges = False
        for relation in self.relation_types:
            edges = [(u, v) for u, v, d in subgraph.edges(data=True)
                    if d.get('relation') == relation]
            if edges:
                nx.draw_networkx_edges(
                    subgraph,
                    pos,
                    edges,
                    edge_color=edge_colors.get(relation, 'gray'),
                    arrows=True,
                    arrowsize=16,
                    width=max(1.0, 2.5 - n_nodes * 0.02),
                    label=relation
                )
                has_labeled_edges = True
        
        # Draw labels
        nx.draw_networkx_labels(
            subgraph,
            pos,
            font_size=font_size,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.5)
        )
        
        plt.margins(0.2)
        
        # Only create legend if there are labeled edges
        # Check for labeled artists before attempting to create legend
        if has_labeled_edges:
            try:
                handles, labels = plt.gca().get_legend_handles_labels()
                if handles and labels and len(handles) > 0:
                    plt.legend(handles, labels, loc='best', fontsize=8)
            except (ValueError, AttributeError):
                # No labeled artists or legend creation failed - silently skip
                pass
            except Exception:
                # Other errors - silently skip
                pass
        plt.axis('off')
        plt.tight_layout()
        return plt

    def export_subgraph(self, center: Optional[str] = None, radius: int = 1,
                        relations: Optional[Set[str]] = None,
                        direction: str = 'both') -> dict:
        """Export a D3-friendly subgraph.

        Args:
            center: If provided, take neighborhood around this node; if None, use full graph
            radius: Neighborhood radius (ignored if center is None)
            relations: If provided, include only edges whose relation is in this set
            direction: Direction used for neighborhood gathering ('in', 'out', 'both')

        Returns:
            dict with 'nodes' and 'links' lists suitable for D3 rendering
        """
        if center:
            nodes_set = self.get_concept_neighborhood(center, radius)
        else:
            nodes_set = set(self.graph.nodes())

        nodes = []
        for n in nodes_set:
            meta = self.metadata.get(n, {})
            nodes.append({'id': n, 'group': meta.get('type', 'concept')})

        links = []
        for u, v, data in self.graph.edges(data=True):
            if u in nodes_set and v in nodes_set:
                rel = data.get('relation')
                if relations is None or rel in relations:
                    links.append({'source': u, 'target': v, 'relation': rel})

        return {'nodes': nodes, 'links': links}

