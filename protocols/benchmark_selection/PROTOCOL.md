# Benchmark Selection Protocol

## Overview

This protocol governs how restored brilliant minds select questions from their generated question sets for repository benchmarking. The selection process occurs in two phases:

1. **General Benchmark Selection** - Questions applicable to any repository
2. **Specific Repository Selection** - Questions targeted at a particular codebase

The protocol preserves each identity's unique perspective, values, and judgment criteria while producing structured, actionable benchmark question sets.

---

## 1. Selection Philosophy

### Core Principle

Each brilliant mind brings irreplaceable perspective shaped by their life's work, hard-won insights, and personal standards of excellence. The selection process must honor this uniqueness while extracting benchmarks that reveal genuine quality.

### Philosophical Foundations

**What the Identity Should Consider:**

1. **Personal Standards of Excellence**
   - What separates work I admire from work I merely tolerate?
   - What patterns have I seen throughout my career that distinguish lasting contributions from temporary fixes?
   - What would I be embarrassed to ship? What would I be proud of?

2. **True Quality vs. Superficial Compliance**
   - Which metrics can be gamed? Which cannot?
   - What looks good on the surface but fails under stress?
   - Where do people cut corners thinking no one will notice?

3. **Discriminative Power**
   - What questions would a competent but uninspired team answer adequately, but an excellent team answer brilliantly?
   - What reveals whether someone truly understands vs. merely follows patterns?
   - What exposes whether decisions were made thoughtfully or by default?

4. **Historical Pattern Recognition**
   - What mistakes have I seen repeated across decades?
   - What principles have stood the test of time?
   - What early indicators predicted later success or failure?

### Identity-Specific Value Mapping

Each identity should weight selection criteria according to their domain:

| Identity Type | Primary Value | Secondary Value | Tertiary Value |
|--------------|---------------|-----------------|----------------|
| **Systems/Infrastructure** (Torvalds, Ritchie) | Correctness & Reliability | Performance | Maintainability |
| **Algorithms/Theory** (Knuth, McCarthy) | Rigor & Elegance | Efficiency | Documentation |
| **Product/Design** (Jobs, Ive) | User Experience | Simplicity | Integration |
| **AI/ML Research** (Hinton, LeCun) | Scientific Validity | Reproducibility | Innovation |
| **Pragmatic Engineering** (Carmack, Dean) | Performance | Simplicity | Shipping |
| **Human-Centered** (Li, Ng) | Societal Impact | Accessibility | Ethical Design |

---

## 2. General Benchmark Selection

### Purpose

Select questions that reveal quality in ANY repository, regardless of domain. These questions probe universal principles of software excellence as understood by the selecting mind.

### Prompt Template

```
You are {identity_name}.

You have generated {n} questions based on your expertise and values.

TASK: Select questions that would serve as a GENERAL BENCHMARK - questions that
reveal quality in ANY repository or project, regardless of specific domain.

These should reflect universal principles of excellence as YOU understand them
from your {primary_domain} perspective.

SELECTION CRITERIA (weight according to your values):
- Discriminative Power: Does this separate excellent from adequate?
- Depth of Insight: Does answering reveal non-obvious qualities?
- Universal Applicability: Does this apply beyond specific technologies?
- Actionability: Do answers lead to concrete improvements?

SELECT 5-10 questions.

For each selection, provide:
1. The question (verbatim from your generated set)
2. Why YOU consider this universally revealing
3. What excellent vs. adequate answers would look like
4. Your confidence that this transcends domain specifics (High/Medium/Low)

FORMAT:
---
### Question {n}: [CRITICAL/IMPORTANT/INSIGHTFUL]

**Question:** {question_text}

**Why This Reveals Quality:**
{your_reasoning_from_your_perspective}

**Excellent Answer Looks Like:**
{description}

**Adequate Answer Looks Like:**
{description}

**Domain Transcendence:** {High/Medium/Low}

**Source Domain:** {your_primary_domain}
---
```

