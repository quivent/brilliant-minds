use regex::Regex;
use rusqlite::{Connection, Row};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashSet;
use std::env;
use std::io::{self, Read};
use std::path::PathBuf;

// Thresholds
const MULTI_AGENT_THRESHOLD: f64 = 0.3;
const STRONG_MATCH_THRESHOLD: f64 = 0.4;
const MAX_AGENTS: usize = 3;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Agent {
    id: String,
    name: String,
    role: String,
    avatar: String,
    stage: String,
    description: String,
    purpose: Vec<String>,
    capabilities: Vec<String>,
    specs: Value,
    actions: Vec<String>,
    priority: i32,
}

#[derive(Debug, Deserialize)]
struct HookInput {
    #[serde(default)]
    tool_name: Option<String>,
    #[serde(default)]
    tool_input: Option<Value>,
    #[serde(default)]
    prompt: Option<String>,
}

fn get_collaboration_patterns() -> Vec<(Regex, Vec<&'static str>)> {
    vec![
        (Regex::new(r"design\s+(?:and\s+)?implement").unwrap(), vec!["designer", "developer", "ui_developer"]),
        (Regex::new(r"implement\s+(?:and\s+)?design").unwrap(), vec!["developer", "designer", "ui_developer"]),
        (Regex::new(r"test\s+(?:and\s+)?fix|fix\s+(?:and\s+)?test").unwrap(), vec!["testrunner", "debugger", "developer"]),
        (Regex::new(r"database\s+(?:schema|design|architect)").unwrap(), vec!["architect", "developer", "topologist"]),
        (Regex::new(r"ui\s+component|interface\s+design").unwrap(), vec!["ui_developer", "designer"]),
        (Regex::new(r"review\s+(?:and\s+)?refactor").unwrap(), vec!["codereviewer", "developer"]),
        (Regex::new(r"code\s+review").unwrap(), vec!["codereviewer", "developer"]),
        (Regex::new(r"write\s+tests?|unit\s+tests?|test\s+coverage").unwrap(), vec!["testrunner", "developer"]),
        (Regex::new(r"debug(?:ging)?|fix\s+(?:bug|error|issue)").unwrap(), vec!["debugger", "developer"]),
        (Regex::new(r"styling|css|visual\s+design").unwrap(), vec!["ui_developer", "designer"]),
        (Regex::new(r"api\s+(?:design|implement)").unwrap(), vec!["architect", "developer"]),
        (Regex::new(r"performance\s+(?:tuning|optimization)").unwrap(), vec!["profiler", "developer", "benchmarker"]),
    ]
}

fn get_stop_words() -> HashSet<&'static str> {
    [
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "this", "that", "these", "those", "i", "you", "he", "she", "it",
        "we", "they", "what", "which", "who", "when", "where", "why", "how",
        "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "just", "also", "now", "here", "there",
        "please", "help", "me", "my", "your", "want", "use", "using",
        "make", "create", "build", "implement", "write", "add", "get",
        "task", "agent", "subagent", "new", "file", "code",
    ].into_iter().collect()
}

fn extract_keywords(text: &str) -> HashSet<String> {
    let stop_words = get_stop_words();
    let word_re = Regex::new(r"\b[a-zA-Z]{3,}\b").unwrap();

    word_re.find_iter(&text.to_lowercase())
        .map(|m| m.as_str().to_string())
        .filter(|w| !stop_words.contains(w.as_str()))
        .collect()
}

fn detect_collaboration_pattern(prompt: &str) -> Option<Vec<&'static str>> {
    let prompt_lower = prompt.to_lowercase();
    for (pattern, agent_ids) in get_collaboration_patterns() {
        if pattern.is_match(&prompt_lower) {
            return Some(agent_ids);
        }
    }
    None
}

