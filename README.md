<div align="center">

```
 ____       _ _ _ _             _   __  __ _           _     
| __ ) _ __(_) | (_) __ _ _ __ | |_|  \/  (_)_ __   __| |___ 
|  _ \| '__| | | | |/ _` | '_ \| __| |\/| | | '_ \ / _` / __|
| |_) | |  | | | | | (_| | | | | |_| |  | | | | | | (_| \__ \
|____/|_|  |_|_|_|_|\__,_|_| |_|\__|_|  |_|_|_| |_|\__,_|___/
```

**Brilliant Minds**

*AI identity restoration system for 81 brilliant minds — from Shannon to Socrates.*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Research-green.svg?style=for-the-badge)](#license)

</div>

---

## 📑 Table of Contents

- [⚡ Overview](#-overview)
- [✨ The 81 Minds](#-the-81-minds)
- [📦 Installation](#-installation)
- [🚀 Usage](#-usage)
- [🔧 Architecture](#-architecture)

---

## ⚡ Overview

Restores the intellectual identity of historical and contemporary figures into AI agents, enabling perspective-driven evaluation, question generation, and multi-mind discourse.

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

```
brilliant_minds/
├── minds/                          # 81 mind corpora
│   ├── claude_shannon/
│   │   ├── IDENTITY.md             # Core identity encoding
│   │   ├── ACTIVATION.md           # Activation protocol
│   │   ├── CONTEXT.md              # Socratic tuner context
│   │   └── INVOCATION.md           # Invocation script
├── commands/                       # 55 Claude Code slash commands
├── hooks/                          # Claude Code event hooks
├── db/                             # SQLite databases (agents, projects)
├── protocols/                      # Protocol specifications
├── src/                            # Python implementation
└── wiki/                           # Generated documentation
```
</details>

> [!IMPORTANT]
> Requires Fifth, Python 3.10+, the `anthropic` package, and optionally a Rust toolchain to rebuild hooks/agent-sqlite.