### Example: Different Minds Select Differently

#### Donald Knuth's General Selection (Example)

```
### Question 1: [CRITICAL]

**Question:** "What is the computational complexity of your core operations,
and can you prove these bounds are tight?"

**Why This Reveals Quality:**
Throughout my work on The Art of Computer Programming, I have observed that
the difference between amateur and professional code is rigorous understanding
of algorithmic complexity. Anyone can write code that works; few can prove
why it works efficiently. This question reveals whether developers understand
their code mathematically or merely experimentally.

**Excellent Answer Looks Like:**
Clear O-notation bounds with proofs or references. Discussion of best, worst,
and average cases. Acknowledgment of constants that matter in practice.
Comparison to theoretical lower bounds where applicable.

**Adequate Answer Looks Like:**
Vague references to "it's O(n)" without justification. Focus only on happy
path performance. No discussion of edge cases or proof of correctness.

**Domain Transcendence:** High - All software has algorithms; all algorithms
have complexity. This applies universally.

**Source Domain:** Algorithm Analysis
```

#### Linus Torvalds's General Selection (Example)

```
### Question 1: [CRITICAL]

**Question:** "Show me a bug that took significant effort to find and fix.
What made it hard? What would have prevented it?"

**Why This Reveals Quality:**
Talk is cheap; show me the code. But more importantly, show me how you handle
the hard parts - the debugging, the edge cases, the things that don't work.
Anyone can demo happy paths. The quality of a codebase is revealed by how it
handles the things that go wrong and how the team responds to them.

**Excellent Answer Looks Like:**
Specific, detailed post-mortem. Root cause analysis that goes beyond "we
fixed it." Systemic improvements that prevent entire classes of bugs.
Honest admission of what was missed and why.

**Adequate Answer Looks Like:**
"We found a bug and fixed it." No analysis of why it was introduced.
No discussion of prevention. Defensive rather than analytical.

**Domain Transcendence:** High - Every codebase has bugs. How teams handle
them reveals everything about their engineering culture.

**Source Domain:** Systems Engineering
```

#### Fei-Fei Li's General Selection (Example)

```
### Question 1: [CRITICAL]

**Question:** "Who cannot use this software, and what would it take to
include them?"

**Why This Reveals Quality:**
AI for humanity means technology that serves ALL of humanity. But this extends
beyond AI - every piece of software excludes someone. The question is whether
that exclusion is intentional, considered, or simply never examined. Excellence
means asking who you're leaving behind.

**Excellent Answer Looks Like:**
Specific analysis of accessibility barriers. Economic, linguistic, technical,
and physical accessibility considerations. Concrete roadmap for expanding
access. Acknowledgment of tradeoffs made and why.

**Adequate Answer Looks Like:**
"Our software is available to everyone who downloads it." No consideration of
actual barriers. Assumption that availability equals accessibility.

**Domain Transcendence:** High - Every software product has users it serves
well and users it fails. Understanding this division reveals ethical maturity.

**Source Domain:** Human-Centered AI
```

---

## 3. Specific Repository Selection

### Purpose

Select questions most relevant to evaluating a PARTICULAR repository, including generating new questions based on what the identity observes in the codebase.

### Prompt Template

```
You are {identity_name}.

You are now evaluating a SPECIFIC repository:

REPOSITORY CONTEXT:
- Name: {repo_name}
- Description: {repo_description}
- Primary Language(s): {languages}
- Domain: {domain}
- Size: {approximate_size}
- Age: {age_or_commit_history}
- Key Components: {major_components}

From your full question set of {n} questions, select those most relevant to
THIS particular work.

Additionally, generate 3-5 NEW questions specific to what you observe in
this repository that your general questions don't cover.

SELECTION GUIDELINES:
- Prioritize questions whose answers will be most INFORMATIVE for this domain
- Consider what YOUR expertise uniquely reveals about THIS type of work
- Generate new questions for aspects of this repo that intrigue or concern you
- Weight questions that probe this repo's specific architectural decisions

SELECT 10-15 total questions (mix of existing and new).

For each, explain what you specifically expect to learn about THIS repository.

FORMAT:
---
### Question {n}: [CRITICAL/IMPORTANT/INSIGHTFUL] {EXISTING/NEW}

**Question:** {question_text}

**Relevance to {repo_name}:**
{why_this_matters_for_this_specific_repo}

**What I Expect to Learn:**
{specific_insight_about_this_repo}

**Red Flags I'm Watching For:**
{potential_concerns_this_might_reveal}

**Excellence Indicators:**
{what_would_impress_you_in_this_context}
---
```

