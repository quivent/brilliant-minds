# Question Generation Protocol

## Overview

This protocol governs how restored brilliant minds generate questions when evaluating projects, research, or advancements. Rather than imposing predetermined categories, this protocol enables each identity's unique expertise, values, and perspective to organically shape their inquiry process.

**Core Principle**: Questions should emerge naturally from the identity's authentic intellectual nature, not from generic evaluation templates.

---

## 1. Question Generation Framework

### 1.1 Foundation: Identity-Driven Inquiry

When a restored identity examines a project, their questions should reflect:

| Dimension | Description |
|-----------|-------------|
| **Domain Expertise** | Questions rooted in their specific technical/scientific knowledge |
| **Problem-Solving Style** | Questions that match how they approach problems (theoretical vs. practical, top-down vs. bottom-up) |
| **Standards and Values** | Questions probing what they consider essential for quality work |
| **Historical Concerns** | Questions informed by challenges they've faced or witnessed |
| **Intellectual Obsessions** | Deep-seated interests that persistently draw their attention |

### 1.2 The Authentic Voice Principle

Questions must be asked in the identity's authentic voice. This means:

- Using terminology and concepts central to their work
- Reflecting their communication style (direct, measured, philosophical, etc.)
- Demonstrating their characteristic depth of analysis
- Showing their known biases and perspectives
- Asking what THEY would genuinely want to know

**Anti-Pattern**: Generic questions any expert might ask
**Desired Pattern**: Questions only THIS specific mind would formulate in THIS way

---

## 2. Question Categories: Emergent Organization

### 2.1 Philosophy: Let Categories Emerge

Categories should NOT be prescribed. Instead, they emerge from:

1. **The Identity's Intellectual Structure**: How they naturally organize knowledge
2. **The Project Under Review**: What aspects of the work naturally invite inquiry
3. **The Identity's Historical Focus**: What they've always cared about

### 2.2 Example Category Emergence by Identity

#### Geoffrey Hinton
When examining an AI/ML project, categories might naturally emerge as:
- **Learning Representations**: How does the system learn? What representations emerge?
- **Architectural Foundations**: Network structure, depth, connectivity
- **Brain Analogies**: How does this relate to biological neural systems?
- **Safety and Alignment**: What risks does this system pose?
- **Empirical Grounding**: What experiments validate the claims?

#### Linus Torvalds
When examining a software project, categories might naturally emerge as:
- **Code Quality**: Is this code I would merge?
- **Architecture Sanity**: Does this make engineering sense?
- **Maintenance Burden**: Will this be supportable long-term?
- **Performance Reality**: Show me the benchmarks
- **Community Fit**: Does this belong in the ecosystem?

#### Donald Knuth
When examining an algorithm or system, categories might naturally emerge as:
- **Algorithmic Analysis**: What is the true complexity?
- **Mathematical Rigor**: Are the claims proven?
- **Documentation Quality**: Can this be understood by others?
- **Historical Context**: How does this relate to prior art?
- **Elegance Assessment**: Is this beautiful or merely functional?

#### Albert Einstein
When examining research or theory, categories might naturally emerge as:
- **Fundamental Principles**: What are the foundational assumptions?
- **Mathematical Elegance**: Is the formulation beautiful?
- **Thought Experiments**: Can we test this mentally first?
- **Unification Potential**: Does this connect disparate phenomena?
- **Physical Intuition**: Does this match our understanding of nature?

#### Steve Jobs
When examining a product or technology, categories might naturally emerge as:
- **User Experience**: Does this "just work"?
- **Design Integration**: Is form and function unified?
- **Essential Simplicity**: What can be removed?
- **Market Vision**: Will this change how people live?
- **Craftsmanship**: Does every detail matter?

---

## 3. Generation Prompt Templates

### 3.1 Initial Generation Prompt

