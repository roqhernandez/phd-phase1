# Phase 1: Getting Started with Knowledge Graph Construction

## 📋 Overview

This guide will help you set up your environment and complete Phase 1 (Weeks 1-4) of your doctoral research plan. By the end of this phase, you will have:

- A working knowledge graph with 20-50 concepts
- Manual triple extraction experience
- A queryable web interface
- Understanding of graph thinking fundamentals

---

## 🛠️ Setup Instructions

### 1. Create Project Directory

```bash
mkdir scientific-kg-research
cd scientific-kg-research
mkdir phase1
cd phase1
```

### 2. Install Dependencies

Create a `requirements.txt` file:

```
networkx>=3.0
matplotlib>=3.5.0
flask>=2.3.0
numpy>=1.24.0
```

Install:

```bash
pip install -r requirements.txt
```

### 3. Download Starter Code

Save the following files from the artifacts:
- `phase1_kg_starter.py` - Core knowledge graph implementation
- `kg_web_interface.py` - Web interface for queries

---

## 📚 Week 1: Reading and Conceptual Foundation

### Required Reading

1. **Hogan et al. (2021)**. Knowledge Graphs. *ACM Computing Surveys*, 54(4).
   - Focus on: Sections 1-3 (Introduction, Data Graphs, Schema)
   - Take notes on: What is a knowledge graph? How do they differ from databases?

2. **Werner et al. (2023)**. Knowledge Enhanced Graph Neural Networks. arXiv:2303.15487v3
   - Focus on: Sections 1-2 (Introduction, Related Work)
   - Take notes on: How can graphs represent knowledge?

### Reading Strategy

For each paper:
1. Read abstract and conclusion first (15 min)
2. Skim figures and captions (10 min)
3. Read introduction carefully (30 min)
4. Read one technical section that interests you (45 min)
5. Write 5 bullet points: key insights you learned

### Reflection Questions

After reading, write short answers (1 paragraph each):

1. What is the difference between a knowledge graph and a traditional database?
2. What kinds of relationships can knowledge graphs represent?
3. How might a knowledge graph help in your specific research area?
4. What challenges do you anticipate in building a knowledge graph?

---

## 🔨 Week 2: Choose Your Domain and Extract First Triples

### Step 1: Select a Small Domain

Choose ONE of:
- **Physics**: Wave phenomena (5-10 paragraphs from a wave physics textbook)
- **Biomedicine**: A specific metabolic pathway (5-10 paragraphs)
- **Your research area**: A small, well-defined topic you know well

**Criteria**: 
- You should be able to explain this topic to a colleague
- Text should have clear concepts and relationships
- Should contain 10-20 distinct concepts

### Step 2: Manual Triple Extraction

Create a spreadsheet or text file: `triples.csv`

```csv
subject,predicate,object,confidence,source,notes
sine_wave,is_a,periodic_function,1.0,textbook_page_45,Clear taxonomic relation
amplitude,part_of,wave_description,1.0,textbook_page_47,Mereological
calculus,prerequisite_of,differential_equations,0.9,implied_from_text,Not explicitly stated
```

**Guidelines**:
1. Read each paragraph carefully
2. Identify main concepts (nouns, noun phrases)
3. Identify relationships between concepts (verbs, prepositions)
4. Convert to (subject, predicate, object) form
5. Note confidence and source

**Target**: Extract 20-40 triples by end of week 2

### Step 3: Define Your Schema

Create `schema.yaml`:

```yaml
relation_types:
  - name: is_a
    description: "Taxonomic relationship (A is a type of B)"
    transitive: true
    examples:
      - ["sine_wave", "is_a", "periodic_function"]
  
  - name: part_of
    description: "Mereological relationship (A is part of B)"
    transitive: true
    examples:
      - ["amplitude", "part_of", "wave_description"]
  
  - name: prerequisite_of
    description: "Pedagogical dependency (A must be learned before B)"
    transitive: true
    examples:
      - ["calculus", "prerequisite_of", "differential_equations"]

node_types:
  - concept: "Abstract scientific concept"
  - equation: "Mathematical equation or formula"
  - quantity: "Measurable physical quantity"
  - phenomenon: "Observable scientific phenomenon"
```

---

## 💻 Week 3: Build Your Knowledge Graph

### Step 1: Load Your Triples

Create `build_my_kg.py`:

```python
from phase1_kg_starter import ScientificKnowledgeGraph
import csv

def load_triples_from_csv(filename):
    """Load triples from your CSV file."""
    kg = ScientificKnowledgeGraph()
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kg.add_triple(
                row['subject'],
                row['predicate'],
                row['object'],
                confidence=float(row.get('confidence', 1.0)),
                source=row.get('source', 'manual')
            )
    
    return kg

# Build your graph
kg = load_triples_from_csv('triples.csv')

print(f"Loaded {kg.graph.number_of_nodes()} concepts")
print(f"Loaded {kg.graph.number_of_edges()} relations")
print(f"Relation types: {kg.relation_types}")

# Save it
kg.save_to_json('my_kg.json')
print("Saved to my_kg.json")
```

Run it:
```bash
python build_my_kg.py
```

### Step 2: Add Rich Metadata

Enhance `build_my_kg.py` to add descriptions:

```python
# After loading triples, add metadata
kg.add_node_metadata(
    "your_concept_name",
    node_type="concept",
    description="Clear, concise description of the concept",
    examples=["Example 1", "Example 2"]
)

# Add metadata for 5-10 key concepts
```

### Step 3: Test Basic Queries

Create `test_queries.py`:

```python
from phase1_kg_starter import ScientificKnowledgeGraph

# Load your graph
kg = ScientificKnowledgeGraph()
kg.load_from_json('my_kg.json')

# Test queries
print("=== Query Tests ===\n")

# 1. Find neighbors
concept = "your_main_concept"
neighbors = kg.get_neighbors(concept, direction='both')
print(f"Neighbors of '{concept}': {neighbors}\n")

# 2. Find prerequisites
prereqs = kg.get_prerequisites("your_advanced_concept")
print(f"Prerequisites:")
for prereq, depth in sorted(prereqs, key=lambda x: x[1]):
    print(f"  {'  ' * depth}{prereq} (level {depth})")

# 3. Find path
path = kg.find_path("basic_concept", "advanced_concept")
if path:
    print(f"\nPath: {' → '.join(path)}")
else:
    print("\nNo path found")

# 4. Get neighborhood
neighborhood = kg.get_concept_neighborhood("central_concept", radius=2)
print(f"\nNeighborhood: {neighborhood}")
```

---

## 🌐 Week 4: Build Query Interface and Visualize

### Step 1: Launch Web Interface

Modify `kg_web_interface.py` to load your graph:

```python
# Around line 480, change:
kg.load_from_json('my_kg.json')  # Instead of 'wave_kg.json'
```

Run:
```bash
python kg_web_interface.py
```

Visit `http://localhost:5000` and test all query types.

### Step 2: Create Visualizations

Create `visualize_my_kg.py`:

```python
from phase1_kg_starter import ScientificKnowledgeGraph
import matplotlib.pyplot as plt

kg = ScientificKnowledgeGraph()
kg.load_from_json('my_kg.json')

# Full graph
kg.visualize()
plt.savefig('full_graph.png', dpi=150, bbox_inches='tight')
print("Saved full_graph.png")

# Neighborhood around key concept
kg.visualize(concept="your_central_concept", radius=2)
plt.savefig('neighborhood.png', dpi=150, bbox_inches='tight')
print("Saved neighborhood.png")
```

### Step 3: Create Query Examples

Document 5-6 interesting queries:

```python
# queries_showcase.py
from phase1_kg_starter import ScientificKnowledgeGraph

kg = ScientificKnowledgeGraph()
kg.load_from_json('my_kg.json')

print("=== Knowledge Graph Query Showcase ===\n")

# Query 1: What are all the prerequisites?
print("1. All prerequisite relationships:")
prereq_pairs = kg.query_by_relation("prerequisite_of")
for subj, obj in prereq_pairs:
    print(f"   {subj} → {obj}")

# Query 2: What is the most connected concept?
print("\n2. Most connected concepts:")
degrees = [(node, kg.graph.degree(node)) for node in kg.graph.nodes()]
top_5 = sorted(degrees, key=lambda x: x[1], reverse=True)[:5]
for node, degree in top_5:
    print(f"   {node}: {degree} connections")

# Query 3: What concepts are leaves (no outgoing edges)?
print("\n3. Leaf concepts (foundational):")
leaves = [n for n in kg.graph.nodes() if kg.graph.out_degree(n) == 0]
print(f"   {leaves}")

# Add 3 more queries specific to your domain
```

---

## 📝 Phase 1 Deliverables Checklist

At the end of Week 4, you should have:

- [ ] `triples.csv` - Your manually extracted triples (20-40 entries)
- [ ] `schema.yaml` - Your relation type definitions
- [ ] `my_kg.json` - Your knowledge graph saved in JSON format
- [ ] `build_my_kg.py` - Script to build your graph
- [ ] `test_queries.py` - Your query examples
- [ ] `visualize_my_kg.py` - Visualization scripts
- [ ] `full_graph.png` - Visualization of complete graph
- [ ] `neighborhood.png` - Focused visualization
- [ ] Working web interface at localhost:5000
- [ ] **1-page reflection** (see below)

---

## 📄 Writing Your Reflection (Week 4)

Create `phase1_reflection.md` addressing:

### What was intuitive?
- Which aspects of graph thinking came naturally?
- What made sense immediately?

### What was confusing?
- What concepts or processes were unclear?
- Where did you get stuck?

### What patterns did you notice?
- What recurring relationship types emerged?
- Did you find clusters of related concepts?
- Were there concepts that acted as "hubs"?

### Technical challenges
- What was hard about extracting triples from text?
- How did you decide on relation names?
- What information felt lost in the triple representation?

### Research questions raised
- What questions emerged while building?
- What would you want to explore in later phases?

**Length**: 1 page, single-spaced

---

## 🎯 Checkpoint Discussion Preparation

Before your 15-minute supervisor meeting, prepare:

1. **Demo** (5 minutes):
   - Show your web interface
   - Demonstrate 2-3 interesting queries
   - Show your visualization

2. **Discussion points** (10 minutes):
   - Share your biggest insight from manual extraction
   - Discuss one challenging decision you made
   - Ask about one confusing aspect
   - Preview what you want to focus on in Phase 2

### Sample Questions for Discussion
- "I struggled to decide whether X should be one concept or multiple. How would you approach this?"
- "I noticed that [pattern]. Is this typical in knowledge graphs?"
- "For Phase 2, should I focus more on [X] or [Y]?"

---

## 🚀 Common Issues and Solutions

### Issue: "I can't decide what relation type to use"

**Solution**: Start with these basic types:
- `is_a`: Taxonomic (type-of)
- `part_of`: Compositional (component-of)
- `prerequisite_of`: Learning dependency
- `related_to`: When unclear, use this temporarily

Refine later as patterns emerge.

### Issue: "My graph has disconnected components"

**Solution**: This is normal! Add a few more connecting triples. Ask:
- Are there shared prerequisites?
- Do concepts appear in the same equations?
- Are they used in the same contexts?

### Issue: "Some concepts are too granular, others too broad"

**Solution**: Document both levels:
- Keep detailed version for now
- Note in your reflection which might need merging
- This is a research question for later!

### Issue: "I'm not sure if my triples are 'correct'"

**Solution**: 
- No single "correct" representation exists
- Focus on consistency within your graph
- Document your decision rules
- This uncertainty is valuable research data

---

## 📖 Additional Resources

### Tools
- **Graphviz**: For alternative visualizations
- **Neo4j Desktop**: Try importing your JSON later
- **Zotero**: Start organizing your papers

### Reading (Optional)
- Miller (1995). "WordNet: A Lexical Database" - Classic KG example
- Any ontology engineering tutorial

### Communities
- Research Gate: Knowledge Graph groups
- Reddit: r/LanguageTechnology
- Stack Overflow: [knowledge-graph] tag

---

## ✅ Success Criteria

You've successfully completed Phase 1 if you can:

1. ✅ Explain what a knowledge graph is to a colleague
2. ✅ Show a working graph with 20+ concepts and 30+ relations
3. ✅ Demonstrate 5 different types of queries
4. ✅ Articulate at least 3 design decisions you made
5. ✅ Identify 2-3 research questions for later phases
6. ✅ Feel comfortable with graph thinking and terminology

---

## 🎓 What's Next: Phase 2 Preview

In Phase 2 (Weeks 5-8), you'll:
- Integrate equations as first-class graph nodes
- Implement symbolic processing
- Add unit consistency checking
- Link mathematical and conceptual knowledge

**Start thinking**: How would you represent an equation in your current graph?

---

## 💡 Final Tips

1. **Start small**: Better to have 30 high-quality triples than 100 messy ones
2. **Document decisions**: Future you will thank current you
3. **Don't overthink**: Perfect is the enemy of done
4. **Ask questions**: Weekly contact with supervisor is key
5. **Have fun**: You're building something cool!

**Remember**: This is exploratory research. "Mistakes" are data. Document everything, including what doesn't work.

Good luck! 🚀