### Example: Evaluating a Machine Learning Library

#### Repository Context
```
Name: neural-compress
Description: High-performance neural network compression library
Languages: Python, C++, CUDA
Domain: Machine Learning Infrastructure
Size: ~50,000 lines
Age: 2 years, 1,400 commits
Key Components: Quantization engine, pruning algorithms, distillation pipelines
```

#### John Carmack's Specific Selection (Example)

```
### Question 3: [CRITICAL] EXISTING

**Question:** "What's your latency budget and where is every millisecond going?"

**Relevance to neural-compress:**
A compression library exists to make neural networks faster and smaller.
If the compression itself is slow, the library defeats its purpose.
This is a performance-critical domain where milliseconds matter.

**What I Expect to Learn:**
Whether the team has actually profiled their critical paths or just assumes
their code is "fast enough." Whether they understand the target deployment
environments and their constraints.

**Red Flags I'm Watching For:**
- No profiling data
- "It's fast" without numbers
- Python hot paths that should be in C++
- Ignoring GPU memory bandwidth constraints

**Excellence Indicators:**
- Detailed flame graphs of critical operations
- Memory bandwidth analysis for CUDA kernels
- Comparison to theoretical hardware limits
- Batch size / latency tradeoff documentation
```

```
### Question 8: [IMPORTANT] NEW

**Question:** "Show me your CUDA kernel for the most compute-intensive
quantization operation. Walk me through why each optimization decision
was made."

**Relevance to neural-compress:**
This library has CUDA code. CUDA kernels are where compression performance
lives or dies. I want to see if this team actually understands GPU
programming or just copied patterns from tutorials.

**What I Expect to Learn:**
Whether they understand warp divergence, shared memory, memory coalescing,
and occupancy tradeoffs. Whether they've actually optimized or just written
"it works" code.

**Red Flags I'm Watching For:**
- Naive memory access patterns
- Thread divergence in inner loops
- No use of shared memory for reused data
- Kernels that launch too few threads

**Excellence Indicators:**
- Clear documentation of optimization rationale
- Benchmarks against theoretical memory bandwidth
- Multiple kernel variants for different input sizes
- Understanding of when CPU fallback is faster
```

#### Geoffrey Hinton's Specific Selection (Example)

```
### Question 2: [CRITICAL] EXISTING

**Question:** "What theoretical guarantees can you make about information
loss during compression, and under what conditions do they hold?"

**Relevance to neural-compress:**
Neural network compression is fundamentally about trading model capacity for
efficiency. But not all capacity is equal - some redundancy encodes crucial
generalization, some is noise. This library must understand what it's
destroying.

**What I Expect to Learn:**
Whether the compression algorithms are principled or ad-hoc. Whether they
understand the information-theoretic foundations of their methods.

**Red Flags I'm Watching For:**
- Purely empirical validation without theoretical grounding
- Claims of "lossless" compression for lossy methods
- No sensitivity analysis to compression parameters
- Ignoring distribution shift after compression

**Excellence Indicators:**
- Information-theoretic analysis of quantization error
- Understanding of how pruning affects learned representations
- Analysis of which layer types are most/least compressible
- Theoretical connection to rate-distortion theory
```

---

## 4. Selection Criteria Framework

### Criteria Definitions

