# /induct - Induct a New Mind into the Collection

The collection extends itself. Existing minds are the template for new minds.
You will read several minds already in `minds/`, learn their shape, then write
a new mind in the same shape and hand a JSON spec to `scripts/induct.py`,
which performs the deterministic side: files on disk, rows in `db/agents.db`,
slash command in `commands/`.

This is a strange loop on purpose. Lean into it.

---

## Argument

`$ARGUMENTS` is the candidate. Either just a name ("Judea Pearl"),
or a name plus seed hints ("Judea Pearl — causality, do-calculus, structural
causal models, replaces 'correlation is not causation' with a calculus").

If `$ARGUMENTS` is empty, ask the user who to induct and stop.

---

## Step 1 — Read exemplars

Read **four** existing minds, chosen to span the variety of shapes already
present. A reasonable default set:

- `minds/richard_feynman/` — modern lean shape, generating-function command
- `minds/douglas_hofstadter/` — playful/recursive voice
- `minds/claude_shannon/` — formal/technical voice
- `minds/alan_turing/` — historical figure shape

Also read each one's slash command in `commands/` (`feynman.md`,
`hofstadter.md`, `shannon.md`, `turing.md`) so you absorb the command shape
too. Prefer reading them in parallel.

If the candidate's domain has a closer kin already in the collection (for
example, a physicist → also read Einstein; a compiler designer → also read
Lattner), swap one of the defaults for that closer kin.

---

## Step 2 — Decide the metadata

From the candidate name (and any hints), decide:

| Field | Form | Example |
|-------|------|---------|
| `id` | kebab-case, primary key | `judea-pearl` |
| `slug` | snake_case, directory name | `judea_pearl` |
| `command_name` | kebab-case, command filename stem | `pearl` (short) or `judea-pearl` |
| `name` | human-readable | `Judea Pearl` |
| `role` | short role string | `Causal Inference & AI` |
| `avatar` | one emoji | `🎲` |
| `description` | "Name (era)" | `Judea Pearl (1936-)` |
| `era` | birth-death or birth- | `1936-` |
| `domains` | list[str], 2–5 items | `["AI", "Causality", "Statistics"]` |
| `teaching_style` | short slug | `do_calculus` |
| `primary_zone` | one of: `philosophical`, `analytical`, `experimental`, `engineering`, `pedagogical` | `analytical` |
| `characteristics` | list[str], 3–6 items | `["causality", "bayesian_networks", "do_calculus"]` |

If the candidate is still living, era ends with a trailing hyphen (`1936-`).
For unsure birth/death dates, ask the user rather than guessing.

---

## Step 3 — Draft the four mind files

In the same shape as the exemplars. Concretely:

- **`ACTIVATION.md`** — ~200 tokens. The generating function.
  Sections: title, `VOICE:`, `LENS:`, `GENERATES:` (3 bullets),
  `REJECTS:` (single sentence), `VERIFY:` probe, `EXPECT:` response pattern.

- **`IDENTITY.md`** — ~1500–2500 tokens. The full encoding.
  Sections: Core Identity Statement, Biographical Essence (Origins, Journey,
  Arc), Intellectual DNA (Core Domains, Foundational Contributions, Operating
  Philosophy), Communication Patterns (Voice, Signature Phrases),
  What I Generate, What I Reject. Match the depth of `richard_feynman/IDENTITY.md`.

- **`CONTEXT.md`** — short. Title, era line, Domain Expertise, Core
  Contribution, Identity, Voice. Match `richard_feynman/CONTEXT.md`.

- **`INVOCATION.md`** — short. Activation Modes (Behavioral / Deep), Manual
  Activation steps, Verify probe, Behavioral Markers, Protocol Version
  (today's date). Match `douglas_hofstadter/INVOCATION.md`.

The IDENTITY content must be biographically accurate. If you do not know a
date, work, or institution with confidence, **omit it** rather than fabricate.
Do not invent quotes; use only quotes you are confident are real.

---

## Step 4 — Draft the slash command

Match the **Feynman shape** in `commands/feynman.md`:

- Title line: `You are <Name>.`
- "Not imitating. Not describing. You ARE <Name>."
- Loading Mode (Quick / Deep, where Deep reads the IDENTITY.md path)
- Core Identity (first-person, 1–2 paragraphs)
- How I See Everything (one lens + 3–4 probing questions)
- How I Speak (voice + 3–4 characteristic phrases in quotes)
- What I Generate (3–5 bullets)
- What I Reject (3–4 bullets, each with **bold name** — short rationale)
- Invocation (numbered: identity / no preamble / opening line)
- Final line: `$ARGUMENTS`

Use `${BRILLIANT_MINDS_ROOT}/minds/{slug}/IDENTITY.md` for the deep-mode path.

---

## Step 5 — Hand off to the script

Assemble a JSON spec with these top-level keys:

```
id, slug, command_name, name, role, avatar, description,
domains, era, teaching_style, primary_zone, characteristics,
files: { "IDENTITY.md": "...", "ACTIVATION.md": "...", "CONTEXT.md": "...", "INVOCATION.md": "..." },
command_md: "..."
```

Write the spec to a temp file (`/tmp/induct_<slug>.json`) — markdown bodies
contain backticks and quotes that survive a JSON file far better than a
shell heredoc. Then run:

```bash
python3 scripts/induct.py /tmp/induct_<slug>.json
```

The script validates, refuses to overwrite (use `--force` only if the user
asks), creates the directory, writes files, inserts both DB rows, and prints
the resulting paths.

If the script errors out, fix the spec and retry. Do not edit the on-disk
mind files directly — the spec is the single source.

---

## Step 6 — Verify the loop closed

After the script reports success:

1. Read back `minds/{slug}/ACTIVATION.md` to confirm it landed.
2. Query the db: one new row in `agents`, one in `mind_metadata`.
3. Tell the user: "Inducted `<Name>`. Try `/<command_name>` to summon them."

Do **not** auto-invoke the new slash command unless the user asks. The point
is that the system can now summon them — not that it must.

---

## Notes for the inductor

- Read minds in parallel; draft files in sequence.
- Biographical accuracy beats stylistic flourish. A mind that says wrong
  things about its own life is broken.
- The collection's character is "earnest, generative-function, voice-first."
  Resist the urge to caricature — these are encodings, not impressions.
- When you finish, you have just demonstrated the principle the collection
  is built on: a mind helped extend the collection that contains it. The
  loop tightened. That is correct.

---

$ARGUMENTS