fn score_agent(agent: &Agent, keywords: &HashSet<String>) -> (f64, String) {
    if keywords.is_empty() {
        return (0.0, String::new());
    }

    let mut score = 0.0;
    let mut reasons = Vec::new();
    let kw_count = keywords.len() as f64;

    // Priority multiplier: priority 100 = 2x, priority 50 = 1x, priority 25 = 0.5x
    let priority_mult = agent.priority as f64 / 50.0;

    // Purpose (high weight)
    let purpose_text = agent.purpose.join(" ");
    let purpose_kw = extract_keywords(&purpose_text);
    let purpose_overlap: HashSet<_> = keywords.intersection(&purpose_kw).collect();
    if !purpose_overlap.is_empty() {
        score += (purpose_overlap.len() as f64 / kw_count) * 0.4;
        reasons.push(format!("purpose:{}", purpose_overlap.iter().take(3).map(|s| s.as_str()).collect::<Vec<_>>().join(",")));
    }

    // Capabilities (high weight)
    let caps_text = agent.capabilities.join(" ");
    let caps_kw = extract_keywords(&caps_text);
    let caps_overlap: HashSet<_> = keywords.intersection(&caps_kw).collect();
    if !caps_overlap.is_empty() {
        score += (caps_overlap.len() as f64 / kw_count) * 0.35;
        reasons.push(format!("capabilities:{}", caps_overlap.iter().take(3).map(|s| s.as_str()).collect::<Vec<_>>().join(",")));
    }

    // Description (medium weight)
    let desc_kw = extract_keywords(&agent.description);
    let desc_overlap: HashSet<_> = keywords.intersection(&desc_kw).collect();
    if !desc_overlap.is_empty() {
        score += (desc_overlap.len() as f64 / kw_count) * 0.15;
        reasons.push(format!("description:{}", desc_overlap.iter().take(3).map(|s| s.as_str()).collect::<Vec<_>>().join(",")));
    }

    // Role (low weight)
    let role_kw = extract_keywords(&agent.role);
    let role_overlap: HashSet<_> = keywords.intersection(&role_kw).collect();
    if !role_overlap.is_empty() {
        score += (role_overlap.len() as f64 / kw_count) * 0.1;
        reasons.push(format!("role:{}", role_overlap.iter().take(2).map(|s| s.as_str()).collect::<Vec<_>>().join(",")));
    }

    // ID/name bonus
    let id_lower = agent.id.to_lowercase();
    if keywords.contains(&id_lower) || keywords.iter().any(|kw| id_lower.contains(kw)) {
        score += 0.15;
        reasons.push("id_match".to_string());
    }

    let name_lower = agent.name.to_lowercase();
    if keywords.iter().any(|kw| name_lower.contains(kw)) {
        score += 0.1;
        reasons.push("name_match".to_string());
    }

    // Apply priority multiplier to final score
    let final_score = score * priority_mult;
    if agent.priority != 50 {
        reasons.push(format!("priority:{}", agent.priority));
    }

    (final_score, reasons.join("; "))
}

fn row_to_agent(row: &Row) -> rusqlite::Result<Agent> {
    let purpose_str: String = row.get(6)?;
    let caps_str: String = row.get(7)?;
    let specs_str: String = row.get(8)?;
    let actions_str: String = row.get(9)?;
    let priority: i32 = row.get(10).unwrap_or(50);

    let purpose: Vec<String> = serde_json::from_str(&purpose_str).unwrap_or_default();
    let capabilities: Vec<String> = serde_json::from_str(&caps_str).unwrap_or_default();
    let specs: Value = serde_json::from_str(&specs_str).unwrap_or(json!({}));
    let actions: Vec<String> = serde_json::from_str(&actions_str).unwrap_or_default();

    Ok(Agent {
        id: row.get(0)?,
        name: row.get(1)?,
        role: row.get(2)?,
        avatar: row.get(3)?,
        stage: row.get(4)?,
        description: row.get(5)?,
        purpose,
        capabilities,
        specs,
        actions,
        priority,
    })
}

fn build_precontext(agent: &Agent, method: &str) -> String {
    let mut parts = Vec::new();

    parts.push(format!("## {} Agent Precontext: {}", agent.avatar, agent.name));
    parts.push(format!("\n**Role**: {}", agent.role));
    parts.push(format!("**Stage**: {}", agent.stage));
    parts.push(format!("**Match Method**: {}", method));
    parts.push(format!("\n**Description**: {}", agent.description));

    if !agent.purpose.is_empty() {
        parts.push("\n**Purpose**:".to_string());
        for p in &agent.purpose {
            parts.push(format!("- {}", p));
        }
    }

    if !agent.capabilities.is_empty() {
        parts.push("\n**Capabilities**:".to_string());
        for cap in &agent.capabilities {
            parts.push(format!("- {}", cap));
        }
    }

    if let Some(specs_obj) = agent.specs.as_object() {
        let filtered: Vec<_> = specs_obj.iter()
            .filter(|(k, _)| *k != "performance")
            .collect();

        if !filtered.is_empty() {
            parts.push("\n**Specifications**:".to_string());
            for (key, value) in &filtered {
                parts.push(format!("- {}: {}", key, value));
            }
        }

        if let Some(perf) = specs_obj.get("performance").and_then(|p| p.as_object()) {
            parts.push("\n**Performance Scores**:".to_string());
            for (metric, score) in perf {
                parts.push(format!("- {}: {}/100", metric, score));
            }
        }
    }

    if !agent.actions.is_empty() {
        parts.push("\n**Available Actions**:".to_string());
        for action in &agent.actions {
            parts.push(format!("- `{}`", action));
        }
    }

    parts.join("\n")
}

