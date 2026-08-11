# brilliant-minds

<pre style="background: #1E1B4B; color: #C084FC; border: 1px solid #6D28D9; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 13px; line-height: 1.25; overflow-x: auto;">
<span style="color: #C084FC; font-weight: bold;"> ╔═════════════════════════════════════════════════════════════════════════════════════════╗</span>
<span style="color: #E879F9; font-weight: bold;"> ║                                                                                         ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   ██████╗ ██████╗ ██╗██╗  ██╗   ██████╗ ███╗   ███╗██╗███╗   ██╗██████╗ ███████╗        ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   ██╔══██╗██╔══██╗██║██║  ██║   ██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██╔════╝        ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   ██████╔╝██████╔╝██║██║  ██║   ██████╔╝██╔████╔██║██║██╔██╗ ██║██║  ██║███████╗        ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   ██╔══██╗██╔══██╗██║██║  ██║   ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██║  ██║╚════██║        ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   ██████╔╝██║  ██║██║███████╗   ██████╔╝██║ ╚═╝ ██║██║██║ ╚████║██████╔╝███████║        ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝   ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝        ║</span>
<span style="color: #C084FC;"> ║                                                                                         ║</span>
<span style="color: #34D399; font-weight: bold;"> ║         ───  S Y N A P T I C  K N O W L E D G E  &  R E A S O N I N G  ───              ║</span>
<span style="color: #C084FC;"> ║                                                                                         ║</span>
<span style="color: #C084FC; font-weight: bold;"> ╠═════════════════════════════════════════════════════════════════════════════════════════╣</span>
<span style="color: #C084FC;"> ║                                                                                         ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   [COGNITIVE GRAPH]        </span><span style="color: #E2E8F0;">Continuous Reasoning Nodes ──► Latent Synaptic Index          </span><span style="color: #C084FC;">║</span>
<span style="color: #C084FC;"> ║                                                                                         ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   [DELIBERATION MATRIX]    </span><span style="color: #E2E8F0;">Multi-Model Dialectics ──► Socratic Tuning & Validation       </span><span style="color: #C084FC;">║</span>
<span style="color: #C084FC;"> ║                                                                                         ║</span>
<span style="color: #E879F9; font-weight: bold;"> ║   [KNOWLEDGE SUBSTRATE]    </span><span style="color: #34D399; font-weight: bold;">Source-Grounded Memory Shards + Realtime Context Graph        </span><span style="color: #C084FC;">║</span>
<span style="color: #C084FC;"> ║                                                                                         ║</span>
<span style="color: #C084FC; font-weight: bold;"> ╚═════════════════════════════════════════════════════════════════════════════════════════╝</span>
</pre>


---

## ✨ The 81 Minds

| Category | Minds |
|----------|-------|
| **AI Pioneers** | Geoffrey Hinton, Yann LeCun, Yoshua Bengio, John McCarthy, Marvin Minsky |
| **AI Leaders** | Jeff Dean, Ilya Sutskever, Andrej Karpathy, Andrew Ng, Fei-Fei Li, Demis Hassabis, Dave Ferrucci, Edward Hu, Hugo Touvron |
| **Language Creators** | Dennis Ritchie, James Gosling, Bjarne Stroustrup, Guido van Rossum, Chris Lattner, Grace Hopper, Chuck Moore |
| **Systems** | Linus Torvalds, Ken Thompson, John Carmack, Casey Muratori, Fabrice Bellard, Martin Thompson, Brendan Gregg, Mike Acton, George Hotz, Seymour Cray |
| **Internet/Web** | Tim Berners-Lee, Vint Cerf, Bob Kahn |
| **Distributed Systems** | Leslie Lamport, Barbara Liskov |
| **Cryptography/Privacy** | David Chaum, Stuart Haber, Ralph Merkle |
| **Hardware/Business** | Jensen Huang, Steve Jobs, Elon Musk |
| **Mathematics/Logic** | Alan Turing, John von Neumann, John Nash, Kurt Godel, Donald Knuth, Claude Shannon |
| **Physics** | Albert Einstein, Richard Feynman, Nikola Tesla, Marie Curie, J. Robert Oppenheimer |
| **Historical** | Ada Lovelace, Leonardo da Vinci, Socrates, Alan Kay |

*(Includes Neuroscience, Philosophy, Psychology, and Collectives as well)*

---

## 📦 Installation

### 1. Install Fifth

```bash
git clone git@github.com:quivent/fifth.git
cd fifth/engine && make && cd ..
./engine/fifth install.fs
```

### 2. Install Brilliant Minds

```bash
git clone git@github.com:quivent/brilliant-minds.git
cd brilliant-minds
fifth install.fs
```

> [!NOTE]
> This copies the package into `~/.fifth/packages/brilliant-minds/` and records the install path so Fifth can find `agents.db` automatically. Optionally set `BRILLIANT_MINDS_ROOT` to override the install path.

---

## 🚀 Usage

### Summon a Mind (Claude Code)

```text
/shannon     # Claude Shannon - information theory lens
/linus       # Linus Torvalds - no-bullshit systems review
/ferrucci    # Dave Ferrucci - parallel consensus analysis
/feynman     # Richard Feynman - first principles
```

### Python API

```python
from brilliant_minds.src import BrilliantMindsOrchestrator, OrchestratorConfig
from pathlib import Path

config = OrchestratorConfig(
    corpus_path=Path("./minds"),
    output_path=Path("./output"),
    model_name="claude-opus-4-5-20251101"
)
orchestrator = BrilliantMindsOrchestrator(config)

# Restore and interact
hinton = await orchestrator.restore_mind("geoffrey_hinton")
questions = await orchestrator.generate_questions("geoffrey_hinton", project_info={...})
report = await orchestrator.evaluate_repository("repo_path", mind_name="geoffrey_hinton")
```

### Fifth API

```bash
# List all minds
MINDS_CMD=list fifth minds/loader.fs

# Get a specific mind
MINDS_CMD=get MINDS_ARG=claude-shannon fifth minds/loader.fs

# Search by domain, zone, or era
MINDS_CMD=search-domain MINDS_ARG=Cryptography fifth minds/loader.fs
```

---

## 🔧 Architecture

<details>
<summary>Package Structure</summary>

Research and educational use.