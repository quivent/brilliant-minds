package main

import (
	"fmt"
	"strconv"
	"strings"
)

type runFlags struct {
	question     string
	rounds       int
	model        string
	modelSet     bool // true if --model was explicitly given
	maxTokens    int
	executor     string
	close        bool
	closeSet     bool // true if --close or --no-close was explicitly given
	dryRun       bool
	synthesis    string
}

// parseRunArgs is a minimal hand-rolled flag parser that allows positional
// arguments and flags to interleave. Unknown flags error out.
func parseRunArgs(args []string) (*runFlags, []string, error) {
	rf := &runFlags{
		model:     defaultModel,
		maxTokens: defaultMaxTokens,
		executor:  "auto",
		close:     true,
		synthesis: "the_assembler",
	}
	var pos []string

	i := 0
	next := func(name string) (string, error) {
		i++
		if i >= len(args) {
			return "", fmt.Errorf("flag %s needs a value", name)
		}
		return args[i], nil
	}

	for ; i < len(args); i++ {
		a := args[i]
		// support --flag=value
		var val string
		var hasEq bool
		if strings.HasPrefix(a, "--") {
			if eq := strings.IndexByte(a, '='); eq >= 0 {
				val = a[eq+1:]
				a = a[:eq]
				hasEq = true
			}
		}
		take := func(name string) (string, error) {
			if hasEq {
				return val, nil
			}
			return next(name)
		}

		switch a {
		case "--question", "-q":
			v, err := take(a)
			if err != nil {
				return nil, nil, err
			}
			rf.question = v
		case "--rounds":
			v, err := take(a)
			if err != nil {
				return nil, nil, err
			}
			n, err := strconv.Atoi(v)
			if err != nil {
				return nil, nil, fmt.Errorf("--rounds: %w", err)
			}
			rf.rounds = n
		case "--model":
			v, err := take(a)
			if err != nil {
				return nil, nil, err
			}
			rf.model = v
			rf.modelSet = true
		case "--executor":
			v, err := take(a)
			if err != nil {
				return nil, nil, err
			}
			rf.executor = v
		case "--max-tokens":
			v, err := take(a)
			if err != nil {
				return nil, nil, err
			}
			n, err := strconv.Atoi(v)
			if err != nil {
				return nil, nil, fmt.Errorf("--max-tokens: %w", err)
			}
			rf.maxTokens = n
		case "--close":
			rf.close = true
			rf.closeSet = true
		case "--no-close":
			rf.close = false
			rf.closeSet = true
		case "--dry-run":
			rf.dryRun = true
		case "--synthesis":
			v, err := take(a)
			if err != nil {
				return nil, nil, err
			}
			rf.synthesis = v
		default:
			if strings.HasPrefix(a, "-") {
				return nil, nil, fmt.Errorf("unknown flag: %s", a)
			}
			pos = append(pos, a)
		}
	}
	return rf, pos, nil
}

func cmdList(args []string) {
	_ = args
	slugs, err := listMinds()
	if err != nil {
		die(err)
	}
	for _, s := range slugs {
		m, err := loadMind(s)
		if err != nil {
			fmt.Printf("%-32s  (error: %v)\n", s, err)
			continue
		}
		fmt.Printf("%-32s  %s\n", s, m.Name)
	}
	fmt.Printf("\n%d minds.\n", len(slugs))
}

func cmdShow(args []string) {
	if len(args) < 1 {
		dieMsg("usage: hofstadter show <id>")
	}
	m, err := loadMind(args[0])
	if err != nil {
		die(err)
	}
	fmt.Print(m.Activation)
}

func cmdSummon(args []string) {
	if len(args) < 1 {
		dieMsg("usage: hofstadter summon <id>")
	}
	m, err := loadMind(args[0])
	if err != nil {
		die(err)
	}
	fmt.Print(m.SystemPrompt())
}

func cmdLoop(args []string) {
	rf, pos, err := parseRunArgs(args)
	if err != nil {
		die(err)
	}
	if len(pos) < 1 {
		dieMsg("usage: hofstadter loop <id1> [id2 ...] [flags]")
	}
	if rf.rounds < 1 {
		rf.rounds = 1
	}
	q := resolveQuestion(rf.question)
	close := rf.close
	if !rf.closeSet {
		close = len(pos) >= 2 // default: close only if 2+ minds
	}

	var minds []*Mind
	for _, id := range pos {
		m, err := loadMind(id)
		if err != nil {
			die(err)
		}
		minds = append(minds, m)
	}

	if err := Loop(minds, RunOpts{
		Question:      q,
		Rounds:        rf.rounds,
		Model:         rf.model,
		ModelExplicit: rf.modelSet,
		MaxTokens:     rf.maxTokens,
		Executor:      rf.executor,
		DryRun:        rf.dryRun,
		Close:         close,
	}); err != nil {
		die(err)
	}
}

func cmdBraid(args []string) {
	rf, pos, err := parseRunArgs(args)
	if err != nil {
		die(err)
	}
	if len(pos) != 1 {
		dieMsg("usage: hofstadter braid <id> [flags]")
	}
	if rf.rounds < 1 {
		rf.rounds = 3
	}
	q := resolveQuestion(rf.question)

	m, err := loadMind(pos[0])
	if err != nil {
		die(err)
	}
	if err := Braid(m, RunOpts{
		Question:      q,
		Rounds:        rf.rounds,
		Model:         rf.model,
		ModelExplicit: rf.modelSet,
		MaxTokens:     rf.maxTokens,
		Executor:      rf.executor,
		DryRun:        rf.dryRun,
	}); err != nil {
		die(err)
	}
}

func cmdPanel(args []string) {
	rf, pos, err := parseRunArgs(args)
	if err != nil {
		die(err)
	}
	if len(pos) != 1 {
		dieMsg("usage: hofstadter panel <id1>,<id2>,... [flags]")
	}
	ids := strings.Split(pos[0], ",")
	if len(ids) < 2 {
		dieMsg("panel needs at least 2 minds (got %d)", len(ids))
	}
	q := resolveQuestion(rf.question)

	var minds []*Mind
	for _, id := range ids {
		id = strings.TrimSpace(id)
		if id == "" {
			continue
		}
		m, err := loadMind(id)
		if err != nil {
			die(err)
		}
		minds = append(minds, m)
	}
	syn, err := loadMind(rf.synthesis)
	if err != nil {
		die(fmt.Errorf("synthesis mind %q: %w", rf.synthesis, err))
	}
	if err := Panel(minds, syn, RunOpts{
		Question:      q,
		Model:         rf.model,
		ModelExplicit: rf.modelSet,
		MaxTokens:     rf.maxTokens,
		Executor:      rf.executor,
		DryRun:        rf.dryRun,
	}); err != nil {
		die(err)
	}
}

func resolveQuestion(fromFlag string) string {
	if fromFlag != "" {
		return fromFlag
	}
	piped := readStdin()
	if piped != "" {
		return piped
	}
	dieMsg("provide --question or pipe one on stdin")
	return ""
}
