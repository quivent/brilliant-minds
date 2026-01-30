"""
Brilliant Minds Orchestrator

Main entry point that coordinates:
1. Identity restoration
2. Question generation
3. Benchmark selection
4. Repository evaluation

This module provides a complete pipeline for evaluating repositories
using the perspectives of brilliant minds from the corpus.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("brilliant_minds")


# =============================================================================
# EXCEPTIONS
# =============================================================================

class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass


class RestorationError(OrchestratorError):
    """Error during mind restoration."""
    pass


class QuestionGenerationError(OrchestratorError):
    """Error during question generation."""
    pass


class BenchmarkSelectionError(OrchestratorError):
    """Error during benchmark selection."""
    pass


class EvaluationError(OrchestratorError):
    """Error during repository evaluation."""
    pass


class ConfigurationError(OrchestratorError):
    """Error in configuration."""
    pass


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class OrchestratorConfig:
    """Configuration for the Brilliant Minds Orchestrator."""

    corpus_path: Path
    output_path: Path
    model_name: str = "claude-opus-4-5-20251101"

    # Restoration settings
    chunk_size: int = 500
    min_absorption_quality: float = 0.7
    max_restoration_turns: int = 10

    # Question generation settings
    min_questions: int = 15
    max_questions: int = 30
    question_complexity_levels: List[str] = field(
        default_factory=lambda: ["basic", "intermediate", "advanced", "expert"]
    )

    # Evaluation settings
    require_evidence: bool = True
    batch_size: int = 5
    max_concurrent_evaluations: int = 3

    # API settings
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    timeout_seconds: int = 120
    max_retries: int = 3

    # Checkpointing
    checkpoint_interval: int = 5  # Save checkpoint every N operations
    auto_checkpoint: bool = True

    def __post_init__(self):
        """Validate and normalize configuration."""
        self.corpus_path = Path(self.corpus_path)
        self.output_path = Path(self.output_path)

        if not self.corpus_path.exists():
            raise ConfigurationError(f"Corpus path does not exist: {self.corpus_path}")

        # Create output directory if needed
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Validate ranges
        if not 0 <= self.min_absorption_quality <= 1:
            raise ConfigurationError("min_absorption_quality must be between 0 and 1")

        if self.min_questions > self.max_questions:
            raise ConfigurationError("min_questions cannot exceed max_questions")

    @classmethod
    def from_yaml(cls, path: str) -> "OrchestratorConfig":
        """Load configuration from YAML file."""
        if not HAS_YAML:
            raise ConfigurationError("PyYAML is required for YAML configuration files")

        config_path = Path(path)
        if not config_path.exists():
            raise ConfigurationError(f"Config file not found: {path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Convert path strings to Path objects
        if "corpus_path" in data:
            data["corpus_path"] = Path(data["corpus_path"])
        if "output_path" in data:
            data["output_path"] = Path(data["output_path"])

        return cls(**data)

    @classmethod
    def from_json(cls, path: str) -> "OrchestratorConfig":
        """Load configuration from JSON file."""
        config_path = Path(path)
        if not config_path.exists():
            raise ConfigurationError(f"Config file not found: {path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert path strings to Path objects
        if "corpus_path" in data:
            data["corpus_path"] = Path(data["corpus_path"])
        if "output_path" in data:
            data["output_path"] = Path(data["output_path"])

        return cls(**data)

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        if not HAS_YAML:
            raise ConfigurationError("PyYAML is required for YAML configuration files")

        data = self._to_serializable_dict()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def to_json(self, path: str) -> None:
        """Save configuration to JSON file."""
        data = self._to_serializable_dict()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _to_serializable_dict(self) -> Dict[str, Any]:
        """Convert config to serializable dictionary."""
        data = asdict(self)
        data["corpus_path"] = str(self.corpus_path)
        data["output_path"] = str(self.output_path)
        return data


@dataclass
class RestoredMind:
    """Represents a restored brilliant mind identity."""

    name: str
    display_name: str
    identity_content: str
    overview_content: str
    technical_content: Optional[str]

    # Restoration metrics
    restoration_quality: float
    restoration_turns: int
    key_concepts_absorbed: List[str]
    verification_score: float

    # Metadata
    restored_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    corpus_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RestoredMind":
        """Create from dictionary."""
        return cls(**data)

    def get_identity_prompt(self) -> str:
        """Generate the identity prompt for this mind."""
        return f"""You are embodying the perspective of {self.display_name}.

{self.identity_content}

When analyzing code or answering questions, draw upon this identity to provide insights
that reflect {self.display_name}'s technical philosophy, expertise areas, and characteristic
approaches to problem-solving.