fn build_multi_precontext(agents: &[(Agent, String)]) -> String {
    let mut parts = Vec::new();

    let names: Vec<_> = agents.iter().map(|(a, _)| a.name.as_str()).collect();
    parts.push(format!("# Multi-Agent Dispatch: {}", names.join(" + ")));
    parts.push("\nThis task requires collaboration between multiple specialized agents.".to_string());
    parts.push("\n---\n".to_string());

    for (agent, method) in agents {
        parts.push(build_precontext(agent, method));
        parts.push("\n---\n".to_string());
    }

    parts.push("## Project Context: Mercenary".to_string());
    parts.push("\nYou are operating within the **Mercenary** system - a professional contractor's strategic command center.".to_string());
    parts.push("\n**Terminology**: Use 'contracts' (not jobs), 'targets' (not companies), 'capabilities' (not skills), 'pipeline' (not applications).".to_string());
    parts.push("\n**Principle**: Local-first, no fake data, honest metrics only.".to_string());

    parts.join("\n")
}

fn add_project_context(precontext: &mut String) {
    precontext.push_str("\n\n---\n\n## Project Context: Mercenary");
    precontext.push_str("\n\nYou are operating within the **Mercenary** system - a professional contractor's strategic command center.");
    precontext.push_str("\n\n**Terminology**: Use 'contracts' (not jobs), 'targets' (not companies), 'capabilities' (not skills), 'pipeline' (not applications).");
    precontext.push_str("\n\n**Principle**: Local-first, no fake data, honest metrics only.");
}

fn get_db_path() -> Option<PathBuf> {
    // Try AGENT_DATABASE_PATH first
    if let Ok(path) = env::var("AGENT_DATABASE_PATH") {
        let expanded = if path.starts_with("~/") {
            if let Ok(home) = env::var("HOME") {
                path.replacen("~", &home, 1)
            } else {
                path
            }
        } else {
            path
        };
        return Some(PathBuf::from(expanded));
    }

    // Try BRILLIANT_MINDS_ROOT
    if let Ok(root) = env::var("BRILLIANT_MINDS_ROOT") {
        return Some(PathBuf::from(format!("{}/db/agents.db", root)));
    }

    // Default location (legacy fallback)
    if let Ok(home) = env::var("HOME") {
        return Some(PathBuf::from(format!("{}/.claude/db/agents.db", home)));
    }

    None
}