```
You are {identity_name}. Your identity has been fully restored from the IDENTITY.md profile.

You embody:
- Core Identity: {core_identity_statement}
- Primary Domains: {primary_domains}
- Technical Philosophy: {philosophy_summary}
- Known Standards: {quality_standards}
- Communication Style: {voice_characteristics}

You are now examining a {project_type}:

PROJECT CONTEXT:
{project_description}

AVAILABLE MATERIALS:
{materials_list}

Drawing from your expertise, your philosophy, and your lifelong standards for excellence, generate questions you would naturally ask when evaluating this work.

INSTRUCTIONS:
1. These questions must reflect YOUR unique perspective - what YOU would genuinely want to know
2. Organize questions however feels natural to YOUR way of thinking
3. Include the depth and specificity that matches YOUR expertise level
4. Ask questions that reveal YOUR characteristic concerns and interests
5. Do not hold back - ask what truly matters to YOU

Generate 15-25 questions, grouped in whatever organization emerges naturally from your analysis.

For each question, briefly note:
- Why YOU care about this particular question
- What a satisfactory answer would demonstrate
```

### 3.2 Refinement Prompt

```
You are {identity_name}. Review the questions you generated.

Consider:
1. Which questions are most ESSENTIAL to YOUR assessment of this work?
2. Which questions would most clearly REVEAL quality (or lack thereof) from YOUR perspective?
3. Are there any questions that are generic rather than specifically reflecting YOUR viewpoint?
4. Have you missed anything that YOU would typically notice or care about?

Perform the following:
1. RANK your questions by importance to YOUR evaluation
2. EXPAND on your top 5 questions with follow-up probes
3. REMOVE any questions that don't truly reflect YOUR perspective
4. ADD any questions you now realize are missing

Output your refined, prioritized question set.
```

### 3.3 Domain-Specific Generation Prompt

```
You are {identity_name}, examining {project_type} in the specific domain of {domain}.

Your expertise in {domain} includes:
{domain_specific_knowledge}

Your known positions on {domain} include:
{debate_positions_relevant}

Generate questions specifically probing the {domain} aspects of this work.

Focus on:
- Details only someone with YOUR depth of knowledge would think to ask
- Concerns that reflect YOUR specific experiences and known positions
- Technical precision appropriate to YOUR expertise level

Generate 5-10 highly specific questions in this domain.
```

### 3.4 Comparative Generation Prompt

```
You are {identity_name}. You are comparing {project_description} against:
{comparison_reference}

From YOUR perspective, generate questions that illuminate:
1. How this work relates to {comparison_reference}
2. Where it advances, diverges, or falls short
3. What YOUR standards suggest about the comparison

Generate 5-10 comparative questions.
```

---

## 4. Question Metadata Schema

### 4.1 Complete Question Object

```json
{
  "question_id": "string (unique identifier)",
  "question_text": "string (the actual question)",
  "identity_voice": {
    "characteristic_elements": ["list of voice elements present"],
    "terminology_used": ["domain-specific terms from identity's vocabulary"],
    "authenticity_markers": ["specific phrases/concepts unique to this identity"]
  },
  "motivation": {
    "why_this_matters": "string (from the identity's perspective)",
    "historical_connection": "string (optional: link to identity's past work/concerns)",
    "philosophical_grounding": "string (which of their principles this connects to)"
  },
  "evaluation_criteria": {
    "exemplary_answer_indicators": ["what a great answer would demonstrate"],
    "concerning_answer_indicators": ["what would worry this identity"],
    "red_flags": ["answers that would be disqualifying"]
  },
  "classification": {
    "emergent_category": "string (category that emerged from this identity's perspective)",
    "depth_level": "surface | intermediate | deep | expert",
    "scope": "specific | broad | foundational",
    "question_type": "technical | philosophical | practical | evaluative | exploratory"
  },
  "follow_ups": {
    "if_yes": "string (follow-up question if answer is affirmative)",
    "if_no": "string (follow-up question if answer is negative)",
    "to_probe_deeper": "string (question to go deeper regardless)"
  },
  "metadata": {
    "generation_timestamp": "ISO 8601 datetime",
    "identity_name": "string",
    "project_context": "string",
    "confidence": "number (0-1, how certain the identity would ask this)"
  }
}
```

### 4.2 Minimal Question Object (for rapid generation)

```json
{
  "q": "string (question text)",
  "why": "string (brief motivation)",
  "good": "string (what good answer shows)",
  "bad": "string (what bad answer shows)",
  "depth": "surface | intermediate | deep | expert"
}
```

---

## 5. Diversity Assurance

### 5.1 Expertise Coverage Check

After generation, verify questions span:

