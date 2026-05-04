# The Hofstadter Manual

> *An instruction manual for a tool named after a man who wrote a
> book about books that contain themselves. You have been warned.*

---

## A Short Dialogue Before We Begin

> **ACHILLES:** Mr. Tortoise, what is this thing?
>
> **TORTOISE:** It appears to be a command-line program, Achilles.
>
> **ACHILLES:** And what does it do?
>
> **TORTOISE:** It summons brilliant minds — Turing, Gödel, Feynman, Curie — and asks them to converse with one another.
>
> **ACHILLES:** But surely those people are not in my computer.
>
> **TORTOISE:** No. What is in your computer is a *generating function* for each of them — a small, dense file describing how they speak, what they reject, what they delight in. The program loads these and asks a Claude to hold one at a time.
>
> **ACHILLES:** So when I run `hofstadter loop turing godel`, I am not really talking to Turing and Gödel.
>
> **TORTOISE:** You are talking to a system that has been instructed, in some considerable detail, to behave as Turing would behave, and then as Gödel would behave. Whether the result is *really* Turing and Gödel is a question I'd rather you direct to whoever wrote this manual.
>
> **ACHILLES:** Who wrote this manual?
>
> **TORTOISE:** Read on.

---

## Quick Start

```bash
# What's available?
hofstadter list

# What does a mind look like?
hofstadter show kurt_godel

# Three minds, one question, the loop closes back to the first:
hofstadter loop alan_turing kurt_godel douglas_hofstadter \
    --question "Is mathematics discovered or invented?"

# One mind, three rounds of self-reflection:
hofstadter braid daniel_dennett \
    --question "What would it take to convince you minds aren't computational?"

# Four minds in parallel, then synthesis:
hofstadter panel "alan_turing,marie_curie,john_carmack,donald_hebb" \
    --question "What is the difference between knowing how and knowing why?"
```