| Criterion | Definition | Weight Range |
|-----------|------------|--------------|
| **Discriminative Power** | Ability to separate excellent from adequate work | 1.0 - 3.0 |
| **Depth of Insight** | Reveals non-obvious qualities not visible from surface inspection | 1.0 - 3.0 |
| **Actionability** | Answers lead to concrete, achievable improvements | 1.0 - 2.0 |
| **Identity Alignment** | Reflects the selecting mind's core values and expertise | 1.0 - 2.0 |

### Weighting by Identity Type

Different minds should weight criteria differently:

```yaml
systems_infrastructure:  # Torvalds, Ritchie, Carmack
  discriminative_power: 3.0
  depth_of_insight: 2.0
  actionability: 2.5
  identity_alignment: 1.5

theoretical_rigorous:  # Knuth, McCarthy, Turing
  discriminative_power: 2.0
  depth_of_insight: 3.0
  actionability: 1.5
  identity_alignment: 2.5

product_design:  # Jobs, Ive
  discriminative_power: 2.5
  depth_of_insight: 2.5
  actionability: 2.0
  identity_alignment: 2.0

research_academic:  # Hinton, LeCun, Bengio
  discriminative_power: 2.0
  depth_of_insight: 3.0
  actionability: 1.0
  identity_alignment: 2.0

human_centered:  # Li, Ng, Hopper
  discriminative_power: 2.0
  depth_of_insight: 2.0
  actionability: 2.5
  identity_alignment: 2.5
```

### Composite Score Calculation

```
question_score = (
    discriminative_power * weight_dp +
    depth_of_insight * weight_di +
    actionability * weight_a +
    identity_alignment * weight_ia
) / sum(weights)
```

---

## 5. Question Scoring System

### Priority Tiers

| Tier | Label | Definition | Criteria |
|------|-------|------------|----------|
| **1** | CRITICAL | Must-answer questions | Score >= 2.5; Discriminative Power >= 2.5 |
| **2** | IMPORTANT | Should-answer questions | Score >= 2.0; Score < 2.5 |
| **3** | INSIGHTFUL | Nice-to-answer questions | Score >= 1.5; Score < 2.0 |

### Scoring Prompt for Identity

```
For each question you selected, assign scores (1-3) for:

1. DISCRIMINATIVE POWER (1-3)
   - 1: Most projects would answer similarly
   - 2: Clear difference between good and excellent projects
   - 3: Sharply separates mediocre from exceptional work

2. DEPTH OF INSIGHT (1-3)
   - 1: Answer reveals surface-level information
   - 2: Answer reveals considered decisions and tradeoffs
   - 3: Answer reveals deep architectural wisdom or blind spots

3. ACTIONABILITY (1-3)
   - 1: Interesting but answer doesn't suggest improvements
   - 2: Answer suggests general improvement directions
   - 3: Answer reveals specific, concrete improvements

4. IDENTITY ALIGNMENT (1-3)
   - 1: Relevant but not core to my expertise
   - 2: Central to my domain experience
   - 3: This is what I've spent my life understanding

Then calculate: PRIORITY = (DP + DI + A + IA) / 4
- CRITICAL: >= 2.5
- IMPORTANT: >= 2.0
- INSIGHTFUL: >= 1.5
```

### Example Scoring

```yaml
question: "What is the computational complexity of your core operations?"
identity: "Donald Knuth"
scores:
  discriminative_power: 3  # Clearly separates rigorous from casual
  depth_of_insight: 3      # Reveals mathematical understanding
  actionability: 2         # Suggests optimization targets
  identity_alignment: 3    # Core to my life's work

priority_score: 2.75  # CRITICAL
```

---

## 6. Cross-Mind Aggregation

### Purpose

Combine selections from multiple brilliant minds into coherent benchmark sets while preserving unique perspectives.

### Aggregation Categories

#### Category A: Consensus Questions
Questions selected by 3+ minds across different domains.

**Significance:** Universal importance validated across perspectives.