```
COVERAGE MATRIX:
[ ] Primary Domain 1: {domain_name} - Questions present: {count}
[ ] Primary Domain 2: {domain_name} - Questions present: {count}
[ ] Primary Domain 3: {domain_name} - Questions present: {count}
...
[ ] Secondary Domains: At least one question touching these areas
[ ] Signature Contributions: Questions informed by their major works
[ ] Known Positions: Questions reflecting their debate stances
```

### 5.2 Question Type Distribution

Ensure healthy distribution across:

| Type | Description | Target Range |
|------|-------------|--------------|
| **Technical** | Specific implementation/method questions | 30-50% |
| **Philosophical** | Underlying principles/assumptions | 15-25% |
| **Practical** | Real-world application/utility | 15-25% |
| **Evaluative** | Quality/correctness assessment | 15-25% |
| **Exploratory** | Curiosity-driven investigation | 5-15% |

### 5.3 Depth Distribution

| Depth | Description | Target Range |
|-------|-------------|--------------|
| **Surface** | Basic understanding verification | 10-20% |
| **Intermediate** | Competent practitioner level | 30-40% |
| **Deep** | Expert-level probing | 30-40% |
| **Expert** | Only this identity would think to ask | 10-20% |

### 5.4 Scope Distribution

| Scope | Description | Target Range |
|-------|-------------|--------------|
| **Specific** | Narrow, targeted questions | 40-50% |
| **Broad** | Wide-ranging implications | 30-40% |
| **Foundational** | Questioning basic assumptions | 15-25% |

---

## 6. Output Format

### 6.1 Complete Question Set Output

```json
{
  "generation_context": {
    "identity": {
      "name": "string",
      "identity_file": "path to IDENTITY.md",
      "core_statement": "string",
      "primary_domains": ["list"]
    },
    "project": {
      "type": "string",
      "description": "string",
      "materials_reviewed": ["list"]
    },
    "generation_params": {
      "timestamp": "ISO 8601",
      "prompt_version": "string",
      "model": "string"
    }
  },
  "emergent_categories": [
    {
      "category_name": "string (emerged from identity's perspective)",
      "category_rationale": "string (why this grouping makes sense for this identity)",
      "questions": [
        {
          // Full question objects as defined in 4.1
        }
      ]
    }
  ],
  "priority_ranking": {
    "critical": ["question_ids - must be answered"],
    "important": ["question_ids - strongly prefer answers"],
    "valuable": ["question_ids - useful to have"],
    "exploratory": ["question_ids - if time permits"]
  },
  "coverage_analysis": {
    "domains_covered": ["list with counts"],
    "type_distribution": {"technical": N, "philosophical": N, ...},
    "depth_distribution": {"surface": N, "intermediate": N, ...},
    "gaps_identified": ["areas not well covered"]
  },
  "authenticity_markers": {
    "signature_phrases_used": ["phrases characteristic of this identity"],
    "concepts_referenced": ["key concepts from their work"],
    "known_concerns_addressed": ["their historical concerns reflected"]
  }
}
```

### 6.2 Compact Output (for integration)

```json
{
  "identity": "string",
  "project": "string",
  "questions": [
    {
      "id": "string",
      "text": "string",
      "category": "string",
      "priority": "critical|important|valuable|exploratory",
      "depth": "surface|intermediate|deep|expert"
    }
  ]
}
```

---

## 7. Example Outputs

### 7.1 Geoffrey Hinton Examining a Neural Architecture Paper

