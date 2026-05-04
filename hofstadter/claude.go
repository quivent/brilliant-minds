package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

const (
	apiURL           = "https://api.anthropic.com/v1/messages"
	apiVersion       = "2023-06-01"
	defaultModel     = "claude-sonnet-4-6"
	defaultMaxTokens = 1024
)

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

// ClaudeClient is a minimal stdlib HTTP client for the Anthropic Messages API.
// The system prompt is sent with cache_control:ephemeral so successive turns
// for the same mind reuse the cached identity (the IDENTITY.md is large and
// stable, so this matters for kloops with many turns).
type ClaudeClient struct {
	apiKey    string
	model     string
	maxTokens int
	httpc     *http.Client

	// cumulative usage across this client's lifetime
	totalUsage apiUsage
}

func NewClaudeClient(model string, maxTokens int) (*ClaudeClient, error) {
	key := os.Getenv("ANTHROPIC_API_KEY")
	if key == "" {
		return nil, errors.New("ANTHROPIC_API_KEY not set (or use --dry-run)")
	}
	if model == "" {
		model = defaultModel
	}
	if maxTokens <= 0 {
		maxTokens = defaultMaxTokens
	}
	return &ClaudeClient{
		apiKey:    key,
		model:     model,
		maxTokens: maxTokens,
		httpc:     &http.Client{Timeout: 5 * time.Minute},
	}, nil
}

// Call sends one Messages turn. The system prompt is cached.
func (c *ClaudeClient) Call(system string, msgs []apiMessage) (string, error) {
	req := apiRequest{
		Model:     c.model,
		MaxTokens: c.maxTokens,
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
	httpReq.Header.Set("x-api-key", c.apiKey)
	httpReq.Header.Set("anthropic-version", apiVersion)

	resp, err := c.httpc.Do(httpReq)
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

	c.totalUsage.InputTokens += ar.Usage.InputTokens
	c.totalUsage.OutputTokens += ar.Usage.OutputTokens
	c.totalUsage.CacheCreationInputTokens += ar.Usage.CacheCreationInputTokens
	c.totalUsage.CacheReadInputTokens += ar.Usage.CacheReadInputTokens

	var out bytes.Buffer
	for _, b := range ar.Content {
		if b.Type == "text" {
			out.WriteString(b.Text)
		}
	}
	return out.String(), nil
}

// PrintUsage writes a one-line usage summary to stderr.
func (c *ClaudeClient) PrintUsage() {
	if c == nil {
		return
	}
	u := c.totalUsage
	fmt.Fprintf(os.Stderr,
		"\n[usage] in=%d out=%d cache_create=%d cache_read=%d\n",
		u.InputTokens, u.OutputTokens, u.CacheCreationInputTokens, u.CacheReadInputTokens,
	)
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}