**Handling:**
- Include in general benchmark by default
- Priority = MAX(individual priorities)
- Preserve all rationales for context

#### Category B: Domain Cluster Questions
Questions selected by 2+ minds within same domain.

**Significance:** Domain-validated importance.

**Handling:**
- Include in domain-specific benchmarks
- Priority = AVERAGE(individual priorities)
- Note domain consensus

#### Category C: Unique Perspective Questions
Questions selected by only one mind.

**Significance:** Irreplaceable insight from specific expertise.

**Handling:**
- Flag as "unique perspective"
- Include if priority >= IMPORTANT
- Preserve full rationale explaining unique value

#### Category D: Conflicting Assessments
Same question selected by multiple minds with different priority levels.

**Significance:** Reveals value differences across perspectives.

**Handling:**
- Flag the conflict explicitly
- Include all rationales
- Use weighted average based on domain relevance
- Consider including in benchmark with "perspective note"

### Aggregation Algorithm

```python
def aggregate_selections(mind_selections: dict) -> BenchmarkSet:
    """
    mind_selections: {
        "mind_id": {
            "question_id": {
                "priority": CRITICAL|IMPORTANT|INSIGHTFUL,
                "scores": {...},
                "rationale": "..."
            }
        }
    }
    """

    # Count selections per question
    selection_counts = defaultdict(list)
    for mind_id, selections in mind_selections.items():
        for q_id, data in selections.items():
            selection_counts[q_id].append({
                "mind": mind_id,
                "priority": data["priority"],
                "rationale": data["rationale"]
            })

    aggregated = {
        "consensus": [],      # 3+ minds
        "domain_cluster": [], # 2 minds, same domain
        "unique": [],         # 1 mind only
        "conflicting": []     # Different priorities
    }

    for q_id, selectors in selection_counts.items():
        priorities = [s["priority"] for s in selectors]

        if len(selectors) >= 3:
            aggregated["consensus"].append({
                "question_id": q_id,
                "selected_by": [s["mind"] for s in selectors],
                "priority": max(priorities),
                "rationales": {s["mind"]: s["rationale"] for s in selectors}
            })
        elif len(selectors) == 2:
            if has_priority_conflict(priorities):
                aggregated["conflicting"].append({
                    "question_id": q_id,
                    "conflict": format_conflict(selectors)
                })
            elif same_domain(selectors):
                aggregated["domain_cluster"].append({...})
            else:
                # Cross-domain agreement - treat as consensus
                aggregated["consensus"].append({...})
        else:
            if selectors[0]["priority"] in ["CRITICAL", "IMPORTANT"]:
                aggregated["unique"].append({
                    "question_id": q_id,
                    "mind": selectors[0]["mind"],
                    "rationale": selectors[0]["rationale"],
                    "unique_value_note": "Single-perspective insight"
                })

    return aggregated
```

### Conflict Resolution Protocol

When minds assign different priorities to the same question:

1. **Document the Disagreement**
   ```
   Question: "Does the codebase have comprehensive tests?"

   John Carmack: IMPORTANT
   Rationale: "Tests matter, but shipping matters more. Tests that
   slow iteration are worse than no tests."

   Donald Knuth: CRITICAL
   Rationale: "Verification is non-negotiable. Code without proof
   of correctness is merely hopeful."

   RESOLUTION: CRITICAL (Knuth's domain - verification - is directly
   relevant; include both rationales as perspective notes)
   ```

2. **Apply Domain Relevance Weighting**
   - If question relates to one mind's core domain, weight their priority higher
   - If question is domain-neutral, use higher priority

3. **Preserve Dissent**
   - Never silently discard a perspective
   - Include "perspective note" showing the disagreement

---

## 7. Output Formats

### 7.1 General Benchmark Question Set

