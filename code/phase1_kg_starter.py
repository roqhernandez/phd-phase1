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
from classes.class_scientific_kg import ScientificKnowledgeGraph
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
    
    #Add metadata
    
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
    kg.visualize(concept="", radius=2)
    plt.savefig("wave_kg_visualization.png", dpi=150, bbox_inches='tight')
    print("Saved visualization to 'wave_kg_visualization.png'")
    
    print("\n✓ Phase 1 starter code complete!")
    print("  Next steps:")
    print("  1. Modify this code for your chosen domain")
    print("  2. Extract 30-50 triples manually")
    print("  3. Build queries specific to your research questions")
    print("  4. Prepare a demo for your supervisor meeting")