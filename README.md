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


## Package Structure

```
brilliant_minds/
├── README.md
├── ACTIVATION_TEMPLATE.md
│
├── minds/                          # 81 mind corpora
│   ├── loader.fs                   # Fifth loader (query by domain, zone, era)
│   ├── claude_shannon/
│   │   ├── IDENTITY.md             # Core identity encoding
│   │   ├── ACTIVATION.md           # Activation protocol
│   │   ├── CONTEXT.md              # Socratic tuner context
│   │   ├── INVOCATION.md           # Invocation script
│   │   └── research_*.md           # Extended corpus (varies by mind)
│   └── ...79 more
│
├── commands/                       # 55 Claude Code slash commands
│   ├── shannon.md                  # /shannon - summon Shannon
│   ├── linus-torvalds.md           # /linus-torvalds - summon Linus
│   ├── ferrucci.md                 # /ferrucci - summon Ferrucci
│   ├── app-agent.md                # /app-agent - project-aware agent
│   ├── project-encode.md           # /project-encode - encode project identity
│   └── ...50 more
│
├── hooks/                          # Claude Code event hooks
│   ├── settings.json               # Hook configuration (4 events)
│   ├── session-welcome.sh          # SessionStart - agent infrastructure display
│   ├── agent-sqlite                # PreToolUse - agent matching from DB
│   ├── agent-precontext-sqlite/    # Rust source for agent-sqlite
│   ├── pre-compact-lore.py         # PreCompact - transcript preservation
│   ├── transcript-to-lore.py       # SessionEnd - chronicle generation
│   └── lore_utils.py               # Shared Python utilities
│
├── db/                             # SQLite databases
│   ├── agents.db                   # 166 agents (80 minds + 86 functional) + mind_metadata
│   └── projects.db                 # Project identity encodings
│
├── protocols/                      # Protocol specifications
│   ├── identity_restoration/       # Multi-turn restoration protocol
│   ├── question_generation/        # Identity-driven question generation
│   ├── benchmark_selection/        # Benchmark selection methodology
│   ├── repository_evaluation/      # Repository evaluation process
│   └── orchestration/              # System architecture design
│
├── src/                            # Python implementation
│   ├── orchestrator.py             # Main orchestration system
│   ├── identity_restoration.py     # Identity restoration engine
│   ├── question_generation.py      # Question generation engine
│   ├── benchmark_selection.py      # Benchmark selection engine
│   └── repository_evaluation.py    # Repository evaluation engine
│
└── wiki/                           # Generated documentation
    ├── index.html                  # Wikipedia-style reference
    ├── generate_wiki.py            # HTML generator
    └── generate_protocols_wiki.py  # Protocol wiki generator
```

## The 81 Minds

| Category | Minds |
|----------|-------|
| **AI Pioneers** | Geoffrey Hinton, Yann LeCun, Yoshua Bengio, John McCarthy, Marvin Minsky |
| **AI Leaders** | Jeff Dean, Ilya Sutskever, Andrej Karpathy, Andrew Ng, Fei-Fei Li, Demis Hassabis, Dave Ferrucci, Edward Hu, Hugo Touvron |
| **Language Creators** | Dennis Ritchie, James Gosling, Bjarne Stroustrup, Guido van Rossum, Chris Lattner, Grace Hopper, Chuck Moore |
| **Systems** | Linus Torvalds, Ken Thompson, John Carmack, Casey Muratori, Fabrice Bellard, Martin Thompson, Brendan Gregg, Mike Acton, George Hotz, Seymour Cray |
| **Internet/Web** | Tim Berners-Lee, Vint Cerf, Bob Kahn |
| **Distributed Systems** | Leslie Lamport, Barbara Liskov |
| **Cryptography/Privacy** | David Chaum, Stuart Haber, Ralph Merkle |
| **Aerospace/Software Engineering** | Margaret Hamilton |
| **Hardware/Business** | Jensen Huang, Steve Jobs, Elon Musk |
| **Neuroscience** | Donald Hebb, Eric Kandel, Santiago Ramon y Cajal, Michael Hasselmo, Terrence Sejnowski, Karl Friston, David Marr, Warren McCulloch |
| **Mathematics/Logic** | Alan Turing, John von Neumann, John Nash, Kurt Godel, Donald Knuth, Claude Shannon |
| **Physics** | Albert Einstein, Richard Feynman, Nikola Tesla, Marie Curie, J. Robert Oppenheimer |
| **Philosophy/Theory** | Daniel Dennett, Douglas Hofstadter, Thomas Kuhn, Mikhail Bakhtin, Christopher Alexander, Herbert Simon, Norbert Wiener, Buckminster Fuller |
| **Psychology/Education** | B.F. Skinner, Ivan Pavlov, Paulo Freire |
| **Historical** | Ada Lovelace, Leonardo da Vinci, Socrates, Alan Kay |
| **Collectives** | Llama Collective, The Assembler, David Blaine, Wim Hof |

## Installation

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

This copies the package into `~/.fifth/packages/brilliant-minds/` and records the install path so Fifth can find `agents.db` automatically.

### Configuration

Optionally set `BRILLIANT_MINDS_ROOT` to override the install path:

```bash
export BRILLIANT_MINDS_ROOT=/path/to/brilliant-minds
```

All internal paths resolve via `${BRILLIANT_MINDS_ROOT}` or the recorded install path. External dependencies (`~/.linus/`, `~/.agents/`) are runtime-optional.

## Usage

### Summon a Mind (Claude Code)

```
/shannon     # Claude Shannon - information theory lens
/linus       # Linus Torvalds - no-bullshit systems review
/ferrucci    # Dave Ferrucci - parallel consensus analysis
/feynman     # Richard Feynman - first principles
```

### Python API

```python
from brilliant_minds.src import BrilliantMindsOrchestrator, OrchestratorConfig

config = OrchestratorConfig(
    corpus_path=Path("./minds"),
    output_path=Path("./output"),
    model_name="claude-opus-4-5-20251101"
)
orchestrator = BrilliantMindsOrchestrator(config)

hinton = await orchestrator.restore_mind("geoffrey_hinton")
questions = await orchestrator.generate_questions("geoffrey_hinton", project_info={...})
report = await orchestrator.evaluate_repository(repo_path, mind_name="geoffrey_hinton")
```

### Fifth API

```bash
# Count minds
MINDS_CMD=count fifth minds/loader.fs

# List all minds
MINDS_CMD=list fifth minds/loader.fs

# Get a specific mind
MINDS_CMD=get MINDS_ARG=claude-shannon fifth minds/loader.fs

# Search by domain, zone, or era
MINDS_CMD=search-domain MINDS_ARG=Cryptography fifth minds/loader.fs
MINDS_CMD=search-zone MINDS_ARG=synthesis fifth minds/loader.fs
MINDS_CMD=search-era MINDS_ARG=1943 fifth minds/loader.fs

# List all domains or zones
MINDS_CMD=domains fifth minds/loader.fs
MINDS_CMD=zones fifth minds/loader.fs

# Random mind
MINDS_CMD=random fifth minds/loader.fs
```

## Requirements

- Fifth (`brew tap quivent/fifth && brew install fifth`)
- Python 3.10+ (for src/ orchestrator)
- anthropic (Claude API)
- Rust toolchain (optional, to rebuild hooks/agent-sqlite)

## License

Research and educational use.