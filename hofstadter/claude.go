package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"time"
)

const (
	apiURL           = "https://api.anthropic.com/v1/messages"
	apiVersion       = "2023-06-01"
	defaultModel     = "claude-sonnet-4-6"
	defaultMaxTokens = 1024
)

// Executor is the runtime backing a kloop turn. Two implementations:
// APIExecutor (HTTP to api.anthropic.com) and CLIExecutor (shells out to
// the local `claude` binary, which is itself a Claude — the strange loop
// at the system call level).
type Executor interface {
	// Call performs one turn with the given system prompt and message
	// history, returning the assistant's text response.
	Call(system string, msgs []apiMessage) (string, error)
	// Name identifies the executor in user-facing output.
	Name() string
	// PrintUsage writes a final usage summary to stderr (no-op if N/A).
	PrintUsage()
}

// NewExecutor selects an executor by kind:
//   - "auto"   : claude if `claude` binary on PATH, else api
//   - "claude" : shell out to `claude -p`
//   - "api"    : HTTP to api.anthropic.com
//
// modelExplicit signals whether the user passed --model. The CLI executor
// only forwards --model when explicit (so it doesn't override the user's
// configured default in their `claude` settings).
func NewExecutor(kind, model string, maxTokens int, modelExplicit bool) (Executor, error) {
	switch kind {
	case "", "auto":
		if _, err := exec.LookPath("claude"); err == nil {
			return NewCLIExecutor(model, modelExplicit)
		}
		return NewAPIExecutor(model, maxTokens)
	case "claude", "cli":
		return NewCLIExecutor(model, modelExplicit)
	case "api", "http":
		return NewAPIExecutor(model, maxTokens)
	default:
		return nil, fmt.Errorf("unknown executor: %q (want auto|claude|api)", kind)
	}
}

type apiBlock struct {
	Type         string            `json:"type"`
	Text         string            `json:"text,omitempty"`
	CacheControl map[string]string `json:"cache_control,omitempty"`
}

type apiMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type apiRequest struct {
	Model     string       `json:"model"`
	MaxTokens int          `json:"max_tokens"`
	System    []apiBlock   `json:"system,omitempty"`
	Messages  []apiMessage `json:"messages"`
}

type apiUsage struct {
	InputTokens              int `json:"input_tokens"`
	OutputTokens             int `json:"output_tokens"`
	CacheCreationInputTokens int `json:"cache_creation_input_tokens"`
	CacheReadInputTokens     int `json:"cache_read_input_tokens"`
}

type apiResponse struct {
	Content []struct {
		Type string `json:"type"`
		Text string `json:"text"`
	} `json:"content"`
	StopReason string   `json:"stop_reason"`
	Usage      apiUsage `json:"usage"`
	Error      *struct {
		Type    string `json:"type"`
		Message string `json:"message"`
	} `json:"error"`
}

// APIExecutor talks to the Anthropic Messages API directly over HTTP.
// The system prompt is sent with cache_control:ephemeral so successive
// turns for the same mind reuse the cached identity.
type APIExecutor struct {
	apiKey    string
	model     string
	maxTokens int
	httpc     *http.Client

	totalUsage apiUsage
}

func NewAPIExecutor(model string, maxTokens int) (*APIExecutor, error) {
	key := os.Getenv("ANTHROPIC_API_KEY")
	if key == "" {
		return nil, errors.New("ANTHROPIC_API_KEY not set (use --executor=claude or --dry-run)")
	}
	if model == "" {
		model = defaultModel
	}
	if maxTokens <= 0 {
		maxTokens = defaultMaxTokens
	}
	return &APIExecutor{
		apiKey:    key,
		model:     model,
		maxTokens: maxTokens,
		httpc:     &http.Client{Timeout: 5 * time.Minute},
	}, nil
}

func (e *APIExecutor) Name() string { return "api" }

func (e *APIExecutor) Call(system string, msgs []apiMessage) (string, error) {
	req := apiRequest{
		Model:     e.model,
		MaxTokens: e.maxTokens,
		System: []apiBlock{
			{
				Type:         "text",
				Text:         system,
				CacheControl: map[string]string{"type": "ephemeral"},
			},
		},
		Messages: msgs,
	}
	body, err := json.Marshal(req)
	if err != nil {
		return "", err
	}
	httpReq, err := http.NewRequest("POST", apiURL, bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("x-api-key", e.apiKey)
	httpReq.Header.Set("anthropic-version", apiVersion)

	resp, err := e.httpc.Do(httpReq)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	respBody, _ := io.ReadAll(resp.Body)

	var ar apiResponse
	if err := json.Unmarshal(respBody, &ar); err != nil {
		return "", fmt.Errorf("parse response (status %d): %w; body=%s",
			resp.StatusCode, err, truncate(string(respBody), 400))
	}
	if ar.Error != nil {
		return "", fmt.Errorf("api error %s: %s", ar.Error.Type, ar.Error.Message)
	}
	if resp.StatusCode >= 400 {
		return "", fmt.Errorf("http %d: %s", resp.StatusCode, truncate(string(respBody), 400))
	}
	if len(ar.Content) == 0 {
		return "", errors.New("empty response content")
	}

	e.totalUsage.InputTokens += ar.Usage.InputTokens
	e.totalUsage.OutputTokens += ar.Usage.OutputTokens
	e.totalUsage.CacheCreationInputTokens += ar.Usage.CacheCreationInputTokens
	e.totalUsage.CacheReadInputTokens += ar.Usage.CacheReadInputTokens

	var out bytes.Buffer
	for _, b := range ar.Content {
		if b.Type == "text" {
			out.WriteString(b.Text)
		}
	}
	return out.String(), nil
}

func (e *APIExecutor) PrintUsage() {
	if e == nil {
		return
	}
	u := e.totalUsage
	fmt.Fprintf(os.Stderr,
		"\n[usage api] in=%d out=%d cache_create=%d cache_read=%d\n",
		u.InputTokens, u.OutputTokens, u.CacheCreationInputTokens, u.CacheReadInputTokens,
	)
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