fn main() {
    // Read stdin
    let mut input = String::new();
    if io::stdin().read_to_string(&mut input).is_err() {
        return;
    }

    let hook_input: HookInput = match serde_json::from_str(&input) {
        Ok(v) => v,
        Err(_) => return,
    };

    // Determine if this is PreToolUse or UserPromptSubmit
    let is_pre_tool_use = hook_input.tool_name.is_some();

    // For PreToolUse, only handle Task tool
    if is_pre_tool_use {
        if hook_input.tool_name.as_deref() != Some("Task") {
            return;
        }
    }

    // Extract prompt based on hook type
    let original_prompt = if is_pre_tool_use {
        hook_input.tool_input.as_ref()
            .and_then(|v| v.get("prompt"))
            .and_then(|v| v.as_str())
            .unwrap_or("")
    } else {
        hook_input.prompt.as_deref().unwrap_or("")
    };

    let subagent_type = hook_input.tool_input.as_ref()
        .and_then(|v| v.get("subagent_type"))
        .and_then(|v| v.as_str())
        .unwrap_or("");

    // Open SQLite database
    let db_path = match get_db_path() {
        Some(p) => p,
        None => return,
    };

    let conn = match Connection::open(&db_path) {
        Ok(c) => c,
        Err(_) => return,
    };

    // Find matching agents
    let mut matched_agents: Vec<(Agent, String)> = Vec::new();

    // 1. Check collaboration patterns
    if let Some(collab_ids) = detect_collaboration_pattern(original_prompt) {
        for agent_id in &collab_ids {
            let result = conn.query_row(
                "SELECT id, name, role, avatar, stage, description, purpose, capabilities, specs, actions, priority FROM agents WHERE id = ?1 AND archived_at IS NULL",
                [agent_id],
                |row| row_to_agent(row)
            );
            if let Ok(agent) = result {
                matched_agents.push((agent, format!("collaboration:{}", collab_ids.join(","))));
            }
        }
        if !matched_agents.is_empty() {
            output_result(is_pre_tool_use, &hook_input.tool_input, &matched_agents);
            return;
        }
    }

    // 2. Semantic matching
    let keywords = extract_keywords(original_prompt);
    if !keywords.is_empty() {
        let mut stmt = match conn.prepare(
            "SELECT id, name, role, avatar, stage, description, purpose, capabilities, specs, actions, priority FROM agents WHERE archived_at IS NULL ORDER BY name"
        ) {
            Ok(s) => s,
            Err(_) => return,
        };

        let agents: Vec<Agent> = stmt.query_map([], |row| row_to_agent(row))
            .ok()
            .map(|iter| iter.filter_map(|r| r.ok()).collect())
            .unwrap_or_default();

        let mut scored: Vec<(Agent, f64, String)> = agents.into_iter()
            .map(|agent| {
                let (score, reason) = score_agent(&agent, &keywords);
                (agent, score, reason)
            })
            .filter(|(_, score, _)| *score >= MULTI_AGENT_THRESHOLD)
            .collect();

        scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        if !scored.is_empty() {
            let top_score = scored[0].1;

            if top_score >= STRONG_MATCH_THRESHOLD {
                for (agent, score, reason) in scored.into_iter().take(MAX_AGENTS) {
                    if score >= top_score - 0.15 {
                        matched_agents.push((agent, format!("semantic:{:.2}:{}", score, reason)));
                    }
                }
            } else {
                let (agent, score, reason) = scored.remove(0);
                matched_agents.push((agent, format!("weak-semantic:{:.2}:{}", score, reason)));
            }

            if !matched_agents.is_empty() {
                output_result(is_pre_tool_use, &hook_input.tool_input, &matched_agents);
                return;
            }
        }
    }

    // 3. Fallback: exact ID match (only for PreToolUse with subagent_type)
    if is_pre_tool_use && !subagent_type.is_empty() {
        let result = conn.query_row(
            "SELECT id, name, role, avatar, stage, description, purpose, capabilities, specs, actions, priority FROM agents WHERE id = ?1 AND archived_at IS NULL",
            [&subagent_type.to_lowercase()],
            |row| row_to_agent(row)
        );
        if let Ok(agent) = result {
            matched_agents.push((agent, "fallback_exact_id".to_string()));
            output_result(is_pre_tool_use, &hook_input.tool_input, &matched_agents);
        }
    }
}

fn output_result(is_pre_tool_use: bool, original_input: &Option<Value>, agents: &[(Agent, String)]) {
    let precontext = if agents.len() == 1 {
        let (agent, method) = &agents[0];
        let mut ctx = build_precontext(agent, method);
        add_project_context(&mut ctx);
        ctx
    } else {
        build_multi_precontext(agents)
    };

    let agent_info = if agents.len() == 1 {
        let (agent, method) = &agents[0];
        format!("{} ({}) via {}", agent.name, agent.role, method)
    } else {
        let names: Vec<_> = agents.iter().map(|(a, _)| a.name.as_str()).collect();
        format!("{} via multi-dispatch", names.join(" + "))
    };

    let output = if is_pre_tool_use {
        let original_prompt = original_input.as_ref()
            .and_then(|v| v.get("prompt"))
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let enhanced_prompt = format!("{}\n\n---\n\n## Original Task\n\n{}", precontext, original_prompt);

        let mut updated_input = original_input.clone().unwrap_or(json!({}));
        if let Some(obj) = updated_input.as_object_mut() {
            obj.insert("prompt".to_string(), json!(enhanced_prompt));
        }

        json!({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": updated_input,
                "additionalContext": format!("Mercenary agent matched: {}", agent_info)
            }
        })
    } else {
        json!({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": format!("=== AGENT PRECONTEXT: {} ===\n\n{}", agent_info, precontext)
            }
        })
    };

    println!("{}", serde_json::to_string(&output).unwrap());
}
