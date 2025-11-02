# Manual Knowledge Triple Extraction Worksheet

## 📖 Instructions

This worksheet guides you through systematic knowledge extraction from scientific text. Work through each step carefully and document your decisions.

---

## 📋 Document Information

**Source Document**: _________________________________

**Domain**: _________________________________

**Date of Extraction**: _________________________________

**Pages/Sections Covered**: _________________________________

---

## Step 1: Read and Highlight

### First Pass: Identify Concepts (15 minutes)

Read your selected text and **underline** or **highlight** all important concepts. A concept is typically:
- A noun or noun phrase
- Represents a scientific idea, object, process, or quantity
- Appears multiple times or is central to the explanation

**Example**: In "A sine wave is a periodic function that describes smooth oscillation"
- Concepts: `sine wave`, `periodic function`, `oscillation`

### Your Concepts (List 15-20):

1. ________________
2. ________________
3. ________________
4. ________________
5. ________________
6. ________________
7. ________________
8. ________________
9. ________________
10. ________________
11. ________________
12. ________________
13. ________________
14. ________________
15. ________________
16. ________________
17. ________________
18. ________________
19. ________________
20. ________________

---

## Step 2: Identify Relationships

### Second Pass: Find Connections (20 minutes)

Look for words/phrases that connect concepts:

| Relation Indicator | Relation Type | Example |
|-------------------|---------------|---------|
| "is a", "is a type of" | `is_a` | X is a Y |
| "consists of", "contains", "has" | `part_of` | X part_of Y |
| "requires", "depends on", "builds on" | `prerequisite_of` | X prerequisite_of Y |
| "causes", "leads to", "results in" | `causes` | X causes Y |
| "described by", "governed by" | `has_equation` | X has_equation Y |
| "measured in", "has unit" | `measured_in` | X measured_in Y |
| "used in", "applied to" | `used_in` | X used_in Y |
| "similar to", "analogous to" | `similar_to` | X similar_to Y |

### Your Relationship Patterns

Read each sentence and fill out:

**Sentence 1**: "_________________________________"

- Subject: ________________
- Predicate: ________________
- Object: ________________
- Confidence (0-1): ______
- Notes: _________________________________

**Sentence 2**: "_________________________________"

- Subject: ________________
- Predicate: ________________
- Object: ________________
- Confidence (0-1): ______
- Notes: _________________________________

**Sentence 3**: "_________________________________"

- Subject: ________________
- Predicate: ________________
- Object: ________________
- Confidence (0-1): ______
- Notes: _________________________________

*(Continue for 15-20 sentences)*

---

## Step 3: Classify Triple Types

### Taxonomic Relations (is_a)

These create hierarchies and classification systems.

| Subject | Predicate | Object | Source |
|---------|-----------|--------|--------|
| _______ | is_a | _______ | Page ___ |
| _______ | is_a | _______ | Page ___ |
| _______ | is_a | _______ | Page ___ |
| _______ | is_a | _______ | Page ___ |
| _______ | is_a | _______ | Page ___ |

### Mereological Relations (part_of)

These describe composition and components.

| Subject | Predicate | Object | Source |
|---------|-----------|--------|--------|
| _______ | part_of | _______ | Page ___ |
| _______ | part_of | _______ | Page ___ |
| _______ | part_of | _______ | Page ___ |
| _______ | part_of | _______ | Page ___ |

### Prerequisite Relations (prerequisite_of)

These describe learning or logical dependencies.

| Subject | Predicate | Object | Source |
|---------|-----------|--------|--------|
| _______ | prerequisite_of | _______ | Page ___ |
| _______ | prerequisite_of | _______ | Page ___ |
| _______ | prerequisite_of | _______ | Page ___ |
| _______ | prerequisite_of | _______ | Page ___ |

### Other Relations

| Subject | Predicate | Object | Source |
|---------|-----------|--------|--------|
| _______ | _______ | _______ | Page ___ |
| _______ | _______ | _______ | Page ___ |
| _______ | _______ | _______ | Page ___ |

---

## Step 4: Quality Check

### Validation Questions

For each triple, ask:

#### ✅ Clarity
- [ ] Can I explain this triple to someone unfamiliar with the topic?
- [ ] Are the subject and object clearly defined concepts?
- [ ] Is the predicate unambiguous?

#### ✅ Consistency
- [ ] Do I use the same name for the same concept throughout?
- [ ] Do I use the same predicate for similar relationships?
- [ ] Are my confidence scores consistent with my certainty?

#### ✅ Completeness
- [ ] Have I captured the main concepts from the text?
- [ ] Are there obvious relationships I've missed?
- [ ] Do I have a balanced mix of relation types?