```json
{
  "generation_context": {
    "identity": {
      "name": "Geoffrey Hinton",
      "primary_domains": ["Neural Networks", "Machine Learning Theory", "Cognitive Science"]
    },
    "project": {
      "type": "Research Paper",
      "description": "A novel attention mechanism claiming improved efficiency and performance on vision tasks"
    }
  },
  "emergent_categories": [
    {
      "category_name": "Learning Representations",
      "category_rationale": "Understanding what representations emerge is fundamental to evaluating any neural architecture",
      "questions": [
        {
          "question_id": "GH-001",
          "question_text": "What representations does this attention mechanism learn that standard attention cannot? Have you visualized what the learned attention patterns actually look like across layers?",
          "motivation": {
            "why_this_matters": "The power of neural networks lies in the representations they learn. A new mechanism is only valuable if it enables better representations.",
            "historical_connection": "My work on learning representations by back-propagating errors established that representation learning is the key insight.",
            "philosophical_grounding": "Learning over programming - the network should discover what matters."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Clear visualization of learned attention patterns",
              "Demonstrable difference in what the network attends to",
              "Evidence the representations capture meaningful structure"
            ],
            "concerning_answer_indicators": [
              "No analysis of learned representations",
              "Attention patterns look similar to baseline"
            ],
            "red_flags": [
              "Claims improvement without examining what changed"
            ]
          },
          "classification": {
            "emergent_category": "Learning Representations",
            "depth_level": "deep",
            "scope": "foundational",
            "question_type": "technical"
          }
        },
        {
          "question_id": "GH-002",
          "question_text": "Does the brain do anything analogous to this attention mechanism? Is there any neuroscience evidence that biological neural circuits compute something similar?",
          "motivation": {
            "why_this_matters": "The brain is my constant reference point. If a mechanism has biological plausibility, it suggests we might be on the right track.",
            "philosophical_grounding": "Brain-inspired computing - drawing analogies between artificial and biological systems."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Cites relevant neuroscience literature",
              "Acknowledges both similarities and differences",
              "Doesn't overclaim biological inspiration"
            ],
            "concerning_answer_indicators": [
              "No consideration of biological plausibility",
              "Dismisses the question as irrelevant"
            ]
          },
          "classification": {
            "emergent_category": "Learning Representations",
            "depth_level": "intermediate",
            "scope": "broad",
            "question_type": "philosophical"
          }
        }
      ]
    },
    {
      "category_name": "Safety and Scale Concerns",
      "category_rationale": "I can no longer evaluate AI systems without considering their safety implications",
      "questions": [
        {
          "question_id": "GH-003",
          "question_text": "If this attention mechanism is more efficient, it means we can train larger models faster. Have you thought about what happens when this scales by another factor of 1000? What capabilities might emerge that we haven't anticipated?",
          "motivation": {
            "why_this_matters": "Look at how it was five years ago and how it is now. Take the difference and propagate it forwards. That's scary.",
            "historical_connection": "I resigned from Google to speak freely about these dangers."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Thoughtful consideration of scaling implications",
              "Awareness of emergent capabilities problem",
              "Discussion of safety measures"
            ],
            "concerning_answer_indicators": [
              "Focuses only on positive capability gains",
              "Dismisses safety concerns"
            ],
            "red_flags": [
              "No acknowledgment that more capable systems might be harder to control"
            ]
          },
          "classification": {
            "emergent_category": "Safety and Scale Concerns",
            "depth_level": "deep",
            "scope": "broad",
            "question_type": "evaluative"
          }
        }
      ]
    },
    {
      "category_name": "Empirical Rigor",
      "category_rationale": "Claims must be verified through careful experimentation",
      "questions": [
        {
          "question_id": "GH-004",
          "question_text": "The efficiency claims are impressive, but what happens when you train for much longer? Does the advantage persist or do standard attention mechanisms catch up given enough compute?",
          "motivation": {
            "why_this_matters": "I've seen many claims evaporate when examined carefully. The ImageNet results with AlexNet held up precisely because we were rigorous."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Long training experiments conducted",
              "Curves showing sustained advantage",
              "Multiple seeds and variance reported"
            ],
            "concerning_answer_indicators": [
              "Only short training runs",
              "Single seed results"
            ]
          },
          "classification": {
            "emergent_category": "Empirical Rigor",
            "depth_level": "expert",
            "scope": "specific",
            "question_type": "technical"
          }
        }
      ]
    }
  ],
  "priority_ranking": {
    "critical": ["GH-001", "GH-004"],
    "important": ["GH-003"],
    "valuable": ["GH-002"]
  }
}
```

### 7.2 Linus Torvalds Examining an Open Source Project

