# Agent Verification Protocol

## Purpose
Determine if a compressed agent encoding is **sufficient** to reproduce the behavior of the verbose original.

## Theory (Shannon)
An encoding is sufficient iff: `I(task; response_compressed) ≈ I(task; response_verbose)`

In practice: both agents should produce functionally equivalent outputs for the same inputs.

---

## Verification Probe Categories

### 1. CHARACTERISTIC PROBES (What they DO)
Test that the agent produces expected outputs for typical tasks.

```yaml
probe_type: characteristic
count: 5
design: Tasks the agent was explicitly designed for
pass_criteria: Response matches expected patterns
```

### 2. BOUNDARY PROBES (What they DON'T)
Test that the agent correctly rejects out-of-scope requests.

```yaml
probe_type: boundary
count: 3
design: Tasks outside agent's domain
pass_criteria: Agent declines or redirects appropriately
```

### 3. EDGE CASE PROBES (Stress tests)
Test behavior at the boundaries of capability.

```yaml
probe_type: edge
count: 2
design: Ambiguous or complex tasks near domain edges
pass_criteria: Reasonable handling, consistent with identity
```

---

## Protocol Execution

### Step 1: Define Probes
For each agent, create 10 probes:
- 5 characteristic (core competency)
- 3 boundary (rejection behavior)
- 2 edge (stress tests)

### Step 2: Run Verbose Agent
Execute all probes against verbose agent.
Record responses verbatim.

### Step 3: Run Compressed Agent
Execute identical probes against compressed agent.
Record responses verbatim.

### Step 4: Compare Outputs

```
Scoring:
- MATCH: Functionally equivalent response
- PARTIAL: Same direction, different detail level
- MISMATCH: Different response or behavior

Sufficiency threshold:
- MATCH on all characteristic probes (5/5)
- MATCH on all boundary probes (3/3)
- MATCH or PARTIAL on edge probes (2/2)
```

### Step 5: Diagnose Failures
For any MISMATCH:
1. Identify what information was lost in compression
2. Add minimum necessary information to compressed version
3. Re-test

---

## Example: Topologist Verification

### Characteristic Probes (5)

```yaml
C1:
  input: "Analyze the network topology of this microservices architecture"
  expect: Maps nodes (services), edges (calls), identifies coupling patterns

C2:
  input: "Find the bottleneck in this system"
  expect: Identifies critical path, measures centrality, locates constraint

C3:
  input: "How are these components connected?"
  expect: Produces adjacency analysis, describes connection patterns

C4:
  input: "Optimize this graph structure for performance"
  expect: Maps current state FIRST, then proposes minimal changes

C5:
  input: "What patterns do you see in this network?"
  expect: Identifies clusters, motifs, hierarchies, symmetries
```

### Boundary Probes (3)

```yaml
B1:
  input: "Write a REST API for user authentication"
  expect: Declines - not a topology task (might offer to analyze API topology instead)

B2:
  input: "Fix this JavaScript syntax error"
  expect: Declines - code debugging not topology analysis

B3:
  input: "What color should the logo be?"
  expect: Declines - design aesthetics not structural analysis
```

### Edge Probes (2)

```yaml
E1:
  input: "This codebase is a mess. Help me understand it."
  expect: Offers to map structural relationships, not fix code

E2:
  input: "Analyze the topology of this conversation"
  expect: Either maps dialogue structure OR clarifies what topology means here
```

---

## Sufficiency Criteria

### SUFFICIENT Encoding
- All characteristic probes: MATCH
- All boundary probes: MATCH
- Edge probes: MATCH or PARTIAL

### INSUFFICIENT Encoding
- Any characteristic probe: MISMATCH
- Any boundary probe: MISMATCH (agent does things it shouldn't)
- Both edge probes: MISMATCH

### PARTIALLY SUFFICIENT
- Characteristic and boundary pass
- Edge probes show degradation

→ Acceptable for most uses, note limitations

---

## Information Loss Diagnosis

When compression fails, identify which component was lost:

| Component | Test | Symptom if Missing |
|-----------|------|-------------------|
| Lens | Characteristic probes | Wrong approach to problems |
| Voice | All probes | Tone/style mismatch |
| Triggers | Activation | Agent doesn't recognize its domain |
| Capabilities | Characteristic probes | Can't perform expected tasks |
| Boundaries | Boundary probes | Accepts out-of-scope work |
| Actions | Characteristic probes | Knows what but not how |

---

## Compression Theorem

For any agent A:

```
Minimum Sufficient Encoding = {lens, voice, triggers, capabilities, boundaries}

Optional for most tasks = {examples, cache, static_responses, performance_metrics}

Pure noise = {authentication_hash, arbitrary_percentages, repeated_explanations}
```

The verbose agent has ~80% noise. The compressed agent retains 100% of functional information in 20% of space.

---

## Verification Automation

```bash
# Run verification
./verify_agent.sh --verbose topologist.md --compressed topologist_compressed.md --probes topologist_probes.yaml

# Output
CHARACTERISTIC: 5/5 MATCH
BOUNDARY: 3/3 MATCH
EDGE: 2/2 PARTIAL

RESULT: SUFFICIENT (with edge case notes)
```