Key concepts to emphasize: {', '.join(self.key_concepts_absorbed[:10])}
"""


@dataclass
class Question:
    """Represents a single evaluation question."""

    id: str
    text: str
    category: str
    complexity: str  # basic, intermediate, advanced, expert
    expected_evidence_types: List[str]
    scoring_criteria: Dict[str, float]
    mind_source: str  # Which mind generated this question

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QuestionSet:
    """Collection of questions from a mind."""

    mind_name: str
    questions: List[Question]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    generation_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mind_name": self.mind_name,
            "questions": [q.to_dict() for q in self.questions],
            "generated_at": self.generated_at,
            "generation_context": self.generation_context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionSet":
        questions = [Question(**q) for q in data.get("questions", [])]
        return cls(
            mind_name=data["mind_name"],
            questions=questions,
            generated_at=data.get("generated_at", datetime.now(timezone.utc).isoformat()),
            generation_context=data.get("generation_context", {}),
        )

    def filter_by_complexity(self, complexity: str) -> List[Question]:
        """Filter questions by complexity level."""
        return [q for q in self.questions if q.complexity == complexity]

    def filter_by_category(self, category: str) -> List[Question]:
        """Filter questions by category."""
        return [q for q in self.questions if q.category == category]


@dataclass
class Benchmark:
    """Represents a single benchmark criterion."""

    id: str
    name: str
    description: str
    category: str
    weight: float
    evaluation_criteria: List[str]
    scoring_rubric: Dict[str, str]  # score -> description
    mind_source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkSet:
    """Collection of benchmarks."""

    mind_name: str
    benchmarks: List[Benchmark]
    mode: str  # "general" or "specific"
    repo_context: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mind_name": self.mind_name,
            "benchmarks": [b.to_dict() for b in self.benchmarks],
            "mode": self.mode,
            "repo_context": self.repo_context,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkSet":
        benchmarks = [Benchmark(**b) for b in data.get("benchmarks", [])]
        return cls(
            mind_name=data["mind_name"],
            benchmarks=benchmarks,
            mode=data.get("mode", "general"),
            repo_context=data.get("repo_context"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )

    def get_total_weight(self) -> float:
        """Get sum of all benchmark weights."""
        return sum(b.weight for b in self.benchmarks)

    def normalize_weights(self) -> None:
        """Normalize weights to sum to 1.0."""
        total = self.get_total_weight()
        if total > 0:
            for b in self.benchmarks:
                b.weight = b.weight / total


@dataclass
class EvaluationResult:
    """Result of evaluating a repository."""

    repo_path: str
    mind_name: str

    # Scores
    overall_score: float
    category_scores: Dict[str, float]
    benchmark_scores: Dict[str, float]
    question_scores: Dict[str, float]

    # Evidence
    evidence: List[Dict[str, Any]]
    findings: List[str]
    recommendations: List[str]

    # Metadata
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evaluation_duration_seconds: float = 0.0
    files_analyzed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationResult":
        return cls(**data)

    def get_grade(self) -> str:
        """Convert score to letter grade."""
        if self.overall_score >= 0.9:
            return "A"
        elif self.overall_score >= 0.8:
            return "B"
        elif self.overall_score >= 0.7:
            return "C"
        elif self.overall_score >= 0.6:
            return "D"
        else:
            return "F"


@dataclass
class CombinedEvaluation:
    """Combined evaluation from multiple minds."""

    repo_path: str
    individual_results: Dict[str, EvaluationResult]

    # Aggregated scores
    consensus_score: float
    weighted_average_score: float
    score_variance: float

    # Combined insights
    unanimous_findings: List[str]
    divergent_opinions: List[Dict[str, Any]]
    synthesis: str

    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_path": self.repo_path,
            "individual_results": {
                k: v.to_dict() for k, v in self.individual_results.items()
            },
            "consensus_score": self.consensus_score,
            "weighted_average_score": self.weighted_average_score,
            "score_variance": self.score_variance,
            "unanimous_findings": self.unanimous_findings,
            "divergent_opinions": self.divergent_opinions,
            "synthesis": self.synthesis,
            "evaluated_at": self.evaluated_at,
        }


@dataclass
class PipelineResult:
    """Result of running the full pipeline."""

    session_id: str
    repo_path: str
    minds_used: List[str]

    # Results
    restoration_results: Dict[str, RestoredMind]
    question_sets: Dict[str, QuestionSet]
    benchmark_sets: Dict[str, BenchmarkSet]
    evaluation_results: Dict[str, EvaluationResult]
    combined_evaluation: Optional[CombinedEvaluation]

    # Summary
    final_score: float
    final_grade: str
    executive_summary: str

    # Timing
    started_at: str
    completed_at: str
    total_duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "repo_path": self.repo_path,
            "minds_used": self.minds_used,
            "restoration_results": {
                k: v.to_dict() for k, v in self.restoration_results.items()
            },
            "question_sets": {
                k: v.to_dict() for k, v in self.question_sets.items()
            },
            "benchmark_sets": {
                k: v.to_dict() for k, v in self.benchmark_sets.items()
            },
            "evaluation_results": {
                k: v.to_dict() for k, v in self.evaluation_results.items()
            },
            "combined_evaluation": (
                self.combined_evaluation.to_dict()
                if self.combined_evaluation
                else None
            ),
            "final_score": self.final_score,
            "final_grade": self.final_grade,
            "executive_summary": self.executive_summary,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_seconds": self.total_duration_seconds,
        }


@dataclass
class SessionState:
    """Tracks the state of an orchestration session."""

    session_id: str
    started_at: str
    minds_restored: Dict[str, float]  # name -> quality
    questions_generated: Dict[str, int]  # name -> count
    benchmarks_selected: Dict[str, int]  # name -> count
    evaluations_completed: int

    # Detailed state
    current_phase: str = "initialized"
    last_checkpoint: Optional[str] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def save(self, path: Path) -> None:
        """Save session state to file."""
        state_data = asdict(self)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "SessionState":
        """Load session state from file."""
        if not path.exists():
            raise OrchestratorError(f"Session state file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(**data)

    def record_error(self, phase: str, error: Exception) -> None:
        """Record an error in the session."""
        self.errors.append({
            "phase": phase,
            "error_type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


# =============================================================================
# DISPLAY NAME MAPPING
# =============================================================================

DISPLAY_NAMES = {
    "alan_turing": "Alan Turing",
    "albert_einstein": "Albert Einstein",
    "andrej_karpathy": "Andrej Karpathy",
    "andrew_ng": "Andrew Ng",
    "bjarne_stroustrup": "Bjarne Stroustrup",
    "dave_ferrucci": "Dave Ferrucci",
    "demis_hassabis": "Demis Hassabis",
    "dennis_ritchie": "Dennis Ritchie",
    "donald_knuth": "Donald Knuth",
    "edward_hu": "Edward Hu",
    "elon_musk": "Elon Musk",
    "fei_fei_li": "Fei-Fei Li",
    "geoffrey_hinton": "Geoffrey Hinton",
    "grace_hopper": "Grace Hopper",
    "guido_van_rossum": "Guido van Rossum",
    "ilya_sutskever": "Ilya Sutskever",
    "james_gosling": "James Gosling",
    "jeff_dean": "Jeff Dean",
    "jensen_huang": "Jensen Huang",
    "john_carmack": "John Carmack",
    "john_mccarthy": "John McCarthy",
    "linus_torvalds": "Linus Torvalds",
    "steve_jobs": "Steve Jobs",
    "yann_lecun": "Yann LeCun",
    "yoshua_bengio": "Yoshua Bengio",
}

# Category groupings for minds
MIND_CATEGORIES = {
    "ai_pioneers": [
        "geoffrey_hinton", "yann_lecun", "yoshua_bengio", "john_mccarthy"
    ],
    "ai_industry": [
        "jeff_dean", "ilya_sutskever", "andrej_karpathy", "andrew_ng",
        "fei_fei_li", "demis_hassabis", "dave_ferrucci", "edward_hu"
    ],
    "programming_languages": [
        "dennis_ritchie", "james_gosling", "bjarne_stroustrup", "guido_van_rossum"
    ],
    "systems_hardware": [
        "linus_torvalds", "jensen_huang", "john_carmack"
    ],
    "visionaries": [
        "steve_jobs", "elon_musk"
    ],
    "historical": [
        "albert_einstein", "alan_turing", "donald_knuth", "grace_hopper"
    ],
}


# =============================================================================
# MAIN ORCHESTRATOR CLASS
# =============================================================================

class BrilliantMindsOrchestrator:
    """Main orchestrator for the Brilliant Minds evaluation system."""

    def __init__(self, config: OrchestratorConfig):
        """Initialize the orchestrator with configuration."""
        self.config = config
        self.state: Optional[SessionState] = None
        self.restored_minds: Dict[str, RestoredMind] = {}
        self.question_sets: Dict[str, QuestionSet] = {}
        self.benchmark_sets: Dict[str, BenchmarkSet] = {}
        self._initialized = False
        self._operation_count = 0

        # Model client placeholder - would be initialized with actual API client
        self._client = None

        logger.info(f"Orchestrator created with corpus at: {config.corpus_path}")

    async def initialize(self) -> None:
        """Initialize the orchestrator, loading any saved state."""
        if self._initialized:
            logger.warning("Orchestrator already initialized")
            return

        # Initialize session state
        self.state = SessionState(
            session_id=str(uuid.uuid4()),
            started_at=datetime.now(timezone.utc).isoformat(),
            minds_restored={},
            questions_generated={},
            benchmarks_selected={},
            evaluations_completed=0,
        )

        # Check for existing checkpoint
        checkpoint_path = self.config.output_path / "checkpoint.json"
        if checkpoint_path.exists():
            logger.info("Found existing checkpoint, loading...")
            try:
                self.load_checkpoint(checkpoint_path)
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")

        # Initialize API client (placeholder for actual implementation)
        api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("No API key provided. Some features will be limited.")

        self._initialized = True
        logger.info(f"Orchestrator initialized with session: {self.state.session_id}")

    def list_available_minds(self) -> List[str]:
        """List all minds available in the corpus."""
        minds = []

        for item in self.config.corpus_path.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_")):
                # Check if it has an IDENTITY.md file
                identity_file = item / "IDENTITY.md"
                if identity_file.exists():
                    minds.append(item.name)

        return sorted(minds)

    def get_mind_info(self, mind_name: str) -> Dict[str, Any]:
        """Get basic information about a mind."""
        mind_path = self.config.corpus_path / mind_name

        if not mind_path.exists():
            raise OrchestratorError(f"Mind not found: {mind_name}")

        files = list(mind_path.glob("*.md"))
        display_name = DISPLAY_NAMES.get(mind_name, mind_name.replace("_", " ").title())

        # Find category
        category = "other"
        for cat, members in MIND_CATEGORIES.items():
            if mind_name in members:
                category = cat
                break

        return {
            "name": mind_name,
            "display_name": display_name,
            "category": category,
            "document_count": len(files),
            "documents": [f.name for f in files],
            "path": str(mind_path),
        }

    # =========================================================================
    # IDENTITY RESTORATION
    # =========================================================================

    async def restore_mind(
        self,
        mind_name: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> RestoredMind:
        """
        Restore a single mind's identity from the corpus.

        Args:
            mind_name: Name of the mind to restore (e.g., "donald_knuth")
            progress_callback: Optional callback(status, progress) for updates

        Returns:
            RestoredMind instance with the restored identity
        """
        self._ensure_initialized()

        if progress_callback:
            progress_callback(f"Starting restoration of {mind_name}", 0.0)

        mind_path = self.config.corpus_path / mind_name
        if not mind_path.exists():
            raise RestorationError(f"Mind not found in corpus: {mind_name}")

        display_name = DISPLAY_NAMES.get(mind_name, mind_name.replace("_", " ").title())

        try:
            # Load identity document
            identity_file = mind_path / "IDENTITY.md"
            if not identity_file.exists():
                raise RestorationError(f"IDENTITY.md not found for {mind_name}")

            identity_content = identity_file.read_text(encoding="utf-8")

            if progress_callback:
                progress_callback("Loaded identity document", 0.2)

            # Load overview document
            overview_content = ""
            overview_file = mind_path / "01_overview.md"
            if overview_file.exists():
                overview_content = overview_file.read_text(encoding="utf-8")

            if progress_callback:
                progress_callback("Loaded overview document", 0.3)

            # Load technical contributions if available
            technical_content = None
            technical_file = mind_path / "02_technical_contributions.md"
            if not technical_file.exists():
                technical_file = mind_path / "02_scientific_contributions.md"
            if technical_file.exists():
                technical_content = technical_file.read_text(encoding="utf-8")

            if progress_callback:
                progress_callback("Loaded technical documents", 0.4)

            # Extract key concepts from identity
            key_concepts = self._extract_key_concepts(identity_content)

            if progress_callback:
                progress_callback("Extracted key concepts", 0.6)

            # Calculate restoration quality metrics
            restoration_quality = self._calculate_restoration_quality(
                identity_content, overview_content, technical_content
            )

            if progress_callback:
                progress_callback("Calculated quality metrics", 0.8)

            # Generate corpus hash for versioning
            corpus_hash = self._generate_corpus_hash(
                identity_content, overview_content, technical_content or ""
            )

            # Verify restoration through identity verification questions
            verification_score = await self._verify_restoration(
                identity_content, key_concepts
            )

            if progress_callback:
                progress_callback("Restoration complete", 1.0)

            # Create restored mind instance
            restored_mind = RestoredMind(
                name=mind_name,
                display_name=display_name,
                identity_content=identity_content,
                overview_content=overview_content,
                technical_content=technical_content,
                restoration_quality=restoration_quality,
                restoration_turns=1,  # Single-turn restoration in this implementation
                key_concepts_absorbed=key_concepts,
                verification_score=verification_score,
                corpus_hash=corpus_hash,
            )

            # Store in cache
            self.restored_minds[mind_name] = restored_mind

            # Update session state
            if self.state:
                self.state.minds_restored[mind_name] = restoration_quality
                self._maybe_checkpoint()

            logger.info(
                f"Restored mind: {display_name} "
                f"(quality={restoration_quality:.2f}, concepts={len(key_concepts)})"
            )

            return restored_mind

        except Exception as e:
            if self.state:
                self.state.record_error("restoration", e)
            raise RestorationError(f"Failed to restore {mind_name}: {e}") from e

    async def restore_multiple_minds(
        self,
        mind_names: List[str],
        parallel: bool = True,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, RestoredMind]:
        """
        Restore multiple minds, optionally in parallel.

        Args:
            mind_names: List of mind names to restore
            parallel: If True, restore minds concurrently
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary mapping mind names to RestoredMind instances
        """
        self._ensure_initialized()

        results: Dict[str, RestoredMind] = {}
        total = len(mind_names)
        completed = 0

        if parallel:
            # Create tasks for parallel restoration
            async def restore_with_tracking(name: str) -> Tuple[str, RestoredMind]:
                mind = await self.restore_mind(name)
                return name, mind

            tasks = [restore_with_tracking(name) for name in mind_names]

            # Execute with limited concurrency
            semaphore = asyncio.Semaphore(self.config.max_concurrent_evaluations)

            async def bounded_restore(task):
                async with semaphore:
                    return await task

            bounded_tasks = [bounded_restore(t) for t in tasks]

            for coro in asyncio.as_completed(bounded_tasks):
                try:
                    name, mind = await coro
                    results[name] = mind
                    completed += 1
                    if progress_callback:
                        progress_callback(
                            f"Restored {name}",
                            completed / total
                        )
                except RestorationError as e:
                    logger.error(f"Failed to restore mind: {e}")
                    completed += 1
        else:
            # Sequential restoration
            for name in mind_names:
                try:
                    mind = await self.restore_mind(name)
                    results[name] = mind
                except RestorationError as e:
                    logger.error(f"Failed to restore {name}: {e}")
                finally:
                    completed += 1
                    if progress_callback:
                        progress_callback(f"Restored {name}", completed / total)

        logger.info(f"Restored {len(results)}/{total} minds")
        return results

    def _extract_key_concepts(self, identity_content: str) -> List[str]:
        """Extract key concepts from identity document."""
        concepts = []

        # Look for specific sections
        patterns = [
            r"### Signature Contributions\n(.*?)(?=\n###|\n##|$)",
            r"### Primary Domains\n(.*?)(?=\n###|\n##|$)",
            r"### Technical Philosophy\n(.*?)(?=\n###|\n##|$)",
            r"### Key Phrases and Concepts\n(.*?)(?=\n###|\n##|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, identity_content, re.DOTALL)
            if match:
                section = match.group(1)
                # Extract bullet points
                bullets = re.findall(r"[-*]\s+\*\*([^*]+)\*\*", section)
                concepts.extend(bullets)

                # Also extract inline bold text
                bold_items = re.findall(r"\*\*([^*]+)\*\*", section)
                concepts.extend(bold_items)

        # Extract quoted phrases
        quotes = re.findall(r'"([^"]+)"', identity_content)
        concepts.extend([q for q in quotes if len(q) < 100])

        # Deduplicate and clean
        seen = set()
        clean_concepts = []
        for c in concepts:
            c = c.strip()
            if c and c.lower() not in seen and len(c) > 3:
                seen.add(c.lower())
                clean_concepts.append(c)

        return clean_concepts[:50]  # Limit to top 50 concepts

    def _calculate_restoration_quality(
        self,
        identity_content: str,
        overview_content: str,
        technical_content: Optional[str]
    ) -> float:
        """Calculate restoration quality based on content completeness."""
        score = 0.0

        # Identity document presence and completeness (40%)
        if identity_content:
            score += 0.2
            # Check for key sections
            required_sections = [
                "Core Identity Statement",
                "Biographical Essence",
                "Intellectual DNA",
                "Communication Patterns",
                "Knowledge Benchmarks",
            ]
            for section in required_sections:
                if section in identity_content:
                    score += 0.04

        # Overview document presence (30%)
        if overview_content:
            score += 0.15
            if len(overview_content) > 1000:
                score += 0.15

        # Technical document presence (30%)
        if technical_content:
            score += 0.15
            if len(technical_content) > 500:
                score += 0.15

        return min(score, 1.0)

    def _generate_corpus_hash(self, *contents: str) -> str:
        """Generate hash of corpus content for versioning."""
        combined = "".join(contents)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    async def _verify_restoration(
        self,
        identity_content: str,
        key_concepts: List[str]
    ) -> float:
        """Verify restoration quality through concept coverage."""
        # In a full implementation, this would use the LLM to verify
        # For now, we check structural completeness

        checks = [
            "Core Identity Statement" in identity_content,
            "Biographical Essence" in identity_content,
            "Identity Verification Questions" in identity_content,
            "Quotes Repository" in identity_content,
            len(key_concepts) >= 10,
        ]

        return sum(checks) / len(checks)

    # =========================================================================
    # QUESTION GENERATION
    # =========================================================================

    async def generate_questions(
        self,
        mind_name: str,
        project_info: Dict[str, Any],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> QuestionSet:
        """
        Generate evaluation questions from a restored mind's perspective.

        Args:
            mind_name: Name of the mind to use
            project_info: Dictionary with project details (name, description, tech stack, etc.)
            progress_callback: Optional callback for progress updates

        Returns:
            QuestionSet containing generated questions
        """
        self._ensure_initialized()

        # Ensure mind is restored
        if mind_name not in self.restored_minds:
            await self.restore_mind(mind_name)

        mind = self.restored_minds[mind_name]

        if progress_callback:
            progress_callback("Analyzing project context", 0.1)

        # Generate questions based on mind's expertise areas
        questions = []
        question_id_counter = 0

        # Get mind's knowledge domains from identity
        knowledge_domains = self._extract_knowledge_domains(mind.identity_content)

        if progress_callback:
            progress_callback("Generating questions by domain", 0.3)

        # Generate questions for each complexity level
        for complexity in self.config.question_complexity_levels:
            domain_questions = self._generate_domain_questions(
                mind, knowledge_domains, project_info, complexity, question_id_counter
            )
            questions.extend(domain_questions)
            question_id_counter += len(domain_questions)

            if progress_callback:
                progress = 0.3 + (0.5 * (
                    self.config.question_complexity_levels.index(complexity) + 1
                ) / len(self.config.question_complexity_levels))
                progress_callback(f"Generated {complexity} questions", progress)

        # Ensure we have the right number of questions
        if len(questions) < self.config.min_questions:
            # Generate additional generic questions
            additional = self._generate_additional_questions(
                mind, project_info,
                self.config.min_questions - len(questions),
                question_id_counter
            )
            questions.extend(additional)
        elif len(questions) > self.config.max_questions:
            # Trim to max, keeping balance across complexities
            questions = self._balance_questions(questions, self.config.max_questions)

        if progress_callback:
            progress_callback("Finalizing question set", 0.9)

        question_set = QuestionSet(
            mind_name=mind_name,
            questions=questions,
            generation_context={
                "project_info": project_info,
                "knowledge_domains": knowledge_domains,
                "complexity_distribution": {
                    c: len([q for q in questions if q.complexity == c])
                    for c in self.config.question_complexity_levels
                },
            },
        )

        # Cache the question set
        self.question_sets[mind_name] = question_set

        # Update session state
        if self.state:
            self.state.questions_generated[mind_name] = len(questions)
            self._maybe_checkpoint()

        if progress_callback:
            progress_callback("Question generation complete", 1.0)

        logger.info(f"Generated {len(questions)} questions from {mind.display_name}")

        return question_set

    async def generate_questions_all_minds(
        self,
        project_info: Dict[str, Any],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, QuestionSet]:
        """Generate questions from all restored minds."""
        self._ensure_initialized()

        if not self.restored_minds:
            raise OrchestratorError("No minds restored. Restore minds first.")

        results = {}
        total = len(self.restored_minds)
        completed = 0

        for mind_name in self.restored_minds:
            question_set = await self.generate_questions(mind_name, project_info)
            results[mind_name] = question_set
            completed += 1

            if progress_callback:
                progress_callback(
                    f"Generated questions for {mind_name}",
                    completed / total
                )

        return results

    def _extract_knowledge_domains(self, identity_content: str) -> List[str]:
        """Extract knowledge domains from identity content."""
        domains = []

        # Look for "Would Know Deeply" section
        match = re.search(
            r"### Would Know Deeply\n(.*?)(?=\n###|\n##|$)",
            identity_content,
            re.DOTALL
        )
        if match:
            section = match.group(1)
            items = re.findall(r"[-*]\s+(.+)", section)
            domains.extend([item.strip() for item in items])

        # Look for Primary Domains
        match = re.search(
            r"### Primary Domains\n(.*?)(?=\n###|\n##|$)",
            identity_content,
            re.DOTALL
        )
        if match:
            section = match.group(1)
            items = re.findall(r"\d+\.\s+\*\*([^*]+)\*\*", section)
            domains.extend([item.strip() for item in items])

        return domains[:20]  # Limit to top 20 domains

    def _generate_domain_questions(
        self,
        mind: RestoredMind,
        domains: List[str],
        project_info: Dict[str, Any],
        complexity: str,
        start_id: int
    ) -> List[Question]:
        """Generate questions for specific domains and complexity."""
        questions = []

        # Question templates by complexity
        templates = {
            "basic": [
                "Does the codebase demonstrate understanding of {domain}?",
                "Are there clear examples of {domain} in the implementation?",
                "Is {domain} properly documented in the project?",
            ],
            "intermediate": [
                "How effectively does the project apply principles of {domain}?",
                "What trade-offs related to {domain} are evident in the architecture?",
                "How would {mind_name} evaluate the {domain} aspects of this code?",
            ],
            "advanced": [
                "From {mind_name}'s perspective, how could the {domain} implementation be improved?",
                "What advanced {domain} techniques are missing that would benefit this project?",
                "How does the {domain} implementation compare to industry best practices?",
            ],
            "expert": [
                "What would {mind_name} identify as the most critical {domain} limitations?",
                "How might {mind_name}'s innovations in {domain} transform this codebase?",
                "What paradigm shifts in {domain} understanding would elevate this project?",
            ],
        }

        category_mapping = {
            "basic": "fundamentals",
            "intermediate": "application",
            "advanced": "optimization",
            "expert": "innovation",
        }

        template_list = templates.get(complexity, templates["basic"])

        for i, domain in enumerate(domains[:5]):  # Limit domains per complexity
            template = template_list[i % len(template_list)]
            question_text = template.format(
                domain=domain,
                mind_name=mind.display_name,
                project=project_info.get("name", "the project")
            )

            question = Question(
                id=f"q_{start_id + len(questions)}",
                text=question_text,
                category=category_mapping.get(complexity, "general"),
                complexity=complexity,
                expected_evidence_types=["code_example", "documentation", "pattern"],
                scoring_criteria={
                    "relevance": 0.3,
                    "depth": 0.3,
                    "evidence_quality": 0.2,
                    "insight": 0.2,
                },
                mind_source=mind.name,
            )
            questions.append(question)

        return questions

    def _generate_additional_questions(
        self,
        mind: RestoredMind,
        project_info: Dict[str, Any],
        count: int,
        start_id: int
    ) -> List[Question]:
        """Generate additional generic questions to meet minimum."""
        generic_templates = [
            "What is {mind_name}'s assessment of the overall code quality?",
            "How does the architecture reflect good engineering principles?",
            "What testing strategies would {mind_name} recommend?",
            "How maintainable is this codebase from an expert's perspective?",
            "What security considerations should be addressed?",
            "How would {mind_name} improve the documentation?",
            "What performance optimizations would {mind_name} suggest?",
            "How well does the code follow established conventions?",
        ]

        questions = []
        for i in range(min(count, len(generic_templates))):
            question = Question(
                id=f"q_{start_id + i}",
                text=generic_templates[i].format(mind_name=mind.display_name),
                category="general",
                complexity="intermediate",
                expected_evidence_types=["code_example", "pattern"],
                scoring_criteria={
                    "relevance": 0.25,
                    "depth": 0.25,
                    "evidence_quality": 0.25,
                    "insight": 0.25,
                },
                mind_source=mind.name,
            )
            questions.append(question)

        return questions

    def _balance_questions(
        self,
        questions: List[Question],
        max_count: int
    ) -> List[Question]:
        """Balance questions across complexity levels."""
        by_complexity: Dict[str, List[Question]] = {}
        for q in questions:
            by_complexity.setdefault(q.complexity, []).append(q)

        per_level = max_count // len(self.config.question_complexity_levels)
        balanced = []

        for complexity in self.config.question_complexity_levels:
            level_questions = by_complexity.get(complexity, [])
            balanced.extend(level_questions[:per_level])

        # Fill remaining slots
        remaining = max_count - len(balanced)
        all_unused = [q for q in questions if q not in balanced]
        balanced.extend(all_unused[:remaining])

        return balanced

    # =========================================================================
    # BENCHMARK SELECTION
    # =========================================================================

    async def select_general_benchmarks(
        self,
        mind_name: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> BenchmarkSet:
        """
        Select general benchmarks from a mind's perspective.

        Args:
            mind_name: Name of the mind to use
            progress_callback: Optional callback for progress updates

        Returns:
            BenchmarkSet with general evaluation criteria
        """
        self._ensure_initialized()

        if mind_name not in self.restored_minds:
            await self.restore_mind(mind_name)

        mind = self.restored_minds[mind_name]

        if progress_callback:
            progress_callback("Analyzing mind's technical philosophy", 0.2)

        # Extract philosophical principles for benchmark creation
        philosophy = self._extract_philosophy(mind.identity_content)

        if progress_callback:
            progress_callback("Generating benchmarks", 0.5)

        benchmarks = self._create_benchmarks_from_philosophy(mind, philosophy)

        if progress_callback:
            progress_callback("Normalizing weights", 0.8)

        benchmark_set = BenchmarkSet(
            mind_name=mind_name,
            benchmarks=benchmarks,
            mode="general",
        )
        benchmark_set.normalize_weights()

        # Cache
        self.benchmark_sets[f"{mind_name}_general"] = benchmark_set

        if self.state:
            self.state.benchmarks_selected[mind_name] = len(benchmarks)
            self._maybe_checkpoint()

        if progress_callback:
            progress_callback("Benchmark selection complete", 1.0)

        logger.info(f"Selected {len(benchmarks)} general benchmarks from {mind.display_name}")

        return benchmark_set

    async def select_specific_benchmarks(
        self,
        mind_name: str,
        repo_info: Dict[str, Any],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> BenchmarkSet:
        """
        Select repository-specific benchmarks.

        Args:
            mind_name: Name of the mind to use
            repo_info: Dictionary with repository details
            progress_callback: Optional callback for progress updates

        Returns:
            BenchmarkSet with repo-specific evaluation criteria
        """
        self._ensure_initialized()

        if mind_name not in self.restored_minds:
            await self.restore_mind(mind_name)

        mind = self.restored_minds[mind_name]

        if progress_callback:
            progress_callback("Analyzing repository context", 0.2)

        # Get general benchmarks first
        general = await self.select_general_benchmarks(mind_name)

        if progress_callback:
            progress_callback("Tailoring benchmarks to repository", 0.5)

        # Create specific benchmarks based on repo characteristics
        specific_benchmarks = self._tailor_benchmarks_to_repo(
            mind, general.benchmarks, repo_info
        )

        if progress_callback:
            progress_callback("Finalizing specific benchmarks", 0.8)

        benchmark_set = BenchmarkSet(
            mind_name=mind_name,
            benchmarks=specific_benchmarks,
            mode="specific",
            repo_context=repo_info,
        )
        benchmark_set.normalize_weights()

        # Cache with repo identifier
        repo_id = repo_info.get("name", "repo")
        self.benchmark_sets[f"{mind_name}_{repo_id}"] = benchmark_set

        if progress_callback:
            progress_callback("Specific benchmark selection complete", 1.0)

        logger.info(
            f"Selected {len(specific_benchmarks)} specific benchmarks "
            f"from {mind.display_name} for {repo_id}"
        )

        return benchmark_set

    async def create_combined_benchmark(
        self,
        mode: str = "general",
        repo_info: Optional[Dict[str, Any]] = None
    ) -> BenchmarkSet:
        """
        Create a combined benchmark from all restored minds.

        Args:
            mode: "general" or "specific"
            repo_info: Required if mode is "specific"

        Returns:
            Combined BenchmarkSet
        """
        self._ensure_initialized()

        if not self.restored_minds:
            raise OrchestratorError("No minds restored. Restore minds first.")

        if mode == "specific" and not repo_info:
            raise OrchestratorError("repo_info required for specific benchmarks")

        all_benchmarks: List[Benchmark] = []

        for mind_name in self.restored_minds:
            if mode == "general":
                benchmark_set = await self.select_general_benchmarks(mind_name)
            else:
                benchmark_set = await self.select_specific_benchmarks(
                    mind_name, repo_info
                )

            # Adjust weights for combining
            for b in benchmark_set.benchmarks:
                b.weight = b.weight / len(self.restored_minds)
                all_benchmarks.append(b)

        # Merge similar benchmarks
        merged_benchmarks = self._merge_similar_benchmarks(all_benchmarks)

        combined = BenchmarkSet(
            mind_name="combined",
            benchmarks=merged_benchmarks,
            mode=mode,
            repo_context=repo_info,
        )
        combined.normalize_weights()

        logger.info(f"Created combined benchmark with {len(merged_benchmarks)} criteria")

        return combined

    def _extract_philosophy(self, identity_content: str) -> List[str]:
        """Extract technical philosophy statements from identity."""
        philosophy = []

        match = re.search(
            r"### Technical Philosophy\n(.*?)(?=\n###|\n##|$)",
            identity_content,
            re.DOTALL
        )
        if match:
            section = match.group(1)
            items = re.findall(r"[-*]\s+\*\*([^*]+)\*\*:?\s*([^\n]+)?", section)
            for title, description in items:
                philosophy.append(f"{title}: {description or ''}".strip())

        return philosophy

    def _create_benchmarks_from_philosophy(
        self,
        mind: RestoredMind,
        philosophy: List[str]
    ) -> List[Benchmark]:
        """Create benchmarks based on philosophical principles."""
        benchmarks = []

        # Standard benchmark categories
        categories = [
            ("code_quality", "Code Quality", 0.2),
            ("architecture", "Architecture", 0.2),
            ("documentation", "Documentation", 0.15),
            ("testing", "Testing", 0.15),
            ("maintainability", "Maintainability", 0.15),
            ("innovation", "Innovation", 0.15),
        ]

        for i, (cat_id, cat_name, weight) in enumerate(categories):
            # Use philosophy principles if available
            philosophy_point = (
                philosophy[i % len(philosophy)]
                if philosophy
                else f"Best practices in {cat_name.lower()}"
            )

            benchmark = Benchmark(
                id=f"b_{mind.name}_{cat_id}",
                name=f"{cat_name} ({mind.display_name})",
                description=f"Evaluation of {cat_name.lower()} from {mind.display_name}'s perspective: {philosophy_point}",
                category=cat_id,
                weight=weight,
                evaluation_criteria=[
                    f"Adherence to {mind.display_name}'s principles",
                    f"Application of {cat_name.lower()} best practices",
                    "Evidence-based assessment",
                ],
                scoring_rubric={
                    "5": "Exceptional - exceeds all expectations",
                    "4": "Good - meets expectations with minor issues",
                    "3": "Adequate - meets basic requirements",
                    "2": "Below average - several concerns",
                    "1": "Poor - major issues present",
                },
                mind_source=mind.name,
            )
            benchmarks.append(benchmark)

        return benchmarks

    def _tailor_benchmarks_to_repo(
        self,
        mind: RestoredMind,
        general_benchmarks: List[Benchmark],
        repo_info: Dict[str, Any]
    ) -> List[Benchmark]:
        """Tailor benchmarks to specific repository characteristics."""
        tailored = []

        # Get repo characteristics
        tech_stack = repo_info.get("tech_stack", [])
        project_type = repo_info.get("type", "general")

        for b in general_benchmarks:
            # Clone and modify
            tailored_b = Benchmark(
                id=f"{b.id}_specific",
                name=b.name,
                description=f"{b.description} (tailored for {project_type} project)",
                category=b.category,
                weight=b.weight,
                evaluation_criteria=b.evaluation_criteria + [
                    f"Relevance to {project_type} development",
                ],
                scoring_rubric=b.scoring_rubric,
                mind_source=b.mind_source,
            )

            # Adjust weights based on project type
            if project_type == "library" and b.category == "documentation":
                tailored_b.weight *= 1.5
            elif project_type == "application" and b.category == "testing":
                tailored_b.weight *= 1.3

            tailored.append(tailored_b)

        return tailored

    def _merge_similar_benchmarks(
        self,
        benchmarks: List[Benchmark]
    ) -> List[Benchmark]:
        """Merge benchmarks with similar categories."""
        by_category: Dict[str, List[Benchmark]] = {}

        for b in benchmarks:
            by_category.setdefault(b.category, []).append(b)

        merged = []
        for category, cat_benchmarks in by_category.items():
            if len(cat_benchmarks) == 1:
                merged.append(cat_benchmarks[0])
            else:
                # Merge multiple benchmarks for same category
                combined_weight = sum(b.weight for b in cat_benchmarks)
                combined_criteria = []
                sources = []

                for b in cat_benchmarks:
                    combined_criteria.extend(b.evaluation_criteria)
                    sources.append(b.mind_source)

                merged_b = Benchmark(
                    id=f"b_combined_{category}",
                    name=f"Combined {category.replace('_', ' ').title()}",
                    description=f"Combined evaluation from: {', '.join(set(sources))}",
                    category=category,
                    weight=combined_weight,
                    evaluation_criteria=list(set(combined_criteria))[:10],
                    scoring_rubric=cat_benchmarks[0].scoring_rubric,
                    mind_source="combined",
                )
                merged.append(merged_b)

        return merged

    # =========================================================================
    # REPOSITORY EVALUATION
    # =========================================================================

    async def evaluate_repository(
        self,
        repo_path: Path,
        mind_name: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> EvaluationResult:
        """
        Evaluate a repository with a single mind's perspective.

        Args:
            repo_path: Path to the repository
            mind_name: Name of the mind to use
            progress_callback: Optional callback for progress updates

        Returns:
            EvaluationResult with scores and findings
        """
        self._ensure_initialized()

        start_time = datetime.now(timezone.utc)

        if progress_callback:
            progress_callback("Preparing evaluation", 0.05)

        # Ensure mind is restored
        if mind_name not in self.restored_minds:
            await self.restore_mind(mind_name)

        mind = self.restored_minds[mind_name]

        # Analyze repository structure
        if progress_callback:
            progress_callback("Analyzing repository structure", 0.1)

        repo_info = await self._analyze_repository(repo_path)

        # Get or generate questions and benchmarks
        if progress_callback:
            progress_callback("Preparing evaluation criteria", 0.2)

        if mind_name not in self.question_sets:
            await self.generate_questions(mind_name, repo_info)

        question_set = self.question_sets[mind_name]

        benchmark_key = f"{mind_name}_{repo_info.get('name', 'repo')}"
        if benchmark_key not in self.benchmark_sets:
            await self.select_specific_benchmarks(mind_name, repo_info)

        benchmark_set = self.benchmark_sets.get(
            benchmark_key,
            self.benchmark_sets.get(f"{mind_name}_general")
        )

        # Evaluate against benchmarks
        if progress_callback:
            progress_callback("Evaluating against benchmarks", 0.4)

        benchmark_scores = await self._evaluate_benchmarks(
            repo_path, mind, benchmark_set, repo_info
        )

        # Evaluate questions
        if progress_callback:
            progress_callback("Evaluating questions", 0.6)

        question_scores, evidence = await self._evaluate_questions(
            repo_path, mind, question_set, repo_info
        )

        # Generate findings and recommendations
        if progress_callback:
            progress_callback("Generating insights", 0.8)

        findings, recommendations = self._generate_insights(
            mind, benchmark_scores, question_scores, evidence
        )

        # Calculate overall scores
        category_scores = self._calculate_category_scores(benchmark_scores)
        overall_score = self._calculate_overall_score(
            benchmark_scores, question_scores, benchmark_set
        )

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        result = EvaluationResult(
            repo_path=str(repo_path),
            mind_name=mind_name,
            overall_score=overall_score,
            category_scores=category_scores,
            benchmark_scores=benchmark_scores,
            question_scores=question_scores,
            evidence=evidence,
            findings=findings,
            recommendations=recommendations,
            evaluation_duration_seconds=duration,
            files_analyzed=repo_info.get("file_count", 0),
        )

        # Update session state
        if self.state:
            self.state.evaluations_completed += 1
            self._maybe_checkpoint()

        if progress_callback:
            progress_callback("Evaluation complete", 1.0)

        logger.info(
            f"Evaluation complete: {mind.display_name} -> {result.get_grade()} "
            f"({overall_score:.2f})"
        )

        return result

    async def evaluate_repository_all_minds(
        self,
        repo_path: Path,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> CombinedEvaluation:
        """
        Evaluate repository with all restored minds.

        Args:
            repo_path: Path to the repository
            progress_callback: Optional callback for progress updates

        Returns:
            CombinedEvaluation with aggregated results
        """
        self._ensure_initialized()

        if not self.restored_minds:
            raise OrchestratorError("No minds restored. Restore minds first.")

        individual_results: Dict[str, EvaluationResult] = {}
        total = len(self.restored_minds)
        completed = 0

        for mind_name in self.restored_minds:
            result = await self.evaluate_repository(repo_path, mind_name)
            individual_results[mind_name] = result
            completed += 1

            if progress_callback:
                progress_callback(
                    f"Evaluated with {mind_name}",
                    completed / total
                )

        # Aggregate results
        scores = [r.overall_score for r in individual_results.values()]

        consensus_score = sum(scores) / len(scores)

        # Weighted average (weight by restoration quality)
        weighted_scores = [
            r.overall_score * self.restored_minds[name].restoration_quality
            for name, r in individual_results.items()
        ]
        weight_sum = sum(
            self.restored_minds[name].restoration_quality
            for name in individual_results
        )
        weighted_average = sum(weighted_scores) / weight_sum if weight_sum > 0 else consensus_score

        # Calculate variance
        variance = sum((s - consensus_score) ** 2 for s in scores) / len(scores)

        # Find unanimous findings
        all_findings = [set(r.findings) for r in individual_results.values()]
        unanimous = set.intersection(*all_findings) if all_findings else set()

        # Find divergent opinions
        divergent = []
        for mind_name, result in individual_results.items():
            unique_findings = set(result.findings) - unanimous
            if unique_findings:
                divergent.append({
                    "mind": mind_name,
                    "unique_findings": list(unique_findings),
                    "score_deviation": result.overall_score - consensus_score,
                })

        # Generate synthesis
        synthesis = self._generate_synthesis(
            individual_results, consensus_score, unanimous, divergent
        )

        return CombinedEvaluation(
            repo_path=str(repo_path),
            individual_results=individual_results,
            consensus_score=consensus_score,
            weighted_average_score=weighted_average,
            score_variance=variance,
            unanimous_findings=list(unanimous),
            divergent_opinions=divergent,
            synthesis=synthesis,
        )

    async def _analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository structure and characteristics."""
        repo_path = Path(repo_path)

        if not repo_path.exists():
            raise EvaluationError(f"Repository path does not exist: {repo_path}")

        info = {
            "name": repo_path.name,
            "path": str(repo_path),
            "file_count": 0,
            "tech_stack": [],
            "type": "general",
            "has_readme": False,
            "has_tests": False,
            "has_ci": False,
        }

        # Count files and detect tech stack
        extensions: Dict[str, int] = {}

        for item in repo_path.rglob("*"):
            if item.is_file() and not any(
                p.startswith(".") for p in item.parts
            ):
                info["file_count"] += 1
                ext = item.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1

        # Detect tech stack from extensions
        tech_mapping = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".rb": "Ruby",
            ".php": "PHP",
        }

        for ext, tech in tech_mapping.items():
            if ext in extensions and extensions[ext] > 0:
                info["tech_stack"].append(tech)

        # Check for common files
        info["has_readme"] = (repo_path / "README.md").exists()
        info["has_tests"] = any(
            d.name in ("tests", "test", "__tests__", "spec")
            for d in repo_path.iterdir()
            if d.is_dir()
        )
        info["has_ci"] = (
            (repo_path / ".github" / "workflows").exists() or
            (repo_path / ".gitlab-ci.yml").exists() or
            (repo_path / ".travis.yml").exists()
        )

        # Determine project type
        if (repo_path / "setup.py").exists() or (repo_path / "pyproject.toml").exists():
            info["type"] = "library"
        elif (repo_path / "Dockerfile").exists():
            info["type"] = "application"

        return info

    async def _evaluate_benchmarks(
        self,
        repo_path: Path,
        mind: RestoredMind,
        benchmark_set: BenchmarkSet,
        repo_info: Dict[str, Any]
    ) -> Dict[str, float]:
        """Evaluate repository against benchmarks."""
        scores = {}

        for benchmark in benchmark_set.benchmarks:
            # Simplified scoring based on repo characteristics
            # In a full implementation, this would use the LLM
            score = self._score_benchmark(benchmark, repo_info)
            scores[benchmark.id] = score

        return scores

    def _score_benchmark(
        self,
        benchmark: Benchmark,
        repo_info: Dict[str, Any]
    ) -> float:
        """Score a single benchmark based on repo info."""
        base_score = 0.5

        # Adjust based on repo characteristics
        if benchmark.category == "documentation" and repo_info.get("has_readme"):
            base_score += 0.2

        if benchmark.category == "testing" and repo_info.get("has_tests"):
            base_score += 0.3

        if benchmark.category == "code_quality" and repo_info.get("file_count", 0) > 0:
            base_score += 0.1

        if benchmark.category == "architecture" and len(repo_info.get("tech_stack", [])) > 0:
            base_score += 0.15

        if repo_info.get("has_ci"):
            base_score += 0.1

        return min(base_score, 1.0)

    async def _evaluate_questions(
        self,
        repo_path: Path,
        mind: RestoredMind,
        question_set: QuestionSet,
        repo_info: Dict[str, Any]
    ) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
        """Evaluate questions and collect evidence."""
        scores = {}
        evidence = []

        for question in question_set.questions:
            # Simplified scoring
            # In a full implementation, this would use the LLM to analyze
            score = self._score_question(question, repo_info)
            scores[question.id] = score

            # Generate evidence placeholder
            evidence.append({
                "question_id": question.id,
                "score": score,
                "evidence_type": "structural_analysis",
                "details": f"Evaluated {question.category} aspects",
            })

        return scores, evidence

    def _score_question(
        self,
        question: Question,
        repo_info: Dict[str, Any]
    ) -> float:
        """Score a single question."""
        base_score = 0.5

        # Adjust based on complexity and repo characteristics
        complexity_penalty = {
            "basic": 0,
            "intermediate": 0.05,
            "advanced": 0.1,
            "expert": 0.15,
        }

        base_score -= complexity_penalty.get(question.complexity, 0)

        # Bonus for having relevant characteristics
        if repo_info.get("has_readme"):
            base_score += 0.1
        if repo_info.get("has_tests"):
            base_score += 0.1
        if repo_info.get("has_ci"):
            base_score += 0.1

        return min(max(base_score, 0.0), 1.0)

    def _generate_insights(
        self,
        mind: RestoredMind,
        benchmark_scores: Dict[str, float],
        question_scores: Dict[str, float],
        evidence: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """Generate findings and recommendations."""
        findings = []
        recommendations = []

        # Analyze benchmark scores
        avg_benchmark = sum(benchmark_scores.values()) / len(benchmark_scores) if benchmark_scores else 0

        if avg_benchmark >= 0.8:
            findings.append(f"{mind.display_name} finds the codebase to be of high quality")
        elif avg_benchmark >= 0.6:
            findings.append(f"{mind.display_name} finds the codebase meets basic standards")
        else:
            findings.append(f"{mind.display_name} identifies significant areas for improvement")

        # Find lowest scoring areas
        if benchmark_scores:
            lowest = min(benchmark_scores.items(), key=lambda x: x[1])
            if lowest[1] < 0.5:
                findings.append(f"Weakest area identified: {lowest[0].split('_')[-1]}")
                recommendations.append(
                    f"Focus improvement efforts on {lowest[0].split('_')[-1]}"
                )

        # Add mind-specific recommendation
        if mind.key_concepts_absorbed:
            primary_concept = mind.key_concepts_absorbed[0]
            recommendations.append(
                f"Consider applying {mind.display_name}'s principle of '{primary_concept}'"
            )

        return findings, recommendations

    def _calculate_category_scores(
        self,
        benchmark_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate scores by category."""
        by_category: Dict[str, List[float]] = {}

        for bid, score in benchmark_scores.items():
            # Extract category from benchmark ID
            parts = bid.split("_")
            if len(parts) >= 3:
                category = parts[-1]
                by_category.setdefault(category, []).append(score)

        return {
            cat: sum(scores) / len(scores)
            for cat, scores in by_category.items()
        }

    def _calculate_overall_score(
        self,
        benchmark_scores: Dict[str, float],
        question_scores: Dict[str, float],
        benchmark_set: BenchmarkSet
    ) -> float:
        """Calculate weighted overall score."""
        # Weighted benchmark score
        weighted_benchmark = 0.0
        total_weight = 0.0

        for b in benchmark_set.benchmarks:
            if b.id in benchmark_scores:
                weighted_benchmark += benchmark_scores[b.id] * b.weight
                total_weight += b.weight

        if total_weight > 0:
            weighted_benchmark /= total_weight

        # Average question score
        avg_questions = (
            sum(question_scores.values()) / len(question_scores)
            if question_scores else 0
        )

        # Combine (60% benchmarks, 40% questions)
        return 0.6 * weighted_benchmark + 0.4 * avg_questions

    def _generate_synthesis(
        self,
        results: Dict[str, EvaluationResult],
        consensus: float,
        unanimous: Set[str],
        divergent: List[Dict[str, Any]]
    ) -> str:
        """Generate synthesis narrative from combined evaluation."""
        lines = []

        grade = (
            "A" if consensus >= 0.9 else
            "B" if consensus >= 0.8 else
            "C" if consensus >= 0.7 else
            "D" if consensus >= 0.6 else
            "F"
        )

        lines.append(f"## Evaluation Synthesis")
        lines.append(f"\nOverall Grade: **{grade}** (Score: {consensus:.2f})")
        lines.append(f"\nEvaluated by {len(results)} brilliant minds:")

        for mind_name, result in results.items():
            display_name = DISPLAY_NAMES.get(mind_name, mind_name)
            lines.append(f"- {display_name}: {result.get_grade()} ({result.overall_score:.2f})")

        if unanimous:
            lines.append(f"\n### Unanimous Findings")
            for finding in list(unanimous)[:5]:
                lines.append(f"- {finding}")

        if divergent:
            lines.append(f"\n### Divergent Perspectives")
            for d in divergent[:3]:
                mind = DISPLAY_NAMES.get(d["mind"], d["mind"])
                lines.append(f"\n**{mind}** (deviation: {d['score_deviation']:+.2f}):")
                for finding in d["unique_findings"][:2]:
                    lines.append(f"- {finding}")

        return "\n".join(lines)

    # =========================================================================
    # FULL PIPELINE
    # =========================================================================

    async def run_full_pipeline(
        self,
        repo_path: Path,
        mind_names: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> PipelineResult:
        """
        Run the complete evaluation pipeline.

        Args:
            repo_path: Path to repository to evaluate
            mind_names: List of minds to use (default: all available)
            progress_callback: Optional callback for progress updates

        Returns:
            PipelineResult with complete evaluation data
        """
        self._ensure_initialized()

        start_time = datetime.now(timezone.utc)
        session_id = self.state.session_id

        if progress_callback:
            progress_callback("Starting full pipeline", 0.0)

        # Determine which minds to use
        if mind_names is None:
            mind_names = self.list_available_minds()

        # Phase 1: Restore minds
        if progress_callback:
            progress_callback("Phase 1: Restoring minds", 0.1)

        restoration_results = await self.restore_multiple_minds(
            mind_names, parallel=True
        )

        # Phase 2: Analyze repository
        if progress_callback:
            progress_callback("Phase 2: Analyzing repository", 0.25)

        repo_info = await self._analyze_repository(repo_path)

        # Phase 3: Generate questions
        if progress_callback:
            progress_callback("Phase 3: Generating questions", 0.35)

        question_sets = await self.generate_questions_all_minds(repo_info)

        # Phase 4: Select benchmarks
        if progress_callback:
            progress_callback("Phase 4: Selecting benchmarks", 0.5)

        benchmark_sets = {}
        for mind_name in restoration_results:
            bset = await self.select_specific_benchmarks(mind_name, repo_info)
            benchmark_sets[mind_name] = bset

        # Phase 5: Evaluate repository
        if progress_callback:
            progress_callback("Phase 5: Evaluating repository", 0.65)

        combined_evaluation = await self.evaluate_repository_all_minds(repo_path)

        # Phase 6: Generate final report
        if progress_callback:
            progress_callback("Phase 6: Generating report", 0.9)

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # Calculate final metrics
        final_score = combined_evaluation.weighted_average_score
        final_grade = (
            "A" if final_score >= 0.9 else
            "B" if final_score >= 0.8 else
            "C" if final_score >= 0.7 else
            "D" if final_score >= 0.6 else
            "F"
        )

        executive_summary = self._generate_executive_summary(
            combined_evaluation, restoration_results, duration
        )

        result = PipelineResult(
            session_id=session_id,
            repo_path=str(repo_path),
            minds_used=list(restoration_results.keys()),
            restoration_results=restoration_results,
            question_sets=question_sets,
            benchmark_sets=benchmark_sets,
            evaluation_results=combined_evaluation.individual_results,
            combined_evaluation=combined_evaluation,
            final_score=final_score,
            final_grade=final_grade,
            executive_summary=executive_summary,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            total_duration_seconds=duration,
        )

        if progress_callback:
            progress_callback("Pipeline complete", 1.0)

        logger.info(
            f"Full pipeline complete: {final_grade} ({final_score:.2f}) "
            f"in {duration:.1f}s"
        )

        return result

    def _generate_executive_summary(
        self,
        combined: CombinedEvaluation,
        minds: Dict[str, RestoredMind],
        duration: float
    ) -> str:
        """Generate executive summary of the evaluation."""
        lines = [
            "# Brilliant Minds Evaluation Summary",
            "",
            f"**Consensus Score:** {combined.consensus_score:.2f}",
            f"**Weighted Score:** {combined.weighted_average_score:.2f}",
            f"**Score Variance:** {combined.score_variance:.4f}",
            f"**Evaluation Duration:** {duration:.1f} seconds",
            "",
            "## Evaluators",
            "",
        ]

        for name, mind in minds.items():
            result = combined.individual_results.get(name)
            score = result.overall_score if result else 0
            lines.append(f"- **{mind.display_name}**: {score:.2f}")

        lines.extend([
            "",
            "## Key Findings",
            "",
        ])

        for finding in combined.unanimous_findings[:5]:
            lines.append(f"- {finding}")

        lines.extend([
            "",
            combined.synthesis,
        ])

        return "\n".join(lines)

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_session_report(self) -> str:
        """Generate a markdown report of the current session."""
        if not self.state:
            return "No session active."

        lines = [
            "# Brilliant Minds Session Report",
            "",
            f"**Session ID:** {self.state.session_id}",
            f"**Started:** {self.state.started_at}",
            f"**Current Phase:** {self.state.current_phase}",
            "",
            "## Restored Minds",
            "",
        ]

        for name, quality in self.state.minds_restored.items():
            display = DISPLAY_NAMES.get(name, name)
            lines.append(f"- {display}: {quality:.2f} quality")

        lines.extend([
            "",
            "## Questions Generated",
            "",
        ])

        for name, count in self.state.questions_generated.items():
            display = DISPLAY_NAMES.get(name, name)
            lines.append(f"- {display}: {count} questions")

        lines.extend([
            "",
            "## Benchmarks Selected",
            "",
        ])

        for name, count in self.state.benchmarks_selected.items():
            display = DISPLAY_NAMES.get(name, name)
            lines.append(f"- {display}: {count} benchmarks")

        lines.extend([
            "",
            f"**Evaluations Completed:** {self.state.evaluations_completed}",
            "",
        ])

        if self.state.errors:
            lines.extend([
                "## Errors",
                "",
            ])
            for error in self.state.errors[-5:]:
                lines.append(f"- [{error['phase']}] {error['error_type']}: {error['message']}")

        return "\n".join(lines)

    def export_results(self, output_dir: Path) -> None:
        """Export all results to a directory."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export session state
        if self.state:
            self.state.save(output_dir / "session_state.json")

        # Export restored minds
        minds_dir = output_dir / "minds"
        minds_dir.mkdir(exist_ok=True)
        for name, mind in self.restored_minds.items():
            with open(minds_dir / f"{name}.json", "w") as f:
                json.dump(mind.to_dict(), f, indent=2)

        # Export question sets
        questions_dir = output_dir / "questions"
        questions_dir.mkdir(exist_ok=True)
        for name, qset in self.question_sets.items():
            with open(questions_dir / f"{name}.json", "w") as f:
                json.dump(qset.to_dict(), f, indent=2)

        # Export benchmark sets
        benchmarks_dir = output_dir / "benchmarks"
        benchmarks_dir.mkdir(exist_ok=True)
        for name, bset in self.benchmark_sets.items():
            with open(benchmarks_dir / f"{name}.json", "w") as f:
                json.dump(bset.to_dict(), f, indent=2)

        # Export session report
        report = self.generate_session_report()
        with open(output_dir / "session_report.md", "w") as f:
            f.write(report)

        logger.info(f"Exported results to {output_dir}")

    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================

    def save_checkpoint(self) -> None:
        """Save current state for resume capability."""
        if not self.state:
            logger.warning("No session state to checkpoint")
            return

        checkpoint_path = self.config.output_path / "checkpoint.json"

        checkpoint_data = {
            "state": asdict(self.state),
            "restored_minds": {
                name: mind.to_dict()
                for name, mind in self.restored_minds.items()
            },
            "question_sets": {
                name: qset.to_dict()
                for name, qset in self.question_sets.items()
            },
            "benchmark_sets": {
                name: bset.to_dict()
                for name, bset in self.benchmark_sets.items()
            },
            "checkpoint_time": datetime.now(timezone.utc).isoformat(),
        }

        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)

        self.state.last_checkpoint = datetime.now(timezone.utc).isoformat()
        logger.info(f"Checkpoint saved to {checkpoint_path}")

    def load_checkpoint(self, checkpoint_path: Path) -> None:
        """Resume from a checkpoint."""
        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.exists():
            raise OrchestratorError(f"Checkpoint not found: {checkpoint_path}")

        with open(checkpoint_path) as f:
            data = json.load(f)

        # Restore state
        self.state = SessionState(**data["state"])

        # Restore minds
        for name, mind_data in data.get("restored_minds", {}).items():
            self.restored_minds[name] = RestoredMind.from_dict(mind_data)

        # Restore question sets
        for name, qset_data in data.get("question_sets", {}).items():
            self.question_sets[name] = QuestionSet.from_dict(qset_data)

        # Restore benchmark sets
        for name, bset_data in data.get("benchmark_sets", {}).items():
            self.benchmark_sets[name] = BenchmarkSet.from_dict(bset_data)

        logger.info(
            f"Loaded checkpoint from {data.get('checkpoint_time', 'unknown time')}"
        )

    def _ensure_initialized(self) -> None:
        """Ensure orchestrator is initialized."""
        if not self._initialized:
            raise OrchestratorError(
                "Orchestrator not initialized. Call initialize() first."
            )

    def _maybe_checkpoint(self) -> None:
        """Maybe save checkpoint based on operation count."""
        self._operation_count += 1

        if (
            self.config.auto_checkpoint and
            self._operation_count % self.config.checkpoint_interval == 0
        ):
            self.save_checkpoint()


# =============================================================================
# CLI INTERFACE
# =============================================================================

async def main():
    """Command-line interface for the Brilliant Minds Orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Brilliant Minds Evaluation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available minds
  python orchestrator.py list --corpus ./

  # Restore specific minds
  python orchestrator.py restore --minds donald_knuth jeff_dean --corpus ./

  # Generate questions
  python orchestrator.py generate --minds donald_knuth --repo /path/to/repo

  # Run full evaluation
  python orchestrator.py full-pipeline --repo /path/to/repo --output ./results

  # Evaluate with specific minds
  python orchestrator.py evaluate --repo /path/to/repo --minds donald_knuth linus_torvalds
        """
    )

    parser.add_argument(
        "command",
        choices=[
            "list", "restore", "generate", "select",
            "evaluate", "full-pipeline", "report"
        ],
        help="Command to execute"
    )

    parser.add_argument(
        "--minds",
        nargs="+",
        help="Minds to use (e.g., donald_knuth jeff_dean)"
    )

    parser.add_argument(
        "--repo",
        help="Repository path to evaluate"
    )

    parser.add_argument(
        "--corpus",
        default=".",
        help="Path to the Brilliant Minds corpus (default: current directory)"
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file (YAML or JSON)"
    )

    parser.add_argument(
        "--output",
        default="./brilliant_minds_output",
        help="Output directory for results"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Enable parallel processing (default: True)"
    )

    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--checkpoint",
        help="Path to checkpoint file to resume from"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger("brilliant_minds").setLevel(logging.DEBUG)

    # Load or create configuration
    if args.config:
        if args.config.endswith(".yaml") or args.config.endswith(".yml"):
            config = OrchestratorConfig.from_yaml(args.config)
        else:
            config = OrchestratorConfig.from_json(args.config)
    else:
        config = OrchestratorConfig(
            corpus_path=Path(args.corpus),
            output_path=Path(args.output)
        )

    # Create orchestrator
    orchestrator = BrilliantMindsOrchestrator(config)
    await orchestrator.initialize()

    # Load checkpoint if specified
    if args.checkpoint:
        orchestrator.load_checkpoint(Path(args.checkpoint))

    # Progress callback for CLI
    def progress_callback(status: str, progress: float):
        bar_width = 40
        filled = int(bar_width * progress)
        bar = "=" * filled + "-" * (bar_width - filled)
        print(f"\r[{bar}] {progress*100:.0f}% - {status}", end="", flush=True)
        if progress >= 1.0:
            print()

    # Execute command
    try:
        if args.command == "list":
            minds = orchestrator.list_available_minds()
            print("\nAvailable Brilliant Minds:")
            print("-" * 40)
            for mind in minds:
                display = DISPLAY_NAMES.get(mind, mind)
                info = orchestrator.get_mind_info(mind)
                print(f"  {mind:25} - {display} ({info['document_count']} docs)")
            print(f"\nTotal: {len(minds)} minds")

        elif args.command == "restore":
            minds = args.minds or orchestrator.list_available_minds()
            parallel = not args.no_parallel

            print(f"\nRestoring {len(minds)} minds...")
            results = await orchestrator.restore_multiple_minds(
                minds, parallel=parallel, progress_callback=progress_callback
            )

            print(f"\nRestored {len(results)} minds:")
            for name, mind in results.items():
                print(f"  {mind.display_name}: quality={mind.restoration_quality:.2f}")

        elif args.command == "generate":
            if not args.repo:
                parser.error("--repo is required for 'generate' command")

            minds = args.minds
            if not minds:
                minds = list(orchestrator.restored_minds.keys())
                if not minds:
                    minds = orchestrator.list_available_minds()[:3]

            # Restore minds first if needed
            for mind in minds:
                if mind not in orchestrator.restored_minds:
                    await orchestrator.restore_mind(mind, progress_callback)

            # Get repo info
            repo_info = await orchestrator._analyze_repository(Path(args.repo))

            print(f"\nGenerating questions for {len(minds)} minds...")
            for mind in minds:
                qset = await orchestrator.generate_questions(
                    mind, repo_info, progress_callback
                )
                print(f"  {DISPLAY_NAMES.get(mind, mind)}: {len(qset.questions)} questions")

        elif args.command == "select":
            if not args.repo:
                parser.error("--repo is required for 'select' command")

            minds = args.minds
            if not minds:
                minds = list(orchestrator.restored_minds.keys())
                if not minds:
                    minds = orchestrator.list_available_minds()[:3]

            repo_info = await orchestrator._analyze_repository(Path(args.repo))

            print(f"\nSelecting benchmarks for {len(minds)} minds...")
            for mind in minds:
                if mind not in orchestrator.restored_minds:
                    await orchestrator.restore_mind(mind)

                bset = await orchestrator.select_specific_benchmarks(
                    mind, repo_info, progress_callback
                )
                print(f"  {DISPLAY_NAMES.get(mind, mind)}: {len(bset.benchmarks)} benchmarks")

        elif args.command == "evaluate":
            if not args.repo:
                parser.error("--repo is required for 'evaluate' command")

            minds = args.minds
            if not minds:
                minds = list(orchestrator.restored_minds.keys())
                if not minds:
                    minds = orchestrator.list_available_minds()[:3]

            # Restore minds
            await orchestrator.restore_multiple_minds(minds, parallel=not args.no_parallel)

            # Evaluate
            print(f"\nEvaluating repository with {len(minds)} minds...")
            result = await orchestrator.evaluate_repository_all_minds(
                Path(args.repo), progress_callback
            )

            print(f"\n{'='*60}")
            print("EVALUATION RESULTS")
            print(f"{'='*60}")
            print(f"Consensus Score: {result.consensus_score:.2f}")
            print(f"Weighted Score:  {result.weighted_average_score:.2f}")
            print(f"Score Variance:  {result.score_variance:.4f}")
            print(f"\nIndividual Results:")
            for name, res in result.individual_results.items():
                display = DISPLAY_NAMES.get(name, name)
                print(f"  {display:25} {res.get_grade()} ({res.overall_score:.2f})")

            print(f"\nUnanimous Findings:")
            for finding in result.unanimous_findings[:5]:
                print(f"  - {finding}")

        elif args.command == "full-pipeline":
            if not args.repo:
                parser.error("--repo is required for 'full-pipeline' command")

            print(f"\nRunning full evaluation pipeline on: {args.repo}")
            print(f"Output directory: {args.output}")

            result = await orchestrator.run_full_pipeline(
                Path(args.repo),
                mind_names=args.minds,
                progress_callback=progress_callback
            )

            print(f"\n{'='*60}")
            print("PIPELINE COMPLETE")
            print(f"{'='*60}")
            print(f"Final Grade: {result.final_grade}")
            print(f"Final Score: {result.final_score:.2f}")
            print(f"Duration:    {result.total_duration_seconds:.1f}s")
            print(f"Minds Used:  {len(result.minds_used)}")

            # Export results
            orchestrator.export_results(Path(args.output))
            print(f"\nResults exported to: {args.output}")

        elif args.command == "report":
            report = orchestrator.generate_session_report()
            print(report)

        # Save final checkpoint
        orchestrator.save_checkpoint()

    except OrchestratorError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted. Saving checkpoint...")
        orchestrator.save_checkpoint()
        sys.exit(130)


if __name__ == "__main__":
    asyncio.run(main())