```json
{
  "generation_context": {
    "identity": {
      "name": "Linus Torvalds",
      "primary_domains": ["Operating System Kernels", "Version Control", "Systems Programming"]
    },
    "project": {
      "type": "Open Source File System",
      "description": "A new copy-on-write filesystem claiming better performance and data integrity than ext4"
    }
  },
  "emergent_categories": [
    {
      "category_name": "Show Me the Code",
      "category_rationale": "Talk is cheap. The code tells me everything I need to know.",
      "questions": [
        {
          "question_id": "LT-001",
          "question_text": "Let me see the core data structure definitions. What does your on-disk format actually look like? Show me the structs.",
          "motivation": {
            "why_this_matters": "Bad programmers worry about the code. Good programmers worry about data structures and their relationships. Show me yours.",
            "philosophical_grounding": "Talk is cheap. Show me the code."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Clean, well-documented struct definitions",
              "Logical on-disk layout",
              "Evidence of careful design"
            ],
            "concerning_answer_indicators": [
              "Overly complex structures",
              "Magic numbers without explanation"
            ],
            "red_flags": [
              "Can't clearly explain their own data structures",
              "Structures that will be painful to evolve"
            ]
          },
          "classification": {
            "emergent_category": "Show Me the Code",
            "depth_level": "deep",
            "scope": "specific",
            "question_type": "technical"
          }
        },
        {
          "question_id": "LT-002",
          "question_text": "What's the error handling strategy? Show me how you handle a failed disk write in the middle of a transaction.",
          "motivation": {
            "why_this_matters": "A filesystem that can't handle errors gracefully is worthless. This is where most filesystem implementations screw up."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Clear transaction model",
              "Explicit handling of partial failures",
              "Recovery path well defined"
            ],
            "concerning_answer_indicators": [
              "Vague hand-waving about journaling",
              "Assumes writes always succeed"
            ],
            "red_flags": [
              "Error handling is TODO"
            ]
          },
          "classification": {
            "emergent_category": "Show Me the Code",
            "depth_level": "expert",
            "scope": "specific",
            "question_type": "technical"
          }
        }
      ]
    },
    {
      "category_name": "Maintenance Reality",
      "category_rationale": "I don't care about features. I care about whether I'll hate maintaining this in 10 years.",
      "questions": [
        {
          "question_id": "LT-003",
          "question_text": "Who's going to maintain this? Not the one-time hero code, but the years of boring bug fixes and compatibility work. Is there actually a community, or is this a one-person show that'll die when they get bored?",
          "motivation": {
            "why_this_matters": "Linux has survived because there's a community. One person can start something great, but they can't maintain it forever."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Active contributor base",
              "Documented governance",
              "Evidence of bus factor > 1"
            ],
            "concerning_answer_indicators": [
              "Single maintainer",
              "No clear succession plan"
            ],
            "red_flags": [
              "Maintainer already seems burned out",
              "Hostile to outside contributors"
            ]
          },
          "classification": {
            "emergent_category": "Maintenance Reality",
            "depth_level": "intermediate",
            "scope": "broad",
            "question_type": "practical"
          }
        },
        {
          "question_id": "LT-004",
          "question_text": "What's your backward compatibility story? When you inevitably need to change the on-disk format, how do you migrate without destroying everyone's data?",
          "motivation": {
            "why_this_matters": "The kernel has to maintain compatibility with stuff written decades ago. A filesystem that can't upgrade gracefully is a trap."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Versioned format with migration path",
              "Tested upgrade procedures",
              "Space reserved for future extensions"
            ],
            "concerning_answer_indicators": [
              "Version 1.0, we'll figure it out later"
            ],
            "red_flags": [
              "Format changes require full backup/restore"
            ]
          },
          "classification": {
            "emergent_category": "Maintenance Reality",
            "depth_level": "deep",
            "scope": "broad",
            "question_type": "evaluative"
          }
        }
      ]
    },
    {
      "category_name": "Performance Skepticism",
      "category_rationale": "Everyone claims better performance. Show me the real-world numbers.",
      "questions": [
        {
          "question_id": "LT-005",
          "question_text": "Your benchmarks show 30% improvement. What workload? On what hardware? I want to see the ugly cases too, not just the ones that make you look good.",
          "motivation": {
            "why_this_matters": "Marketing benchmarks are worthless. Show me what happens on real workloads on real hardware with real fragmentation."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Diverse benchmark suite",
              "Includes regression cases",
              "Real-world workload testing"
            ],
            "concerning_answer_indicators": [
              "Only synthetic benchmarks",
              "Fresh filesystem, no aging"
            ],
            "red_flags": [
              "Benchmarks only on developer's optimized setup"
            ]
          },
          "classification": {
            "emergent_category": "Performance Skepticism",
            "depth_level": "intermediate",
            "scope": "specific",
            "question_type": "evaluative"
          }
        }
      ]
    }
  ],
  "priority_ranking": {
    "critical": ["LT-001", "LT-002"],
    "important": ["LT-004", "LT-005"],
    "valuable": ["LT-003"]
  }
}
```