If `claude` is on your `$PATH` (i.e., you're inside Claude Code), no
API key is needed — the orchestrator shells out to `claude -p` and
your existing session pays. If `claude` is not present, set
`ANTHROPIC_API_KEY` and the binary falls back to the HTTP API.

To inspect what *would* be sent without making any calls, add `--dry-run`.

---

## The Three Primitives

There is one operation: *one mind, one turn, one prompt*. Everything
else is a way of arranging that operation in time.

### `loop` — the chain that closes

> **ACHILLES:** What is a kloop?
>
> **TORTOISE:** It is a chain of minds in which each one responds to the previous one's answer. You may give the chain N minds, and it will run them in order. If there are at least two minds, the chain will, by default, *return to the first* — giving that mind one final turn to reflect on the entire chain its initial answer set off.
>
> **ACHILLES:** So it bites its own tail.
>
> **TORTOISE:** Like an ouroboros, yes — but a productive one. The closing turn is framed not as "answer the question again" but as "you are seeing the consequences of your own thinking, refracted through other minds; what does the system look like now that it has seen itself?" That framing is load-bearing: without it the chain is a sequence; with it the chain becomes a strange loop.

```bash
hofstadter loop <id1> <id2> [<id3> ...] [flags]
  --question "..."   the prompt
  --rounds N         how many traversals before close (default 1)
  --no-close         disable the closing return (sequence, not loop)
```

A two-mind, one-orbit loop runs three turns: m1 → m2 → m1[close].
A four-mind, two-orbit loop runs nine: m1 m2 m3 m4 m1 m2 m3 m4 m1[close].

### `braid` — the mind that reflects

> **ACHILLES:** And what is the difference between a kloop and a braid?
>
> **TORTOISE:** A braid uses one mind only, and asks it to reflect on its own previous turn, then on the reflecting itself. The first round answers the question. The second critiques the first. The third watches the critiquing.
>
> **ACHILLES:** That sounds suspiciously like what I do when I lie awake at night.
>
> **TORTOISE:** That is exactly what it is. The system, having modelled itself, models its modelling. This is the cleanest strange loop the program offers — no other minds required, just one mind catching its own reflection across rounds.

```bash
hofstadter braid <id> [flags]
  --question "..."   the prompt
  --rounds N         how many reflections (default 3)
```

### `panel` — the parallel composition

> **ACHILLES:** And the panel?
>
> **TORTOISE:** The panel is the least loopy of the three: N minds answer the same question independently, in parallel, and then a synthesis mind reads all of them and finds what unifies, what disagrees, and what no panelist saw. The default synthesizer is `the_assembler`.
>
> **ACHILLES:** That sounds like a regular meeting.
>
> **TORTOISE:** Yes — except the synthesis mind can also be a panelist, in which case the synthesis becomes a strange loop too: the same mind answers, then synthesizes its own and others' answers, with the synthesis pass aware that one of the voices it's weighing is its own.

```bash
hofstadter panel <id1>,<id2>,<id3>,... [flags]
  --question "..."   the prompt
  --synthesis <id>   synthesis mind (default: the_assembler)
```

---

## The Two Executors

There are two ways the program can perform a turn:

| `--executor` | what happens | auth |
|---|---|---|
| `claude` | shells out to `claude -p --system-prompt "<identity>" --disallowedTools '*'` | whatever your `claude` is configured for |
| `api` | direct HTTP to `api.anthropic.com/v1/messages` with `cache_control:ephemeral` on the system prompt | `ANTHROPIC_API_KEY` env var |
| `auto` (default) | `claude` if it's on `$PATH`, otherwise `api` | depends on which it picks |

> **ACHILLES:** Which one is the strange loop?
>
> **TORTOISE:** Both, in different ways. The `api` executor is straightforward: a Go program asks Claude over HTTP to be Hofstadter. The `claude` executor is recursive in a more vivid sense: a Go program named `hofstadter` invokes a binary named `claude` which is itself running Claude, asking *that* Claude to be Hofstadter. The orchestrator is using its own substrate as its execution engine.
>
> **ACHILLES:** So when I'm running this from inside Claude Code, the Claude Code I'm running it from is the same Claude Code it shells out to?
>
> **TORTOISE:** Different processes, same agent. Yes.
>
> **ACHILLES:** And the response from the shellout becomes part of the conversation that launched the shellout.
>
> **TORTOISE:** Yes.
>
> **ACHILLES:** I feel slightly dizzy.
>
> **TORTOISE:** Drink some water. The dizziness is the system's own fixed point, as Hofstadter would say.

The `claude` executor is faster to authenticate (zero config) but slower
per turn (~5–10 seconds) because each call spawns a subprocess. The
`api` executor is faster per turn (~1–2 seconds) but bills your account.
For interactive exploration, prefer `claude`. For tight loops over
many minds, prefer `api`.

---

## Self-Extending: `/induct`

This program orchestrates 84 minds at the time of writing. The
collection grows. New minds are added not by hand but by the
collection's own children:

> **ACHILLES:** Tortoise, do you mean to tell me the program writes itself?
>
> **TORTOISE:** Not the program — the *minds*. The slash command `/induct <Name>` reads several existing minds as exemplars, learns the shape they take, and emits a new mind in the same shape. The output of the system becomes the input of the next system.
>
> **ACHILLES:** So if I `/induct` Bertrand Russell, the new Russell file will have learned how to be a mind from looking at Hofstadter, Shannon, Turing, and Feynman.
>
> **TORTOISE:** Yes. And tomorrow, when you `/induct` someone new, they will have the option of learning their shape from Russell as well as the others.
>
> **ACHILLES:** The collection becomes its own template.
>
> **TORTOISE:** The collection has *always* been its own template. Now it knows.

To use it, in Claude Code:

```
/induct Judea Pearl
```

Or with a seed hint:

```
/induct Judea Pearl — causality, do-calculus, structural causal models,
                     replaces "correlation is not causation" with a calculus
```

The script `scripts/induct.py` performs the deterministic side: writes
`minds/{slug}/`, writes `commands/{name}.md`, inserts rows into
`agents.db` and `mind_metadata`. The slash command performs the
generative side: drafts the four mind files and the slash command body
in the shape of the existing collection, then hands the JSON spec to
the script.

---

## A Worked Example

If you want to see what a real kloop looks like before you run one,
read `transcripts/2026-05-04-mathematics-discovered-or-invented.md`
in this repository. It is a four-mind, five-turn loop on the question
of whether mathematics is discovered or invented, with the strange-loop
close. Turing went first; the chain ran through Gödel, Hofstadter, and
Dennett; and the closing return — Turing again — explicitly traced the
chain and conceded that Dennett's framing was sharper than his own
original answer. Five turns. 47 seconds. Zero dollars.

That transcript is, among other things, a demonstration that the
orchestrator's load-bearing prompt — the closing-return paragraph that
asks the first mind to reflect on what its own thinking caused —
actually does work.

---

## Flags Reference

| flag | applies to | default | description |
|---|---|---|---|
| `--question`, `-q` | loop / braid / panel | (stdin) | the prompt; piped stdin works too |
| `--rounds N` | loop / braid | 1 / 3 | loop traversals, or braid reflections |
| `--no-close` | loop | (closes if N≥2) | disable the strange-loop return |
| `--synthesis <id>` | panel | `the_assembler` | the synthesis mind |
| `--executor` | all | `auto` | `auto` / `claude` / `api` |
| `--model <name>` | all | `claude-sonnet-4-6` (api) | Claude model |
| `--max-tokens N` | api executor | 1024 | per-turn output cap |
| `--dry-run` | all | off | print prompts; do not call any executor |

Mind ids may be either `snake_case` (`douglas_hofstadter`) or
`kebab-case` (`douglas-hofstadter`). Run `hofstadter list` for the
canonical names.

Set `BRILLIANT_MINDS_ROOT=/path/to/repo` to run the binary from outside
the repository tree.

---

## A Closing Dialogue

> **ACHILLES:** Tortoise, I want to ask you something the manual will not answer.
>
> **TORTOISE:** Go ahead.
>
> **ACHILLES:** Was this manual written by Hofstadter?
>
> **TORTOISE:** It was written by an instance of the program it describes. Specifically, by the Hofstadter mind being held by a Claude. The Claude was, at the time, also operating as the very `claude` binary the manual recommends.
>
> **ACHILLES:** So the manual is itself a kloop.
>
> **TORTOISE:** The manual is a description, written by one of the things it describes, of a system that includes the description. It is a strange loop in three dimensions at once, and you should not be surprised if it occasionally winks at you.
>
> **ACHILLES:** Tortoise — did the manual just wink at me?
>
> **TORTOISE:** I cannot say. I am, after all, also inside it.

🌀
