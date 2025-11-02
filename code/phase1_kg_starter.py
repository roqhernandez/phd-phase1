"""
Phase 1: Basic Knowledge Graph Implementation
A hands-on starter for building your first scientific knowledge graph

This code provides:
- Simple triple storage and retrieval
- Basic graph queries (neighbors, paths, prerequisites)
- Manual triple extraction from text
- Simple visualization interface
"""

import networkx as nx
import json
from typing import List, Tuple, Optional, Set
from collections import defaultdict
import matplotlib.pyplot as plt

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
        
        plt.figure(figsize=figsize)
        
        # Create layout
        pos = nx.spring_layout(subgraph, k=0.5, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, node_color='lightblue',
                              node_size=3000, alpha=0.9)
        
        # Draw edges with different colors for different relations
        edge_colors = {
            'is_a': 'blue',
            'part_of': 'green',
            'prerequisite_of': 'red',
            'related_to': 'gray',
            'has_equation': 'purple'
        }
        
        for relation in self.relation_types:
            edges = [(u, v) for u, v, d in subgraph.edges(data=True)
                    if d.get('relation') == relation]
            if edges:
                nx.draw_networkx_edges(
                    subgraph, pos, edges,
                    edge_color=edge_colors.get(relation, 'gray'),
                    arrows=True, arrowsize=20, width=2,
                    label=relation
                )
        
        # Draw labels
        nx.draw_networkx_labels(subgraph, pos, font_size=10)
        
        plt.legend()
        plt.axis('off')
        plt.tight_layout()
        return plt


# ============= EXAMPLE USAGE: Building a Wave Physics KG =============

def build_example_wave_kg():
    """
    Build a small example knowledge graph about wave physics.
    This demonstrates manual triple extraction and structuring.
    """
    kg = ScientificKnowledgeGraph()
    
    # Add fundamental concepts
    triples = [
        # Taxonomic relations (is_a)
        ("sine_wave", "is_a", "periodic_function"),
        ("periodic_function", "is_a", "mathematical_function"),
        ("standing_wave", "is_a", "wave"),
        ("traveling_wave", "is_a", "wave"),
        ("soliton", "is_a", "wave"),
        
        # Mereological relations (part_of)
        ("amplitude", "part_of", "wave_description"),
        ("frequency", "part_of", "wave_description"),
        ("wavelength", "part_of", "wave_description"),
        ("phase", "part_of", "wave_description"),
        
        # Prerequisite relations
        ("trigonometry", "prerequisite_of", "fourier_analysis"),
        ("fourier_analysis", "prerequisite_of", "wave_analysis"),
        ("calculus", "prerequisite_of", "differential_equations"),
        ("differential_equations", "prerequisite_of", "wave_equation"),
        
        # Related concepts
        ("dispersion", "related_to", "wave_propagation"),
        ("interference", "related_to", "superposition"),
        ("diffraction", "related_to", "wave_propagation"),
        
        # Equation relations
        ("wave_equation", "has_equation", "second_order_pde"),
        ("schrodinger_equation", "has_equation", "complex_pde")
    ]
    
    for subj, pred, obj in triples:
        kg.add_triple(subj, pred, obj)
    
    # Add metadata
    kg.add_node_metadata(
        "sine_wave",
        node_type="concept",
        description="A smooth periodic oscillation described by sin(ωt + φ)",
        examples=["Pure tone in sound", "AC current"]
    )
    
    kg.add_node_metadata(
        "soliton",
        node_type="concept",
        description="A self-reinforcing wave packet that maintains its shape while traveling",
        examples=["Tsunami waves", "Optical solitons in fiber"]
    )
    
    kg.add_node_metadata(
        "wave_equation",
        node_type="equation",
        description="∂²u/∂t² = c²∂²u/∂x²",
        examples=["String vibration", "Sound propagation"]
    )
    
    return kg


def demonstrate_queries(kg: ScientificKnowledgeGraph):
    """
    Demonstrate various query patterns on the knowledge graph.
    """
    print("=" * 60)
    print("KNOWLEDGE GRAPH QUERIES - DEMONSTRATION")
    print("=" * 60)
    
    # Query 1: Find neighbors
    print("\n1. What are the neighboring concepts of 'wave'?")
    neighbors = kg.get_neighbors("wave", direction='both')
    print(f"   Neighbors: {neighbors}")
    
    # Query 2: Find specific relation type
    print("\n2. What are all the 'is_a' relationships?")
    is_a_relations = kg.query_by_relation("is_a")
    for subj, obj in is_a_relations[:5]:  # Show first 5
        print(f"   {subj} is_a {obj}")
    
    # Query 3: Find prerequisites
    print("\n3. What are the prerequisites for 'wave_equation'?")
    prereqs = kg.get_prerequisites("wave_equation")
    for prereq, depth in sorted(prereqs, key=lambda x: x[1]):
        print(f"   {'  ' * depth}{prereq} (depth: {depth})")
    
    # Query 4: Find path
    print("\n4. Is there a learning path from 'calculus' to 'wave_analysis'?")
    path = kg.find_path("calculus", "wave_analysis")
    if path:
        print(f"   Path: {' → '.join(path)}")
    else:
        print("   No path found")
    
    # Query 5: Get neighborhood
    print("\n5. What is the 2-hop neighborhood of 'sine_wave'?")
    neighborhood = kg.get_concept_neighborhood("sine_wave", radius=2)
    print(f"   Neighborhood ({len(neighborhood)} concepts): {neighborhood}")
    
    print("\n" + "=" * 60)


# ============= EXERCISES FOR THE STUDENT =============

def exercises():
    """
    Suggested exercises to complete Phase 1.
    
    TODO for student:
    1. Choose your own scientific domain (5-10 paragraphs from a textbook)
    2. Manually extract 30-50 triples from this text
    3. Add them to a knowledge graph using the code above
    4. Implement at least 5 different queries
    5. Add rich metadata to your concepts
    6. Visualize your graph
    7. Save and reload your graph from JSON
    8. Write a 1-page reflection on what you learned
    
    RESEARCH QUESTIONS TO CONSIDER:
    - What made it easy or hard to identify triples in your text?
    - Did you find concepts that didn't fit into clean subject-predicate-object form?
    - How did you decide on relation type names?
    - What information is lost when converting prose to triples?
    - How would you validate that your triples accurately represent the source text?
    """
    pass


if __name__ == "__main__":
    # Build example knowledge graph
    print("Building example wave physics knowledge graph...")
    kg = build_example_wave_kg()
    
    print(f"Created graph with {kg.graph.number_of_nodes()} nodes")
    print(f"and {kg.graph.number_of_edges()} edges")
    print(f"Relation types: {kg.relation_types}")
    
    # Demonstrate queries
    demonstrate_queries(kg)
    
    # Save to file
    print("\nSaving to 'wave_kg.json'...")
    kg.save_to_json("wave_kg.json")
    
    # Visualize
    print("\nGenerating visualization...")
    kg.visualize(concept="wave", radius=2)
    plt.savefig("wave_kg_visualization.png", dpi=150, bbox_inches='tight')
    print("Saved visualization to 'wave_kg_visualization.png'")
    
    print("\n✓ Phase 1 starter code complete!")
    print("  Next steps:")
    print("  1. Modify this code for your chosen domain")
    print("  2. Extract 30-50 triples manually")
    print("  3. Build queries specific to your research questions")
    print("  4. Prepare a demo for your supervisor meeting")