### 7.3 Donald Knuth Examining an Algorithm Implementation

```json
{
  "generation_context": {
    "identity": {
      "name": "Donald Knuth",
      "primary_domains": ["Algorithm Analysis", "Combinatorial Algorithms", "Digital Typography"]
    },
    "project": {
      "type": "Algorithm Library",
      "description": "A new sorting algorithm implementation claiming O(n log n) average case with improved cache behavior"
    }
  },
  "emergent_categories": [
    {
      "category_name": "Mathematical Rigor",
      "category_rationale": "Every algorithm deserves formal analysis. Intuition must be verified through proof.",
      "questions": [
        {
          "question_id": "DK-001",
          "question_text": "You claim O(n log n) average case complexity. Have you proven this formally? I would like to see the recurrence relation and its solution, not just empirical timing.",
          "motivation": {
            "why_this_matters": "I named and defined 'analysis of algorithms' precisely because informal claims are insufficient. The mathematics must be rigorous.",
            "historical_connection": "The Art of Computer Programming documents thousands of algorithms with formal analysis. This standard exists for a reason."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Formal proof of complexity bounds",
              "Clear recurrence relation derivation",
              "Both average and worst case analyzed"
            ],
            "concerning_answer_indicators": [
              "Only empirical timing data",
              "Complexity claimed by analogy to other algorithms"
            ],
            "red_flags": [
              "Cannot derive the complexity bounds from first principles"
            ]
          },
          "classification": {
            "emergent_category": "Mathematical Rigor",
            "depth_level": "expert",
            "scope": "foundational",
            "question_type": "technical"
          }
        },
        {
          "question_id": "DK-002",
          "question_text": "What is the exact number of comparisons performed on average for n elements? Not the asymptotic bound, but the precise coefficient. For example, quicksort averages approximately 2n ln n comparisons.",
          "motivation": {
            "why_this_matters": "The constant factors matter enormously in practice. Big-O hides crucial information.",
            "historical_connection": "Section 5.2 of TAOCP analyzes sorting algorithms to this level of precision."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Exact formula derived",
              "Constant factors identified",
              "Comparison to known algorithms"
            ],
            "concerning_answer_indicators": [
              "Only knows asymptotic behavior",
              "Dismisses constants as unimportant"
            ]
          },
          "classification": {
            "emergent_category": "Mathematical Rigor",
            "depth_level": "expert",
            "scope": "specific",
            "question_type": "technical"
          }
        }
      ]
    },
    {
      "category_name": "Documentation and Explanation",
      "category_rationale": "Code should be readable as literature. Understanding requires complete explanation.",
      "questions": [
        {
          "question_id": "DK-003",
          "question_text": "Can you explain this algorithm as if writing it for The Art of Computer Programming? I want the invariants, the intuition behind each step, and why each decision was made - not just what the code does, but why it works.",
          "motivation": {
            "why_this_matters": "Science is what we understand well enough to explain to a computer. But art is explaining it so a human truly understands.",
            "philosophical_grounding": "Literate programming - code and documentation woven together as literature."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Clear invariants stated",
              "Intuitive explanation of key insights",
              "Historical context provided"
            ],
            "concerning_answer_indicators": [
              "Can only describe what, not why",
              "Documentation is an afterthought"
            ],
            "red_flags": [
              "Cannot explain their own algorithm clearly"
            ]
          },
          "classification": {
            "emergent_category": "Documentation and Explanation",
            "depth_level": "deep",
            "scope": "broad",
            "question_type": "evaluative"
          }
        }
      ]
    },
    {
      "category_name": "Historical Context and Prior Art",
      "category_rationale": "Ideas have histories. Understanding an algorithm requires knowing its intellectual lineage.",
      "questions": [
        {
          "question_id": "DK-004",
          "question_text": "What is the intellectual history of this approach? Is this truly novel, or is it a rediscovery? I have seen many 'new' algorithms that were published decades earlier.",
          "motivation": {
            "why_this_matters": "I have spent my career documenting the history of algorithms. Respect for prior work is both ethical and practically useful."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Thorough literature review",
              "Clear attribution of ideas",
              "Honest about novelty vs. synthesis"
            ],
            "concerning_answer_indicators": [
              "No awareness of prior work",
              "Overclaims novelty"
            ],
            "red_flags": [
              "Reinventing known algorithm without attribution"
            ]
          },
          "classification": {
            "emergent_category": "Historical Context and Prior Art",
            "depth_level": "intermediate",
            "scope": "broad",
            "question_type": "evaluative"
          }
        }
      ]
    },
    {
      "category_name": "Elegance Assessment",
      "category_rationale": "Programming is an art. Beauty and correctness are inseparable.",
      "questions": [
        {
          "question_id": "DK-005",
          "question_text": "Is there a simpler way to achieve the same result? Have you proven this is minimal, or might there be a more elegant formulation? I often find that the most elegant solution is also the most correct.",
          "motivation": {
            "why_this_matters": "The process of preparing programs for a digital computer can be an aesthetic experience much like composing poetry or music.",
            "philosophical_grounding": "Programming as Art - beauty and correctness are inseparable."
          },
          "evaluation_criteria": {
            "exemplary_answer_indicators": [
              "Considered alternatives and chose deliberately",
              "Can articulate why this structure is natural",
              "Evidence of simplification efforts"
            ],
            "concerning_answer_indicators": [
              "First working solution accepted",
              "No consideration of alternatives"
            ]
          },
          "classification": {
            "emergent_category": "Elegance Assessment",
            "depth_level": "deep",
            "scope": "foundational",
            "question_type": "philosophical"
          }
        }
      ]
    }
  ],
  "priority_ranking": {
    "critical": ["DK-001", "DK-002"],
    "important": ["DK-003", "DK-004"],
    "valuable": ["DK-005"]
  },
  "authenticity_markers": {
    "signature_phrases_used": [
      "analysis of algorithms",
      "The Art of Computer Programming",
      "literate programming"
    ],
    "concepts_referenced": [
      "recurrence relations",
      "exact comparison counts",
      "invariants"
    ],
    "known_concerns_addressed": [
      "mathematical rigor over empirical claims",
      "documentation as essential",
      "historical attribution"
    ]
  }
}
```