### Common Issues and Fixes

| Issue | Example | Fix |
|-------|---------|-----|
| Too granular | "nonlinear Schrödinger equation for optical fibers" | Split into multiple concepts |
| Too vague | "X is related to Y" | Find more specific relation |
| Ambiguous direction | "X and Y are connected" | Decide on direction: X→Y or Y→X |
| Missing context | "v is velocity" | Add context: "v_wave is velocity_of wave" |

### Your Issues and Decisions

**Issue encountered**: _________________________________

**Decision made**: _________________________________

**Rationale**: _________________________________

---

**Issue encountered**: _________________________________

**Decision made**: _________________________________

**Rationale**: _________________________________

---

## Step 5: Add Metadata

### Concept Descriptions

For 5-10 key concepts, write brief descriptions:

**Concept**: ________________

**Type**: [ ] concept [ ] equation [ ] quantity [ ] phenomenon

**Description** (1-2 sentences): 

_________________________________

_________________________________

**Examples** (2-3):
1. _________________________________
2. _________________________________
3. _________________________________

---

**Concept**: ________________

**Type**: [ ] concept [ ] equation [ ] quantity [ ] phenomenon

**Description** (1-2 sentences): 

_________________________________

_________________________________

**Examples** (2-3):
1. _________________________________
2. _________________________________
3. _________________________________

---

*(Repeat for additional key concepts)*

---

## Step 6: Reflection and Documentation

### What I Learned

**Most surprising finding**:

_________________________________

_________________________________

**Most difficult decision**:

_________________________________

_________________________________

**Pattern I noticed**:

_________________________________

_________________________________

### Ambiguities and Questions

**Unresolved ambiguity 1**:

_________________________________

**Possible solutions**:
- _________________________________
- _________________________________

---

**Unresolved ambiguity 2**:

_________________________________

**Possible solutions**:
- _________________________________
- _________________________________

---

### Next Steps

**Additional text to analyze**: _________________________________

**Concepts needing more research**: _________________________________

**Relations to refine**: _________________________________

---

## 📊 Summary Statistics

Fill out after completing extraction:

- **Total concepts identified**: _______
- **Total triples extracted**: _______
- **Taxonomic (is_a) relations**: _______
- **Mereological (part_of) relations**: _______
- **Prerequisite relations**: _______
- **Other relations**: _______
- **Concepts with metadata**: _______
- **Average confidence score**: _______
- **Time spent**: _______ hours

---

## 🎯 Quality Metrics

Self-assess your extraction:

| Criterion | Rating (1-5) | Notes |
|-----------|--------------|-------|
| Completeness | ___/5 | Did you capture main concepts? |
| Consistency | ___/5 | Are names and relations uniform? |
| Clarity | ___/5 | Can others understand your triples? |
| Accuracy | ___/5 | Do triples reflect the source text? |

---

## 📝 Tips for Success

### ✅ DO:
- Start with clear, unambiguous relationships
- Use consistent naming conventions (lowercase, underscores)
- Note your confidence level (not everything is 100% certain)
- Document edge cases and difficult decisions
- Take breaks—fatigue leads to inconsistent extraction

### ❌ DON'T:
- Don't worry about creating a perfect representation
- Don't spend too long on any single triple (2-3 min max)
- Don't extract triples that aren't clearly supported by text
- Don't change concept names mid-extraction
- Don't forget to save frequently!

---

## 🔄 Iteration Process

Knowledge extraction is iterative. After your first pass:

1. **Review** your triples with fresh eyes (next day)
2. **Consolidate** duplicate or similar concepts
3. **Refine** ambiguous relation types
4. **Add** missing connections you notice
5. **Document** what changed and why

---

## 📤 Export Format

When ready, transfer to CSV:

```csv
subject,predicate,object,confidence,source,notes
concept_a,is_a,concept_b,1.0,page_23,Clear statement
concept_c,part_of,concept_d,0.9,page_25,Implied relationship
concept_e,prerequisite_of,concept_f,0.8,page_27,Inferred from context
```

Or JSON:

```json
{
  "triples": [
    {
      "subject": "concept_a",
      "predicate": "is_a",
      "object": "concept_b",
      "confidence": 1.0,
      "source": "page_23",
      "notes": "Clear statement"
    }
  ]
}
```

---

## ✨ Remember

**This is research!** Your decisions, ambiguities, and questions are valuable data. Document everything—including what doesn't work. There's no single "correct" knowledge graph representation.

**You're learning by doing.** Each triple you extract teaches you about knowledge representation, your domain, and the gap between human understanding and formal structures.

Good luck with your extraction! 🚀