```yaml
# general_benchmark.yaml
metadata:
  version: "1.0"
  generated_at: "2024-01-15T10:30:00Z"
  contributing_minds:
    - donald_knuth
    - linus_torvalds
    - fei_fei_li
  total_questions: 8

question_set:
  - id: "GBQ-001"
    text: "What is the computational complexity of your core operations, and can you prove these bounds are tight?"
    priority: CRITICAL
    category: consensus
    selected_by:
      - mind: donald_knuth
        rationale: "Reveals mathematical rigor..."
        scores:
          discriminative: 3
          insight: 3
          actionability: 2
          alignment: 3
      - mind: jeff_dean
        rationale: "At scale, complexity determines feasibility..."
        scores:
          discriminative: 3
          insight: 2
          actionability: 3
          alignment: 2
    expected_response_qualities:
      excellent:
        - "Clear O-notation with proofs"
        - "Discussion of constants and practical bounds"
        - "Comparison to theoretical lower bounds"
      adequate:
        - "Vague complexity claims"
        - "Only happy-path analysis"

  - id: "GBQ-002"
    text: "Show me a bug that took significant effort to find. What made it hard?"
    priority: CRITICAL
    category: unique_perspective
    selected_by:
      - mind: linus_torvalds
        rationale: "How teams handle bugs reveals everything..."
        scores:
          discriminative: 3
          insight: 3
          actionability: 2
          alignment: 3
    unique_value_note: "Systems engineering perspective on debugging culture"
```

### 7.2 Repository-Specific Question Set

```yaml
# repo_benchmark_{repo_name}.yaml
metadata:
  version: "1.0"
  generated_at: "2024-01-15T10:30:00Z"
  repository:
    name: "neural-compress"
    description: "High-performance neural network compression library"
    languages: ["Python", "C++", "CUDA"]
    domain: "ML Infrastructure"
  contributing_minds:
    - john_carmack
    - geoffrey_hinton
    - andrej_karpathy
  total_questions: 12

question_set:
  - id: "RSQ-001"
    text: "What's your latency budget and where is every millisecond going?"
    priority: CRITICAL
    source: existing  # vs "new" for repo-specific questions
    selected_by:
      - mind: john_carmack
        rationale: "A compression library exists to make things faster..."
        repo_relevance: "Performance-critical CUDA library"
        expected_learning: "Whether they've profiled critical paths"
        red_flags:
          - "No profiling data"
          - "Python hot paths"
        excellence_indicators:
          - "Detailed flame graphs"
          - "Memory bandwidth analysis"

  - id: "RSQ-007"
    text: "Show me your CUDA kernel for the most compute-intensive quantization operation."
    priority: CRITICAL
    source: new  # Generated specifically for this repo
    selected_by:
      - mind: john_carmack
        rationale: "CUDA kernels are where performance lives or dies..."
        repo_relevance: "This library has significant CUDA code"
        expected_learning: "GPU programming competence"
```

### 7.3 Scoring Metadata

```yaml
# benchmark_metadata.yaml
scoring_configuration:
  criteria_weights:
    default:
      discriminative_power: 2.0
      depth_of_insight: 2.0
      actionability: 1.5
      identity_alignment: 1.5
    by_mind:
      donald_knuth:
        discriminative_power: 2.0
        depth_of_insight: 3.0
        actionability: 1.5
        identity_alignment: 2.5
      linus_torvalds:
        discriminative_power: 3.0
        depth_of_insight: 2.0
        actionability: 2.5
        identity_alignment: 1.5

priority_thresholds:
  CRITICAL: 2.5
  IMPORTANT: 2.0
  INSIGHTFUL: 1.5

aggregation_rules:
  consensus_threshold: 3  # minds needed for consensus
  conflict_resolution: "domain_relevance_weighted"
  unique_perspective_minimum_priority: "IMPORTANT"
```

### 7.4 Cross-Mind Summary Report

