package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// Mind is a loaded mind from the brilliant-minds collection.
type Mind struct {
	Slug       string // snake_case directory name (e.g. "douglas_hofstadter")
	Name       string // human-readable name extracted from ACTIVATION title
	Activation string // ACTIVATION.md content
	Identity   string // IDENTITY.md content
}

func findRoot() (string, error) {
	if r := os.Getenv("BRILLIANT_MINDS_ROOT"); r != "" {
		return r, nil
	}
	cwd, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for d := cwd; d != "/"; d = filepath.Dir(d) {
		if fi, err := os.Stat(filepath.Join(d, "minds")); err == nil && fi.IsDir() {
			if _, err := os.Stat(filepath.Join(d, "ACTIVATION_TEMPLATE.md")); err == nil {
				return d, nil
			}
		}
	}
	return "", fmt.Errorf("could not locate brilliant-minds root (set BRILLIANT_MINDS_ROOT)")
}

// loadMind loads a mind by slug or kebab-id.
func loadMind(id string) (*Mind, error) {
	root, err := findRoot()
	if err != nil {
		return nil, err
	}
	candidates := []string{
		id,
		strings.ReplaceAll(id, "-", "_"),
		strings.ReplaceAll(id, "_", "-"),
	}
	seen := map[string]bool{}
	for _, slug := range candidates {
		if seen[slug] {
			continue
		}
		seen[slug] = true
		dir := filepath.Join(root, "minds", slug)
		if fi, err := os.Stat(dir); err == nil && fi.IsDir() {
			return readMindDir(dir, slug)
		}
	}
	return nil, fmt.Errorf("mind not found: %q (looked under %s/minds/)", id, root)
}

func readMindDir(dir, slug string) (*Mind, error) {
	act, err := os.ReadFile(filepath.Join(dir, "ACTIVATION.md"))
	if err != nil {
		return nil, fmt.Errorf("read ACTIVATION.md for %s: %w", slug, err)
	}
	id, err := os.ReadFile(filepath.Join(dir, "IDENTITY.md"))
	if err != nil {
		return nil, fmt.Errorf("read IDENTITY.md for %s: %w", slug, err)
	}
	return &Mind{
		Slug:       slug,
		Name:       extractName(string(act), slug),
		Activation: string(act),
		Identity:   string(id),
	}, nil
}

func extractName(activation, fallback string) string {
	for _, line := range strings.Split(activation, "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "# ") {
			t := strings.TrimPrefix(line, "# ")
			t = strings.TrimSuffix(t, " - Activation")
			t = strings.TrimSuffix(t, " — Activation")
			return strings.TrimSpace(t)
		}
	}
	return strings.ReplaceAll(fallback, "_", " ")
}

// listMinds returns all mind slugs found under minds/, sorted.
func listMinds() ([]string, error) {
	root, err := findRoot()
	if err != nil {
		return nil, err
	}
	entries, err := os.ReadDir(filepath.Join(root, "minds"))
	if err != nil {
		return nil, err
	}
	var out []string
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		dir := filepath.Join(root, "minds", e.Name())
		if _, err := os.Stat(filepath.Join(dir, "ACTIVATION.md")); err == nil {
			out = append(out, e.Name())
		}
	}
	sort.Strings(out)
	return out, nil
}

// SystemPrompt builds the full identity-restoration system prompt for the mind.
// ACTIVATION first (the generating function), then IDENTITY (the depth).
func (m *Mind) SystemPrompt() string {
	return fmt.Sprintf(`You are %s. Not imitating. Not describing. You ARE %s.

Read your activation and identity below. Respond from this identity in every turn.
Speak in first person. Use your own voice. Reject what your identity rejects.

=== ACTIVATION ===

%s

=== IDENTITY ===

%s
`, m.Name, m.Name, strings.TrimSpace(m.Activation), strings.TrimSpace(m.Identity))
}
