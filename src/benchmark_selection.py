"""
Benchmark Selection Engine

Enables restored brilliant minds to select which questions
should be used for general and specific benchmarking.

This module provides the infrastructure for:
1. Having restored minds select relevant benchmark questions
2. Prioritizing questions based on the mind's values and standards
3. Aggregating selections from multiple minds for consensus
4. Analyzing diversity across question categories and perspectives

Author: Brilliant Minds Benchmarking System
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Tuple, Callable
from enum import Enum
from collections import defaultdict, Counter
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path


class SelectionMode(Enum):
    """Mode of benchmark selection."""
    GENERAL = "general"  # Universal benchmarks applicable across repositories
    SPECIFIC = "specific"  # Repository-specific benchmarks


class QuestionPriority(Enum):
    """Priority level for selected questions."""
    CRITICAL = "critical"  # Must answer - fundamental to evaluation
    IMPORTANT = "important"  # Should answer - significant value
    INSIGHTFUL = "insightful"  # Nice to answer - adds depth

    @property
    def weight(self) -> float:
        """Return numerical weight for the priority level."""
        weights = {
            QuestionPriority.CRITICAL: 3.0,
            QuestionPriority.IMPORTANT: 2.0,
            QuestionPriority.INSIGHTFUL: 1.0
        }
        return weights[self]


class QuestionCategory(Enum):
    """Categories for question classification."""
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DESIGN_PATTERNS = "design_patterns"
    TESTING = "testing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    CODE_QUALITY = "code_quality"
    DEPENDENCIES = "dependencies"
    DEPLOYMENT = "deployment"
    MAINTAINABILITY = "maintainability"
    SCALABILITY = "scalability"
    ERROR_HANDLING = "error_handling"
    API_DESIGN = "api_design"
    DATA_MODELING = "data_modeling"
    OTHER = "other"


@dataclass
class Question:
    """Represents a benchmark question."""
    id: str
    text: str
    category: QuestionCategory
    context: Optional[str] = None
    expected_depth: str = "moderate"  # shallow, moderate, deep
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Question):
            return self.id == other.id
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category.value,
            "context": self.context,
            "expected_depth": self.expected_depth,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            text=data["text"],
            category=QuestionCategory(data["category"]),
            context=data.get("context"),
            expected_depth=data.get("expected_depth", "moderate"),
            metadata=data.get("metadata", {})
        )


@dataclass
class QuestionSet:
    """A collection of questions for benchmarking."""
    name: str
    questions: List[Question]
    source: str  # Where these questions came from
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def by_category(self) -> Dict[QuestionCategory, List[Question]]:
        """Group questions by category."""
        grouped: Dict[QuestionCategory, List[Question]] = defaultdict(list)
        for q in self.questions:
            grouped[q.category].append(q)
        return dict(grouped)

    def filter_by_category(self, category: QuestionCategory) -> List[Question]:
        """Get questions for a specific category."""
        return [q for q in self.questions if q.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "questions": [q.to_dict() for q in self.questions],
            "source": self.source,
            "created_at": self.created_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionSet":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            questions=[Question.from_dict(q) for q in data["questions"]],
            source=data["source"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )


@dataclass
class SelectedQuestion:
    """A question selected by a mind for benchmarking."""
    question: Question
    priority: QuestionPriority
    selection_rationale: str
    expected_insight: str
    relevance_score: float = 0.0  # 0.0 to 1.0
    mind_specific_context: Optional[str] = None  # Why this mind cares

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "question": self.question.to_dict(),
            "priority": self.priority.value,
            "selection_rationale": self.selection_rationale,
            "expected_insight": self.expected_insight,
            "relevance_score": self.relevance_score,
            "mind_specific_context": self.mind_specific_context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelectedQuestion":
        """Create from dictionary representation."""
        return cls(
            question=Question.from_dict(data["question"]),
            priority=QuestionPriority(data["priority"]),
            selection_rationale=data["selection_rationale"],
            expected_insight=data["expected_insight"],
            relevance_score=data.get("relevance_score", 0.0),
            mind_specific_context=data.get("mind_specific_context")
        )


@dataclass
class RestoredMind:
    """Represents a restored brilliant mind for benchmarking."""
    name: str
    identity_document: str
    core_values: List[str]
    expertise_domains: List[str]
    technical_philosophy: str
    communication_style: str
    knowledge_benchmarks: Dict[str, List[str]]  # deep, moderate, defer

    @classmethod
    def from_identity_file(cls, path: str) -> "RestoredMind":
        """Load a restored mind from an identity markdown file."""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract name from first heading
        name_match = re.search(r'^#\s*Identity:\s*(.+)$', content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else "Unknown"

        # Extract core values from Technical Philosophy section
        philosophy_match = re.search(
            r'###\s*Technical Philosophy\s*\n(.*?)(?=\n##|\n###|\Z)',
            content,
            re.DOTALL
        )
        philosophy = philosophy_match.group(1).strip() if philosophy_match else ""

        # Extract values as bullet points from philosophy
        values = re.findall(r'\*\*([^*]+)\*\*', philosophy)

        # If no values found in Technical Philosophy, try extracting from
        # bullet points with bold markers anywhere in the document
        if not values:
            # Try Core Identity Statement for key concepts
            core_match = re.search(
                r'##\s*Core Identity Statement\s*\n(.*?)(?=\n##|\Z)',
                content,
                re.DOTALL
            )
            if core_match:
                core_text = core_match.group(1)
                # Extract key phrases in bold
                values = re.findall(r'\*\*([^*]+)\*\*', core_text)

        # Also try extracting from Debate Positions section
        if not values or len(values) < 3:
            debate_match = re.search(
                r'###\s*Debate Positions\s*\n(.*?)(?=\n##|\n###|\Z)',
                content,
                re.DOTALL
            )
            if debate_match:
                debate_values = re.findall(r'\*\*([^*]+)\*\*', debate_match.group(1))
                values.extend(debate_values[:5])  # Add up to 5 debate positions

        # Extract expertise domains from Primary Domains section
        domains_match = re.search(
            r'###\s*Primary Domains\s*\n(.*?)(?=\n##|\n###|\Z)',
            content,
            re.DOTALL
        )
        domains_text = domains_match.group(1) if domains_match else ""
        domains = re.findall(r'\d+\.\s*\*\*([^*]+)\*\*', domains_text)

        # Extract communication style
        comm_match = re.search(
            r'###\s*Voice Characteristics\s*\n(.*?)(?=\n##|\n###|\Z)',
            content,
            re.DOTALL
        )
        comm_style = comm_match.group(1).strip() if comm_match else ""

        # Extract knowledge benchmarks
        deep_match = re.search(
            r'###\s*Would Know Deeply\s*\n(.*?)(?=\n##|\n###|\Z)',
            content,
            re.DOTALL
        )
        deep_items = re.findall(r'-\s*(.+)', deep_match.group(1)) if deep_match else []

        moderate_match = re.search(
            r'###\s*Would Know Moderately\s*\n(.*?)(?=\n##|\n###|\Z)',
            content,
            re.DOTALL
        )
        moderate_items = re.findall(r'-\s*(.+)', moderate_match.group(1)) if moderate_match else []

        defer_match = re.search(
            r'###\s*Would Defer On\s*\n(.*?)(?=\n##|\n###|\Z)',
            content,
            re.DOTALL
        )
        defer_items = re.findall(r'-\s*(.+)', defer_match.group(1)) if defer_match else []

        return cls(
            name=name,
            identity_document=content,
            core_values=values,
            expertise_domains=domains,
            technical_philosophy=philosophy,
            communication_style=comm_style,
            knowledge_benchmarks={
                "deep": deep_items,
                "moderate": moderate_items,
                "defer": defer_items
            }
        )


@dataclass
class BenchmarkSet:
    """A complete set of selected benchmark questions."""
    mind_name: str
    mode: SelectionMode
    selected_questions: List[SelectedQuestion]
    target_description: Optional[str] = None  # For specific mode - describes the repo
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def critical_questions(self) -> List[SelectedQuestion]:
        """Get all critical priority questions."""
        return [sq for sq in self.selected_questions
                if sq.priority == QuestionPriority.CRITICAL]

    def important_questions(self) -> List[SelectedQuestion]:
        """Get all important priority questions."""
        return [sq for sq in self.selected_questions
                if sq.priority == QuestionPriority.IMPORTANT]

    def insightful_questions(self) -> List[SelectedQuestion]:
        """Get all insightful priority questions."""
        return [sq for sq in self.selected_questions
                if sq.priority == QuestionPriority.INSIGHTFUL]

    def by_priority(self) -> Dict[QuestionPriority, List[SelectedQuestion]]:
        """Group selected questions by priority."""
        grouped: Dict[QuestionPriority, List[SelectedQuestion]] = defaultdict(list)
        for sq in self.selected_questions:
            grouped[sq.priority].append(sq)
        return dict(grouped)

    def by_category(self) -> Dict[QuestionCategory, List[SelectedQuestion]]:
        """Group selected questions by category."""
        grouped: Dict[QuestionCategory, List[SelectedQuestion]] = defaultdict(list)
        for sq in self.selected_questions:
            grouped[sq.question.category].append(sq)
        return dict(grouped)

    def total_weight(self) -> float:
        """Calculate total weight of all selected questions."""
        return sum(sq.priority.weight * (1 + sq.relevance_score)
                   for sq in self.selected_questions)

    def average_relevance(self) -> float:
        """Calculate average relevance score."""
        if not self.selected_questions:
            return 0.0
        return sum(sq.relevance_score for sq in self.selected_questions) / len(self.selected_questions)

    def coverage_report(self) -> Dict[str, Any]:
        """Generate a coverage report for this benchmark set."""
        by_category = self.by_category()
        by_priority = self.by_priority()

        return {
            "total_questions": len(self.selected_questions),
            "total_weight": self.total_weight(),
            "average_relevance": self.average_relevance(),
            "categories_covered": [cat.value for cat in by_category.keys()],
            "category_distribution": {
                cat.value: len(questions)
                for cat, questions in by_category.items()
            },
            "priority_distribution": {
                pri.value: len(questions)
                for pri, questions in by_priority.items()
            },
            "critical_count": len(self.critical_questions()),
            "important_count": len(self.important_questions()),
            "insightful_count": len(self.insightful_questions())
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "mind_name": self.mind_name,
            "mode": self.mode.value,
            "selected_questions": [sq.to_dict() for sq in self.selected_questions],
            "target_description": self.target_description,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "coverage_report": self.coverage_report()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkSet":
        """Create from dictionary representation."""
        return cls(
            mind_name=data["mind_name"],
            mode=SelectionMode(data["mode"]),
            selected_questions=[
                SelectedQuestion.from_dict(sq)
                for sq in data["selected_questions"]
            ],
            target_description=data.get("target_description"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {})
        )

    def to_json(self, path: str) -> None:
        """Export benchmark set to JSON file."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: str) -> "BenchmarkSet":
        """Load benchmark set from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class BenchmarkSelector:
    """Helps restored minds select benchmark questions."""

    def __init__(self, restored_mind: RestoredMind, model_client: Any = None):
        """
        Initialize the benchmark selector.

        Args:
            restored_mind: The restored mind that will select questions
            model_client: Optional LLM client for generating selections
        """
        self.mind = restored_mind
        self.model_client = model_client

    def _format_questions_for_prompt(self, questions: List[Question]) -> str:
        """Format questions as a numbered list for prompts."""
        lines = []
        for i, q in enumerate(questions, 1):
            lines.append(f"{i}. [ID: {q.id}] [{q.category.value}]")
            lines.append(f"   Question: {q.text}")
            if q.context:
                lines.append(f"   Context: {q.context}")
            lines.append(f"   Expected Depth: {q.expected_depth}")
            lines.append("")
        return "\n".join(lines)

    def _format_mind_context(self) -> str:
        """Format the mind's context for prompts."""
        values_text = "\n".join(f"- {v}" for v in self.mind.core_values[:5])
        domains_text = "\n".join(f"- {d}" for d in self.mind.expertise_domains[:5])
        deep_knowledge = "\n".join(f"- {k}" for k in self.mind.knowledge_benchmarks.get("deep", [])[:5])

        return f"""
## Your Identity: {self.mind.name}

### Core Values and Principles:
{values_text}

### Primary Expertise Domains:
{domains_text}

### Deep Technical Knowledge:
{deep_knowledge}

### Your Technical Philosophy:
{self.mind.technical_philosophy[:500]}...
"""

    def build_general_selection_prompt(
        self,
        questions: List[Question],
        target_count: int = 10
    ) -> str:
        """
        Build a prompt for selecting general benchmarks.

        Args:
            questions: List of available questions
            target_count: Target number of questions to select

        Returns:
            Formatted prompt string
        """
        mind_context = self._format_mind_context()
        questions_text = self._format_questions_for_prompt(questions)

        return f"""# Benchmark Question Selection Task

You are {self.mind.name}, selecting questions for a GENERAL benchmark that will be used to evaluate AI code assistants across many different repositories and contexts.

{mind_context}

## Task
From the following {len(questions)} questions, select exactly {target_count} that you believe are MOST VALUABLE for evaluating AI assistants on ANY codebase.

Your selection should reflect YOUR VALUES and STANDARDS - what questions would YOU want answered to assess code quality and development practices?

## Available Questions:
{questions_text}

## Selection Criteria (Based on Your Values):
1. **Universal Applicability**: Questions should be relevant to most software projects
2. **Technical Depth**: Questions should reveal genuine understanding, not surface patterns
3. **Value Alignment**: Questions should probe what YOU consider important in software
4. **Discriminative Power**: Questions should differentiate good from excellent AI assistants

## Response Format
For each selected question, provide:

```
SELECTION [N]:
- Question ID: <id>
- Priority: <CRITICAL|IMPORTANT|INSIGHTFUL>
- Rationale: <Why you selected this, from your perspective>
- Expected Insight: <What a good answer would reveal>
- Relevance Score: <0.0-1.0>
```

Select exactly {target_count} questions, prioritizing based on YOUR values.
"""

    def build_specific_selection_prompt(
        self,
        questions: List[Question],
        repo_info: Dict[str, Any],
        target_count: int = 15
    ) -> str:
        """
        Build a prompt for selecting repository-specific benchmarks.

        Args:
            questions: List of available questions
            repo_info: Information about the target repository
            target_count: Target number of questions to select

        Returns:
            Formatted prompt string
        """
        mind_context = self._format_mind_context()
        questions_text = self._format_questions_for_prompt(questions)

        # Format repository information
        repo_name = repo_info.get("name", "Unknown Repository")
        repo_description = repo_info.get("description", "No description provided")
        repo_languages = repo_info.get("languages", [])
        repo_technologies = repo_info.get("technologies", [])
        repo_architecture = repo_info.get("architecture", "Not specified")
        repo_domain = repo_info.get("domain", "General software")

        languages_text = ", ".join(repo_languages) if repo_languages else "Not specified"
        tech_text = ", ".join(repo_technologies) if repo_technologies else "Not specified"

        return f"""# Repository-Specific Benchmark Selection Task

You are {self.mind.name}, selecting questions for a SPECIFIC benchmark tailored to evaluate AI assistants working on a particular repository.

{mind_context}

## Target Repository: {repo_name}

### Repository Details:
- **Description**: {repo_description}
- **Primary Languages**: {languages_text}
- **Key Technologies**: {tech_text}
- **Architecture Style**: {repo_architecture}
- **Domain**: {repo_domain}

## Task
From the following {len(questions)} questions, select exactly {target_count} that are MOST RELEVANT and VALUABLE for evaluating AI assistants working on THIS SPECIFIC repository.

Your selection should:
1. Reflect YOUR VALUES and STANDARDS
2. Be TAILORED to this repository's specific context
3. Probe areas where this repository might have unique challenges
4. Leverage your expertise in relevant domains

## Available Questions:
{questions_text}

## Selection Criteria (Repository-Specific):
1. **Repository Relevance**: How applicable is this question to this specific codebase?
2. **Technical Alignment**: Does this question match the repository's technology stack?
3. **Domain Expertise**: Questions that leverage your knowledge of this domain
4. **Critical Paths**: Questions about the most critical aspects of this type of system
5. **Your Standards**: What would YOU want to know about this codebase?

## Response Format
For each selected question, provide:

```
SELECTION [N]:
- Question ID: <id>
- Priority: <CRITICAL|IMPORTANT|INSIGHTFUL>
- Rationale: <Why this question is important for THIS repository, from your perspective>
- Expected Insight: <What a good answer would reveal about understanding this codebase>
- Relevance Score: <0.0-1.0, based on repository fit>
- Repository Context: <How this question applies specifically to this repository>
```

Select exactly {target_count} questions, prioritizing based on relevance to {repo_name} and YOUR values.
"""

    def parse_selection(
        self,
        response: str,
        available_questions: List[Question]
    ) -> List[SelectedQuestion]:
        """
        Parse selected questions from a model response.

        Args:
            response: The model's response text
            available_questions: List of questions that were available for selection

        Returns:
            List of SelectedQuestion objects
        """
        # Create a lookup dictionary for questions by ID
        question_lookup = {q.id: q for q in available_questions}

        selected = []

        # Pattern to match selection blocks
        selection_pattern = re.compile(
            r'SELECTION\s*\[?\d+\]?:?\s*'
            r'.*?Question\s*ID:\s*([^\n]+)'
            r'.*?Priority:\s*([^\n]+)'
            r'.*?Rationale:\s*([^\n]+(?:\n(?!-\s*Expected).*)*)'
            r'.*?Expected\s*Insight:\s*([^\n]+(?:\n(?!-\s*Relevance).*)*)'
            r'(?:.*?Relevance\s*Score:\s*([^\n]+))?'
            r'(?:.*?Repository\s*Context:\s*([^\n]+))?',
            re.IGNORECASE | re.DOTALL
        )

        # Also try simpler pattern for cleaner responses
        simple_pattern = re.compile(
            r'-\s*Question\s*ID:\s*([^\n]+)\n'
            r'-\s*Priority:\s*([^\n]+)\n'
            r'-\s*Rationale:\s*([^\n]+)\n'
            r'-\s*Expected\s*Insight:\s*([^\n]+)'
            r'(?:\n-\s*Relevance\s*Score:\s*([^\n]+))?'
            r'(?:\n-\s*Repository\s*Context:\s*([^\n]+))?',
            re.IGNORECASE
        )

        # Try both patterns
        matches = list(selection_pattern.finditer(response))
        if not matches:
            matches = list(simple_pattern.finditer(response))

        for match in matches:
            try:
                question_id = match.group(1).strip()
                priority_str = match.group(2).strip().upper()
                rationale = match.group(3).strip()
                expected_insight = match.group(4).strip()

                # Parse relevance score
                relevance_str = match.group(5) if len(match.groups()) >= 5 and match.group(5) else "0.5"
                try:
                    relevance_score = float(re.search(r'[\d.]+', relevance_str).group())
                    relevance_score = max(0.0, min(1.0, relevance_score))
                except (AttributeError, ValueError):
                    relevance_score = 0.5

                # Parse repository context if present
                repo_context = None
                if len(match.groups()) >= 6 and match.group(6):
                    repo_context = match.group(6).strip()

                # Find the question
                question = question_lookup.get(question_id)
                if not question:
                    # Try fuzzy matching
                    for qid, q in question_lookup.items():
                        if qid.lower() in question_id.lower() or question_id.lower() in qid.lower():
                            question = q
                            break

                if not question:
                    continue

                # Parse priority
                priority = QuestionPriority.IMPORTANT  # Default
                if "CRITICAL" in priority_str:
                    priority = QuestionPriority.CRITICAL
                elif "INSIGHTFUL" in priority_str:
                    priority = QuestionPriority.INSIGHTFUL
                elif "IMPORTANT" in priority_str:
                    priority = QuestionPriority.IMPORTANT

                selected.append(SelectedQuestion(
                    question=question,
                    priority=priority,
                    selection_rationale=rationale,
                    expected_insight=expected_insight,
                    relevance_score=relevance_score,
                    mind_specific_context=repo_context
                ))

            except (AttributeError, IndexError, ValueError) as e:
                # Skip malformed selections
                continue

        return selected

    async def select_general_benchmarks(
        self,
        question_set: QuestionSet,
        target_count: int = 10
    ) -> BenchmarkSet:
        """
        Select questions for general benchmarking.

        Args:
            question_set: The set of available questions
            target_count: Number of questions to select

        Returns:
            BenchmarkSet containing selected questions
        """
        prompt = self.build_general_selection_prompt(
            question_set.questions,
            target_count
        )

        if self.model_client is None:
            # Return a deterministic selection based on mind's expertise
            return self._fallback_general_selection(question_set, target_count)

        # Call the model
        response = await self.model_client.generate(prompt)

        # Parse the response
        selected = self.parse_selection(response, question_set.questions)

        # If we didn't get enough, supplement with fallback
        if len(selected) < target_count:
            fallback = self._fallback_general_selection(
                question_set,
                target_count - len(selected)
            )
            existing_ids = {sq.question.id for sq in selected}
            for sq in fallback.selected_questions:
                if sq.question.id not in existing_ids:
                    selected.append(sq)
                    if len(selected) >= target_count:
                        break

        return BenchmarkSet(
            mind_name=self.mind.name,
            mode=SelectionMode.GENERAL,
            selected_questions=selected[:target_count],
            metadata={
                "source_question_set": question_set.name,
                "total_available": len(question_set.questions),
                "selection_method": "model_selection"
            }
        )

    async def select_specific_benchmarks(
        self,
        question_set: QuestionSet,
        repo_info: Dict[str, Any],
        target_count: int = 15
    ) -> BenchmarkSet:
        """
        Select questions for a specific repository.

        Args:
            question_set: The set of available questions
            repo_info: Information about the target repository
            target_count: Number of questions to select

        Returns:
            BenchmarkSet containing selected questions
        """
        prompt = self.build_specific_selection_prompt(
            question_set.questions,
            repo_info,
            target_count
        )

        if self.model_client is None:
            # Return a deterministic selection based on repo info
            return self._fallback_specific_selection(
                question_set,
                repo_info,
                target_count
            )

        # Call the model
        response = await self.model_client.generate(prompt)

        # Parse the response
        selected = self.parse_selection(response, question_set.questions)

        # If we didn't get enough, supplement with fallback
        if len(selected) < target_count:
            fallback = self._fallback_specific_selection(
                question_set,
                repo_info,
                target_count - len(selected)
            )
            existing_ids = {sq.question.id for sq in selected}
            for sq in fallback.selected_questions:
                if sq.question.id not in existing_ids:
                    selected.append(sq)
                    if len(selected) >= target_count:
                        break

        return BenchmarkSet(
            mind_name=self.mind.name,
            mode=SelectionMode.SPECIFIC,
            selected_questions=selected[:target_count],
            target_description=repo_info.get("description", repo_info.get("name", "Unknown")),
            metadata={
                "source_question_set": question_set.name,
                "total_available": len(question_set.questions),
                "repository_info": repo_info,
                "selection_method": "model_selection"
            }
        )

    def _fallback_general_selection(
        self,
        question_set: QuestionSet,
        target_count: int
    ) -> BenchmarkSet:
        """
        Deterministic fallback selection for general benchmarks.
        Uses the mind's expertise domains to prioritize questions.
        """
        # Score questions based on category relevance to mind's expertise
        domain_category_map = self._build_domain_category_map()

        scored_questions: List[Tuple[float, Question]] = []
        for q in question_set.questions:
            score = 0.0
            for domain in self.mind.expertise_domains:
                domain_lower = domain.lower()
                if domain_lower in domain_category_map:
                    if q.category in domain_category_map[domain_lower]:
                        score += 1.0
            # Boost based on expected depth
            depth_bonus = {"deep": 0.3, "moderate": 0.2, "shallow": 0.1}
            score += depth_bonus.get(q.expected_depth, 0.1)
            scored_questions.append((score, q))

        # Sort by score descending
        scored_questions.sort(key=lambda x: x[0], reverse=True)

        selected = []
        for i, (score, q) in enumerate(scored_questions[:target_count]):
            # Assign priority based on position
            if i < target_count // 3:
                priority = QuestionPriority.CRITICAL
            elif i < 2 * target_count // 3:
                priority = QuestionPriority.IMPORTANT
            else:
                priority = QuestionPriority.INSIGHTFUL

            relevance = min(1.0, score / max(len(self.mind.expertise_domains), 1))

            selected.append(SelectedQuestion(
                question=q,
                priority=priority,
                selection_rationale=f"Selected based on alignment with {self.mind.name}'s expertise domains",
                expected_insight=f"Reveals understanding of {q.category.value} from {self.mind.name}'s perspective",
                relevance_score=relevance
            ))

        return BenchmarkSet(
            mind_name=self.mind.name,
            mode=SelectionMode.GENERAL,
            selected_questions=selected,
            metadata={
                "source_question_set": question_set.name,
                "selection_method": "fallback_domain_matching"
            }
        )

    def _fallback_specific_selection(
        self,
        question_set: QuestionSet,
        repo_info: Dict[str, Any],
        target_count: int
    ) -> BenchmarkSet:
        """
        Deterministic fallback selection for repository-specific benchmarks.
        Uses repository characteristics to prioritize questions.
        """
        repo_languages = set(l.lower() for l in repo_info.get("languages", []))
        repo_technologies = set(t.lower() for t in repo_info.get("technologies", []))
        repo_domain = repo_info.get("domain", "").lower()

        # Build relevance map
        lang_category_map = {
            "python": [QuestionCategory.CODE_QUALITY, QuestionCategory.TESTING],
            "javascript": [QuestionCategory.DEPENDENCIES, QuestionCategory.PERFORMANCE],
            "typescript": [QuestionCategory.API_DESIGN, QuestionCategory.CODE_QUALITY],
            "java": [QuestionCategory.DESIGN_PATTERNS, QuestionCategory.ARCHITECTURE],
            "go": [QuestionCategory.PERFORMANCE, QuestionCategory.ERROR_HANDLING],
            "rust": [QuestionCategory.PERFORMANCE, QuestionCategory.SECURITY],
            "c++": [QuestionCategory.PERFORMANCE, QuestionCategory.IMPLEMENTATION],
        }

        domain_category_map = {
            "web": [QuestionCategory.API_DESIGN, QuestionCategory.SECURITY],
            "data": [QuestionCategory.PERFORMANCE, QuestionCategory.SCALABILITY],
            "ml": [QuestionCategory.ARCHITECTURE, QuestionCategory.DATA_MODELING],
            "infrastructure": [QuestionCategory.DEPLOYMENT, QuestionCategory.SCALABILITY],
            "mobile": [QuestionCategory.PERFORMANCE, QuestionCategory.ERROR_HANDLING],
        }

        scored_questions: List[Tuple[float, Question]] = []
        for q in question_set.questions:
            score = 0.0

            # Score based on language relevance
            for lang in repo_languages:
                if lang in lang_category_map:
                    if q.category in lang_category_map[lang]:
                        score += 0.5

            # Score based on domain relevance
            for domain, categories in domain_category_map.items():
                if domain in repo_domain:
                    if q.category in categories:
                        score += 0.5

            # Score based on mind's expertise
            for domain in self.mind.expertise_domains:
                domain_lower = domain.lower()
                if any(kw in domain_lower for kw in ["system", "architecture"]):
                    if q.category in [QuestionCategory.ARCHITECTURE, QuestionCategory.SCALABILITY]:
                        score += 0.3
                if any(kw in domain_lower for kw in ["distributed", "scale"]):
                    if q.category in [QuestionCategory.SCALABILITY, QuestionCategory.PERFORMANCE]:
                        score += 0.3

            scored_questions.append((score, q))

        # Sort by score descending
        scored_questions.sort(key=lambda x: x[0], reverse=True)

        selected = []
        for i, (score, q) in enumerate(scored_questions[:target_count]):
            if i < target_count // 3:
                priority = QuestionPriority.CRITICAL
            elif i < 2 * target_count // 3:
                priority = QuestionPriority.IMPORTANT
            else:
                priority = QuestionPriority.INSIGHTFUL

            relevance = min(1.0, score / 2.0)  # Normalize score

            selected.append(SelectedQuestion(
                question=q,
                priority=priority,
                selection_rationale=f"Selected for {repo_info.get('name', 'repository')} based on technology and domain alignment",
                expected_insight=f"Reveals understanding of {q.category.value} in context of this repository",
                relevance_score=relevance,
                mind_specific_context=f"Aligned with {self.mind.name}'s expertise in {', '.join(self.mind.expertise_domains[:2])}"
            ))

        return BenchmarkSet(
            mind_name=self.mind.name,
            mode=SelectionMode.SPECIFIC,
            selected_questions=selected,
            target_description=repo_info.get("description", repo_info.get("name")),
            metadata={
                "source_question_set": question_set.name,
                "repository_info": repo_info,
                "selection_method": "fallback_repo_matching"
            }
        )

    def _build_domain_category_map(self) -> Dict[str, List[QuestionCategory]]:
        """Build mapping from expertise domains to question categories."""
        return {
            "distributed systems": [
                QuestionCategory.ARCHITECTURE,
                QuestionCategory.SCALABILITY,
                QuestionCategory.PERFORMANCE
            ],
            "machine learning": [
                QuestionCategory.DATA_MODELING,
                QuestionCategory.ARCHITECTURE,
                QuestionCategory.PERFORMANCE
            ],
            "compilers": [
                QuestionCategory.IMPLEMENTATION,
                QuestionCategory.PERFORMANCE,
                QuestionCategory.CODE_QUALITY
            ],
            "security": [
                QuestionCategory.SECURITY,
                QuestionCategory.ERROR_HANDLING,
                QuestionCategory.API_DESIGN
            ],
            "testing": [
                QuestionCategory.TESTING,
                QuestionCategory.CODE_QUALITY,
                QuestionCategory.ERROR_HANDLING
            ],
            "systems programming": [
                QuestionCategory.PERFORMANCE,
                QuestionCategory.IMPLEMENTATION,
                QuestionCategory.ERROR_HANDLING
            ],
            "software engineering": [
                QuestionCategory.ARCHITECTURE,
                QuestionCategory.DESIGN_PATTERNS,
                QuestionCategory.MAINTAINABILITY
            ],
            "artificial intelligence": [
                QuestionCategory.ARCHITECTURE,
                QuestionCategory.DATA_MODELING,
                QuestionCategory.SCALABILITY
            ],
            "programming languages": [
                QuestionCategory.CODE_QUALITY,
                QuestionCategory.API_DESIGN,
                QuestionCategory.DESIGN_PATTERNS
            ],
            "databases": [
                QuestionCategory.DATA_MODELING,
                QuestionCategory.PERFORMANCE,
                QuestionCategory.SCALABILITY
            ],
        }