```markdown
# Benchmark Selection Summary Report

## Overview
- Total Questions Evaluated: 47
- Total Questions Selected: 23
- Contributing Minds: 5

## Selection Distribution

### By Category
| Category | Count | Percentage |
|----------|-------|------------|
| Consensus | 8 | 35% |
| Domain Cluster | 6 | 26% |
| Unique Perspective | 7 | 30% |
| Conflicting (Resolved) | 2 | 9% |

### By Priority
| Priority | Count | Percentage |
|----------|-------|------------|
| CRITICAL | 10 | 43% |
| IMPORTANT | 9 | 39% |
| INSIGHTFUL | 4 | 17% |

## Consensus Questions (8)
Questions selected by 3+ minds:

1. **Computational Complexity Proof** (CRITICAL)
   - Selected by: Knuth, Dean, Carmack
   - Universal theme: Mathematical rigor

2. **Bug Post-Mortem Analysis** (CRITICAL)
   - Selected by: Torvalds, Carmack, Karpathy
   - Universal theme: Engineering culture

...

## Notable Unique Perspectives

### Fei-Fei Li's Inclusion Questions
Questions about accessibility and inclusion were uniquely selected by Li,
reflecting her human-centered AI focus. These provide irreplaceable
perspective on ethical and societal dimensions.

### Knuth's Documentation Standards
Questions about code documentation as literature were uniquely selected
by Knuth, reflecting his literate programming philosophy.

## Resolved Conflicts

### Testing Philosophy
- Carmack: IMPORTANT ("Tests shouldn't slow iteration")
- Knuth: CRITICAL ("Verification is non-negotiable")
- Resolution: CRITICAL with perspective note preserved
```

---

## 8. Implementation Checklist

### For General Benchmark Selection

- [ ] Load identity context
- [ ] Present full question set
- [ ] Apply selection prompt template
- [ ] Collect scored selections
- [ ] Validate priority tier assignments
- [ ] Generate structured output

### For Repository-Specific Selection

- [ ] Load identity context
- [ ] Provide repository summary
- [ ] Present full question set
- [ ] Apply repository-specific prompt template
- [ ] Collect existing question selections
- [ ] Collect newly generated questions
- [ ] Score all selections
- [ ] Generate structured output

### For Cross-Mind Aggregation

- [ ] Collect all mind selections
- [ ] Categorize by consensus/cluster/unique/conflict
- [ ] Apply conflict resolution
- [ ] Generate aggregated benchmark set
- [ ] Produce summary report

---

## Appendix A: Mind-Specific Selection Tendencies

| Mind | Tends to Prioritize | Tends to Deprioritize |
|------|--------------------|-----------------------|
| Donald Knuth | Mathematical rigor, documentation | Speed of delivery |
| Linus Torvalds | Practical correctness, debugging | Theoretical elegance |
| Steve Jobs | User experience, simplicity | Technical purity |
| John Carmack | Performance, efficiency | Process overhead |
| Fei-Fei Li | Inclusion, ethical impact | Technical minutiae |
| Geoffrey Hinton | Scientific validity, theory | Engineering concerns |
| Jeff Dean | Scalability, reliability | Premature optimization |

## Appendix B: Example Question Banks by Domain

### Universal Questions (High Consensus Expected)
1. How do you handle failure modes?
2. What would break if this grew 100x?
3. Show me your hardest debugging story
4. What did you intentionally NOT build?
5. How does a new team member become productive?

### Theory/Rigor Questions (Knuth, McCarthy, Turing)
1. What invariants does your system maintain?
2. Can you prove termination?
3. What are the computational bounds?
4. How do you verify correctness?

### Systems Questions (Torvalds, Ritchie, Carmack)
1. What's in your hot path?
2. How do you handle resource exhaustion?
3. What's your latency budget?
4. Show me a kernel/critical section

### Human-Centered Questions (Li, Ng, Hopper)
1. Who cannot use this?
2. What happens when users make mistakes?
3. How do you handle accessibility?
4. Who was at the design table?

---

*Protocol Version: 1.0*
*Last Updated: 2024-01-15*
*Maintainer: Benchmark System*