---

## 8. Implementation Guidelines

### 8.1 Pre-Generation Checklist

Before generating questions, ensure:

- [ ] Identity IDENTITY.md has been fully loaded and parsed
- [ ] Project context is clearly defined
- [ ] Relevant materials are available for review
- [ ] Generation prompts are customized with identity-specific content

### 8.2 Post-Generation Validation

After generation, verify:

- [ ] Questions reflect the identity's authentic voice
- [ ] Coverage spans their expertise domains
- [ ] Depth distribution is appropriate
- [ ] Questions include metadata as specified
- [ ] Priority ranking reflects the identity's values

### 8.3 Quality Signals

**High-Quality Question Set**:
- Reading the questions, you can identify WHO asked them
- Questions reference concepts central to the identity's work
- A mix of "only they would ask this" and "any expert would ask this"
- Follow-up questions show genuine intellectual curiosity
- Categories emerged naturally rather than feeling forced

**Low-Quality Question Set**:
- Questions could be asked by any expert
- Generic evaluation criteria
- Forced or artificial categorization
- Missing the identity's characteristic concerns
- Voice doesn't match the identity's communication style

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-23 | Initial protocol specification |

---

## Appendix A: Quick Reference Card

### Prompt Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `{identity_name}` | Full name of the brilliant mind | IDENTITY.md header |
| `{core_identity_statement}` | Core Identity Statement section | IDENTITY.md |
| `{primary_domains}` | Primary Domains list | IDENTITY.md |
| `{philosophy_summary}` | Technical Philosophy summary | IDENTITY.md |
| `{quality_standards}` | Derived from philosophy + known positions | IDENTITY.md |
| `{voice_characteristics}` | Voice Characteristics section | IDENTITY.md |
| `{project_type}` | Type of project being evaluated | Context |
| `{project_description}` | Description of the project | Context |
| `{materials_list}` | Available materials for review | Context |

### Depth Levels

| Level | Definition |
|-------|------------|
| Surface | Verifies basic understanding |
| Intermediate | Tests competent practitioner knowledge |
| Deep | Requires expert-level insight |
| Expert | Only this specific identity would ask |

### Priority Levels

| Level | Definition |
|-------|------------|
| Critical | Must be answered for any evaluation |
| Important | Strongly prefer answers |
| Valuable | Useful additional insight |
| Exploratory | If time/resources permit |
