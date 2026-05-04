package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
)

// CLIExecutor shells out to the local `claude` binary in headless mode.
// This makes the orchestrator's runtime the same agent that's running
// the orchestrator — Claude Code summoning Claude Code, with each turn
// scoped to a single mind's identity via --system-prompt.
//
// We pass the mind's full system prompt via --system-prompt (which
// REPLACES claude's default system prompt, so no CLAUDE.md or hooks
// metadata bleeds in), and lock all tools off so the response is pure
// text generation — no file reads, no bash, no slash commands.
type CLIExecutor struct {
	bin           string
	model         string
	modelExplicit bool

	totalCalls    int
	totalDuration time.Duration
}

func NewCLIExecutor(model string, modelExplicit bool) (*CLIExecutor, error) {
	bin, err := exec.LookPath("claude")
	if err != nil {
		return nil, fmt.Errorf("claude binary not found on PATH: %w", err)
	}
	return &CLIExecutor{
		bin:           bin,
		model:         model,
		modelExplicit: modelExplicit,
	}, nil
}

func (e *CLIExecutor) Name() string { return "claude" }

func (e *CLIExecutor) Call(system string, msgs []apiMessage) (string, error) {
	prompt := flattenHistory(msgs)

	args := []string{
		"-p",
		"--system-prompt", system,
		"--disallowedTools", "*",
	}
	if e.modelExplicit && e.model != "" {
		args = append(args, "--model", e.model)
	}

	cmd := exec.Command(e.bin, args...)
	cmd.Stdin = strings.NewReader(prompt)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	start := time.Now()
	err := cmd.Run()
	e.totalCalls++
	e.totalDuration += time.Since(start)

	if err != nil {
		return "", fmt.Errorf("claude exited (%v): %s", err, truncate(stderr.String(), 400))
	}
	resp := strings.TrimSpace(stdout.String())
	if resp == "" {
		return "", fmt.Errorf("claude produced no output (stderr: %s)", truncate(stderr.String(), 400))
	}
	return resp, nil
}

func (e *CLIExecutor) PrintUsage() {
	if e == nil || e.totalCalls == 0 {
		return
	}
	fmt.Fprintf(os.Stderr,
		"\n[usage claude] calls=%d total_duration=%s avg=%s\n",
		e.totalCalls, e.totalDuration.Round(time.Millisecond),
		(e.totalDuration / time.Duration(e.totalCalls)).Round(time.Millisecond),
	)
}

// flattenHistory collapses an apiMessage history into a single text prompt
// suitable for `claude -p`. The CLI accepts only one input prompt per call,
// so multi-turn history is folded into a transcript with role markers.
// For single-user-message histories, we pass the content through unchanged.
func flattenHistory(msgs []apiMessage) string {
	if len(msgs) == 0 {
		return ""
	}
	if len(msgs) == 1 && msgs[0].Role == "user" {
		return msgs[0].Content
	}
	var sb strings.Builder
	sb.WriteString("# Prior turns\n\n")
	for _, m := range msgs[:len(msgs)-1] {
		sb.WriteString("## ")
		sb.WriteString(strings.ToUpper(m.Role))
		sb.WriteString("\n\n")
		sb.WriteString(m.Content)
		sb.WriteString("\n\n")
	}
	last := msgs[len(msgs)-1]
	sb.WriteString("# Current turn\n\n")
	if last.Role == "user" {
		sb.WriteString(last.Content)
	} else {
		// Unusual but possible — last message is assistant; we still respond.
		sb.WriteString("(continue)\n\n")
		sb.WriteString(last.Content)
	}
	return sb.String()
}