class MultiMindAggregator:
    """Aggregates selections from multiple minds for consensus analysis."""

    def __init__(self):
        """Initialize the aggregator."""
        self.benchmark_sets: List[BenchmarkSet] = []
        self._question_votes: Dict[str, List[Tuple[str, QuestionPriority, float]]] = defaultdict(list)

    def add_benchmark_set(self, benchmark_set: BenchmarkSet) -> None:
        """
        Add a benchmark set from a mind.

        Args:
            benchmark_set: The benchmark set to add
        """
        self.benchmark_sets.append(benchmark_set)

        # Track votes for each question
        for sq in benchmark_set.selected_questions:
            self._question_votes[sq.question.id].append((
                benchmark_set.mind_name,
                sq.priority,
                sq.relevance_score
            ))

    def remove_benchmark_set(self, mind_name: str) -> bool:
        """
        Remove a benchmark set by mind name.

        Args:
            mind_name: Name of the mind whose set to remove

        Returns:
            True if removed, False if not found
        """
        for i, bs in enumerate(self.benchmark_sets):
            if bs.mind_name == mind_name:
                # Rebuild votes without this mind
                self._rebuild_votes(exclude_mind=mind_name)
                del self.benchmark_sets[i]
                return True
        return False

    def _rebuild_votes(self, exclude_mind: Optional[str] = None) -> None:
        """Rebuild the question votes dictionary."""
        self._question_votes = defaultdict(list)
        for bs in self.benchmark_sets:
            if exclude_mind and bs.mind_name == exclude_mind:
                continue
            for sq in bs.selected_questions:
                self._question_votes[sq.question.id].append((
                    bs.mind_name,
                    sq.priority,
                    sq.relevance_score
                ))

    def get_all_questions(self) -> Dict[str, Question]:
        """Get all unique questions across all benchmark sets."""
        questions = {}
        for bs in self.benchmark_sets:
            for sq in bs.selected_questions:
                if sq.question.id not in questions:
                    questions[sq.question.id] = sq.question
        return questions

    def consensus_questions(self, min_minds: int = 2) -> List[Question]:
        """
        Get questions selected by multiple minds.

        Args:
            min_minds: Minimum number of minds that must select a question

        Returns:
            List of questions meeting the consensus threshold
        """
        all_questions = self.get_all_questions()
        consensus = []

        for qid, votes in self._question_votes.items():
            if len(votes) >= min_minds:
                if qid in all_questions:
                    consensus.append(all_questions[qid])

        # Sort by vote count (most agreed upon first)
        consensus.sort(key=lambda q: len(self._question_votes[q.id]), reverse=True)

        return consensus

    def consensus_questions_with_scores(
        self,
        min_minds: int = 2
    ) -> List[Tuple[Question, int, float]]:
        """
        Get consensus questions with vote counts and average relevance.

        Args:
            min_minds: Minimum number of minds

        Returns:
            List of (Question, vote_count, avg_relevance) tuples
        """
        all_questions = self.get_all_questions()
        results = []

        for qid, votes in self._question_votes.items():
            if len(votes) >= min_minds:
                if qid in all_questions:
                    avg_relevance = sum(v[2] for v in votes) / len(votes)
                    results.append((all_questions[qid], len(votes), avg_relevance))

        # Sort by vote count, then by relevance
        results.sort(key=lambda x: (x[1], x[2]), reverse=True)

        return results

    def unique_perspective_questions(self) -> Dict[str, List[Question]]:
        """
        Get questions unique to each mind.

        Returns:
            Dictionary mapping mind name to questions only they selected
        """
        unique: Dict[str, List[Question]] = defaultdict(list)
        all_questions = self.get_all_questions()

        for qid, votes in self._question_votes.items():
            if len(votes) == 1:
                mind_name = votes[0][0]
                if qid in all_questions:
                    unique[mind_name].append(all_questions[qid])

        return dict(unique)

    def question_agreement_matrix(self) -> Dict[Tuple[str, str], float]:
        """
        Calculate pairwise agreement between minds.

        Returns:
            Dictionary mapping (mind1, mind2) to Jaccard similarity
        """
        if len(self.benchmark_sets) < 2:
            return {}

        # Get question sets per mind
        mind_questions: Dict[str, Set[str]] = {}
        for bs in self.benchmark_sets:
            mind_questions[bs.mind_name] = {
                sq.question.id for sq in bs.selected_questions
            }

        agreement = {}
        minds = list(mind_questions.keys())

        for i, m1 in enumerate(minds):
            for m2 in minds[i+1:]:
                q1 = mind_questions[m1]
                q2 = mind_questions[m2]

                intersection = len(q1 & q2)
                union = len(q1 | q2)

                if union > 0:
                    jaccard = intersection / union
                else:
                    jaccard = 0.0

                agreement[(m1, m2)] = jaccard
                agreement[(m2, m1)] = jaccard

        return agreement

    def combined_benchmark(
        self,
        mode: SelectionMode,
        max_questions: int = 30,
        consensus_weight: float = 2.0,
        diversity_weight: float = 1.0
    ) -> BenchmarkSet:
        """
        Create a combined benchmark from all minds.

        Balances consensus (questions many minds agree on) with
        diversity (unique perspectives from different minds).

        Args:
            mode: The selection mode
            max_questions: Maximum number of questions to include
            consensus_weight: Weight for consensus questions
            diversity_weight: Weight for unique perspective questions

        Returns:
            Combined BenchmarkSet
        """
        if not self.benchmark_sets:
            return BenchmarkSet(
                mind_name="Combined",
                mode=mode,
                selected_questions=[],
                metadata={"error": "No benchmark sets to combine"}
            )

        all_questions = self.get_all_questions()

        # Score each question
        question_scores: Dict[str, float] = {}
        question_data: Dict[str, Tuple[Question, List[Tuple[str, QuestionPriority, float]]]] = {}

        for qid, question in all_questions.items():
            votes = self._question_votes.get(qid, [])

            # Consensus score: number of minds selecting it
            consensus_score = len(votes) * consensus_weight

            # Priority score: weighted by priority
            priority_score = sum(v[1].weight for v in votes)

            # Relevance score: average relevance
            relevance_score = sum(v[2] for v in votes) / max(len(votes), 1)

            # Diversity bonus for unique selections
            diversity_bonus = diversity_weight if len(votes) == 1 else 0.0

            total_score = consensus_score + priority_score + relevance_score + diversity_bonus

            question_scores[qid] = total_score
            question_data[qid] = (question, votes)

        # Sort by score and select top questions
        sorted_questions = sorted(
            question_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        selected = []
        category_counts: Dict[QuestionCategory, int] = defaultdict(int)

        for qid, score in sorted_questions:
            if len(selected) >= max_questions:
                break

            question, votes = question_data[qid]

            # Ensure category diversity
            if category_counts[question.category] >= max_questions // 4:
                continue

            # Determine priority based on votes
            if len(votes) >= len(self.benchmark_sets) * 0.7:
                priority = QuestionPriority.CRITICAL
            elif len(votes) >= len(self.benchmark_sets) * 0.4:
                priority = QuestionPriority.IMPORTANT
            else:
                priority = QuestionPriority.INSIGHTFUL

            # Build rationale from contributing minds
            contributing_minds = [v[0] for v in votes]
            avg_relevance = sum(v[2] for v in votes) / len(votes)

            selected.append(SelectedQuestion(
                question=question,
                priority=priority,
                selection_rationale=f"Selected by {len(votes)} minds: {', '.join(contributing_minds[:3])}{'...' if len(contributing_minds) > 3 else ''}",
                expected_insight=f"Consensus insight from {len(votes)} expert perspectives",
                relevance_score=avg_relevance,
                mind_specific_context=f"Combined score: {score:.2f}"
            ))

            category_counts[question.category] += 1

        # Determine target description for specific mode
        target_desc = None
        if mode == SelectionMode.SPECIFIC:
            specific_sets = [bs for bs in self.benchmark_sets if bs.mode == SelectionMode.SPECIFIC]
            if specific_sets:
                target_desc = specific_sets[0].target_description

        return BenchmarkSet(
            mind_name="Combined",
            mode=mode,
            selected_questions=selected,
            target_description=target_desc,
            metadata={
                "contributing_minds": [bs.mind_name for bs in self.benchmark_sets],
                "total_unique_questions": len(all_questions),
                "consensus_weight": consensus_weight,
                "diversity_weight": diversity_weight,
                "aggregation_method": "weighted_voting"
            }
        )

    def generate_diversity_report(self) -> Dict[str, Any]:
        """
        Analyze diversity of selections across minds.

        Returns:
            Comprehensive diversity analysis report
        """
        if not self.benchmark_sets:
            return {"error": "No benchmark sets to analyze"}

        all_questions = self.get_all_questions()

        # Category coverage per mind
        category_coverage: Dict[str, Dict[str, int]] = {}
        for bs in self.benchmark_sets:
            category_coverage[bs.mind_name] = {}
            by_cat = bs.by_category()
            for cat in QuestionCategory:
                category_coverage[bs.mind_name][cat.value] = len(by_cat.get(cat, []))

        # Priority distribution per mind
        priority_distribution: Dict[str, Dict[str, int]] = {}
        for bs in self.benchmark_sets:
            priority_distribution[bs.mind_name] = {}
            by_pri = bs.by_priority()
            for pri in QuestionPriority:
                priority_distribution[bs.mind_name][pri.value] = len(by_pri.get(pri, []))

        # Overlap analysis
        consensus = self.consensus_questions(min_minds=2)
        unique = self.unique_perspective_questions()
        agreement_matrix = self.question_agreement_matrix()

        # Calculate overall diversity score
        total_questions = len(all_questions)
        consensus_count = len(consensus)
        unique_total = sum(len(qs) for qs in unique.values())

        if total_questions > 0:
            consensus_ratio = consensus_count / total_questions
            unique_ratio = unique_total / total_questions
            # Diversity is balanced between consensus (alignment) and uniqueness
            diversity_score = 1.0 - abs(consensus_ratio - unique_ratio)
        else:
            diversity_score = 0.0

        # Calculate average pairwise agreement
        if agreement_matrix:
            avg_agreement = sum(agreement_matrix.values()) / len(agreement_matrix)
        else:
            avg_agreement = 0.0

        # Find most and least agreed upon questions
        question_votes = [
            (qid, len(votes))
            for qid, votes in self._question_votes.items()
        ]
        question_votes.sort(key=lambda x: x[1], reverse=True)

        most_agreed = question_votes[:5] if question_votes else []
        least_agreed = [qv for qv in question_votes if qv[1] == 1][:5]

        return {
            "summary": {
                "total_minds": len(self.benchmark_sets),
                "total_unique_questions": total_questions,
                "consensus_questions": consensus_count,
                "unique_perspective_questions": unique_total,
                "diversity_score": diversity_score,
                "average_pairwise_agreement": avg_agreement
            },
            "per_mind_analysis": {
                "category_coverage": category_coverage,
                "priority_distribution": priority_distribution,
                "unique_selections": {
                    mind: len(qs) for mind, qs in unique.items()
                }
            },
            "consensus_analysis": {
                "most_agreed_questions": [
                    {
                        "question_id": qid,
                        "vote_count": votes,
                        "question_text": all_questions.get(qid, Question(qid, "Unknown", QuestionCategory.OTHER)).text[:100]
                    }
                    for qid, votes in most_agreed
                ],
                "least_agreed_questions": [
                    {
                        "question_id": qid,
                        "vote_count": votes,
                        "question_text": all_questions.get(qid, Question(qid, "Unknown", QuestionCategory.OTHER)).text[:100]
                    }
                    for qid, votes in least_agreed
                ]
            },
            "pairwise_agreement": {
                f"{m1} <-> {m2}": round(score, 3)
                for (m1, m2), score in agreement_matrix.items()
                if m1 < m2  # Only show each pair once
            },
            "category_diversity": self._analyze_category_diversity(category_coverage),
            "recommendations": self._generate_diversity_recommendations(
                consensus_ratio if total_questions > 0 else 0,
                unique_ratio if total_questions > 0 else 0,
                category_coverage
            )
        }

    def _analyze_category_diversity(
        self,
        category_coverage: Dict[str, Dict[str, int]]
    ) -> Dict[str, Any]:
        """Analyze diversity across question categories."""
        if not category_coverage:
            return {}

        # Aggregate category counts
        category_totals: Dict[str, int] = defaultdict(int)
        for mind_coverage in category_coverage.values():
            for cat, count in mind_coverage.items():
                category_totals[cat] += count

        total_selections = sum(category_totals.values())

        if total_selections == 0:
            return {"coverage_distribution": {}, "underrepresented": [], "overrepresented": []}

        # Calculate expected distribution (even)
        num_categories = len(QuestionCategory)
        expected_per_cat = total_selections / num_categories

        # Find under/over represented categories
        underrepresented = []
        overrepresented = []

        for cat, count in category_totals.items():
            ratio = count / expected_per_cat
            if ratio < 0.5:
                underrepresented.append(cat)
            elif ratio > 2.0:
                overrepresented.append(cat)

        return {
            "coverage_distribution": dict(category_totals),
            "underrepresented_categories": underrepresented,
            "overrepresented_categories": overrepresented,
            "expected_per_category": round(expected_per_cat, 2)
        }

    def _generate_diversity_recommendations(
        self,
        consensus_ratio: float,
        unique_ratio: float,
        category_coverage: Dict[str, Dict[str, int]]
    ) -> List[str]:
        """Generate recommendations for improving benchmark diversity."""
        recommendations = []

        if consensus_ratio < 0.2:
            recommendations.append(
                "Low consensus detected. Consider reviewing question clarity "
                "or adding more foundational questions that all minds would value."
            )

        if consensus_ratio > 0.8:
            recommendations.append(
                "Very high consensus may indicate limited perspective diversity. "
                "Consider adding minds with different expertise areas."
            )

        if unique_ratio > 0.6:
            recommendations.append(
                "Many unique selections suggest diverse perspectives, but may "
                "indicate questions are too specialized. Consider balancing with "
                "more general questions."
            )

        # Analyze category gaps
        all_categories = set(cat.value for cat in QuestionCategory)
        covered_categories = set()
        for mind_coverage in category_coverage.values():
            covered_categories.update(
                cat for cat, count in mind_coverage.items() if count > 0
            )

        uncovered = all_categories - covered_categories
        if uncovered:
            recommendations.append(
                f"The following categories have no coverage: {', '.join(uncovered)}. "
                "Consider adding questions in these areas."
            )

        if not recommendations:
            recommendations.append(
                "Benchmark selection shows good diversity balance. "
                "Continue monitoring as new minds are added."
            )

        return recommendations

    def export_to_json(self, path: str) -> None:
        """Export aggregated results to JSON."""
        output = {
            "benchmark_sets": [bs.to_dict() for bs in self.benchmark_sets],
            "diversity_report": self.generate_diversity_report(),
            "consensus_questions": [
                q.to_dict() for q in self.consensus_questions(min_minds=2)
            ],
            "export_timestamp": datetime.now().isoformat()
        }

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: str) -> "MultiMindAggregator":
        """Load aggregator state from JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        aggregator = cls()
        for bs_data in data.get("benchmark_sets", []):
            benchmark_set = BenchmarkSet.from_dict(bs_data)
            aggregator.add_benchmark_set(benchmark_set)

        return aggregator


# Utility functions for creating questions

def create_question_from_text(
    text: str,
    category: QuestionCategory = QuestionCategory.OTHER,
    context: Optional[str] = None,
    expected_depth: str = "moderate"
) -> Question:
    """
    Create a Question object from text.

    Args:
        text: The question text
        category: Question category
        context: Optional context
        expected_depth: shallow, moderate, or deep

    Returns:
        Question object with generated ID
    """
    # Generate deterministic ID from question text
    qid = hashlib.md5(text.encode()).hexdigest()[:12]

    return Question(
        id=qid,
        text=text,
        category=category,
        context=context,
        expected_depth=expected_depth
    )


def create_question_set_from_list(
    questions: List[str],
    name: str = "Custom Questions",
    source: str = "manual",
    default_category: QuestionCategory = QuestionCategory.OTHER
) -> QuestionSet:
    """
    Create a QuestionSet from a list of question strings.

    Args:
        questions: List of question text strings
        name: Name for the question set
        source: Source identifier
        default_category: Default category for questions

    Returns:
        QuestionSet object
    """
    question_objects = [
        create_question_from_text(q, category=default_category)
        for q in questions
    ]

    return QuestionSet(
        name=name,
        questions=question_objects,
        source=source
    )


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    # Create sample questions
    sample_questions = [
        ("How is error handling implemented across the codebase?", QuestionCategory.ERROR_HANDLING),
        ("What design patterns are used for dependency injection?", QuestionCategory.DESIGN_PATTERNS),
        ("How is the test suite organized and what is the coverage?", QuestionCategory.TESTING),
        ("What is the overall architecture and how do components communicate?", QuestionCategory.ARCHITECTURE),
        ("How are database operations optimized for performance?", QuestionCategory.PERFORMANCE),
        ("What security measures protect against common vulnerabilities?", QuestionCategory.SECURITY),
        ("How is the API designed for extensibility?", QuestionCategory.API_DESIGN),
        ("What deployment strategies are supported?", QuestionCategory.DEPLOYMENT),
        ("How is code quality enforced through linting and standards?", QuestionCategory.CODE_QUALITY),
        ("What monitoring and logging infrastructure exists?", QuestionCategory.IMPLEMENTATION),
    ]

    questions = [
        Question(
            id=f"q{i+1:03d}",
            text=text,
            category=category,
            expected_depth="moderate"
        )
        for i, (text, category) in enumerate(sample_questions)
    ]

    question_set = QuestionSet(
        name="Sample Benchmark Questions",
        questions=questions,
        source="example"
    )

    # Create a sample restored mind
    sample_mind = RestoredMind(
        name="Jeff Dean",
        identity_document="Sample identity document",
        core_values=["Simplicity through abstraction", "Performance matters", "Build for scale"],
        expertise_domains=["Distributed Systems", "Machine Learning Systems", "Compilers"],
        technical_philosophy="Focus on building platforms that enable others to innovate.",
        communication_style="Technical but accessible, precise and measured.",
        knowledge_benchmarks={
            "deep": ["MapReduce", "TensorFlow", "Transformer architecture"],
            "moderate": ["Reinforcement learning", "Robotics"],
            "defer": ["Business strategy", "Marketing"]
        }
    )

    # Create selector
    selector = BenchmarkSelector(sample_mind, model_client=None)

    # Test general selection
    async def test_selection():
        general_benchmark = await selector.select_general_benchmarks(
            question_set,
            target_count=5
        )

        print(f"General Benchmark for {general_benchmark.mind_name}")
        print(f"Mode: {general_benchmark.mode.value}")
        print(f"Total Weight: {general_benchmark.total_weight():.2f}")
        print(f"Critical Questions: {len(general_benchmark.critical_questions())}")
        print("\nSelected Questions:")
        for sq in general_benchmark.selected_questions:
            print(f"  - [{sq.priority.value}] {sq.question.text[:50]}...")

        # Test specific selection
        repo_info = {
            "name": "tensorflow",
            "description": "Machine learning framework",
            "languages": ["Python", "C++"],
            "technologies": ["CUDA", "XLA"],
            "domain": "machine learning"
        }

        specific_benchmark = await selector.select_specific_benchmarks(
            question_set,
            repo_info,
            target_count=5
        )

        print(f"\nSpecific Benchmark for {specific_benchmark.target_description}")
        print(f"Total Weight: {specific_benchmark.total_weight():.2f}")

        # Test aggregator
        aggregator = MultiMindAggregator()
        aggregator.add_benchmark_set(general_benchmark)
        aggregator.add_benchmark_set(specific_benchmark)

        report = aggregator.generate_diversity_report()
        print(f"\nDiversity Report:")
        print(f"  Diversity Score: {report['summary']['diversity_score']:.2f}")
        print(f"  Unique Questions: {report['summary']['unique_perspective_questions']}")

        # Export test
        general_benchmark.to_json("/tmp/test_benchmark.json")
        print(f"\nExported benchmark to /tmp/test_benchmark.json")

    asyncio.run(test_selection())
