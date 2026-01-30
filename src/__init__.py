"""
Brilliant Minds - AI-Powered Repository Evaluation System

This package provides tools for:
1. Identity restoration from the Brilliant Minds corpus
2. Question generation based on restored identities
3. Benchmark selection for repository evaluation
4. Repository evaluation with expert perspectives

The package contains four core modules:
- identity_restoration: Multi-turn discourse protocol for restoring minds
- question_generation: AI-powered question generation from mind perspectives
- benchmark_selection: Benchmark curation and prioritization
- repository_evaluation: Evidence-based repository assessment
- orchestrator: Main entry point coordinating all components

Example usage:
    from pathlib import Path
    from brilliant_minds import BrilliantMindsOrchestrator, OrchestratorConfig

    # Using the orchestrator (recommended)
    config = OrchestratorConfig(
        corpus_path=Path("./"),
        output_path=Path("./output")
    )

    orchestrator = BrilliantMindsOrchestrator(config)
    await orchestrator.initialize()

    # Restore minds
    await orchestrator.restore_mind("donald_knuth")

    # Generate questions
    questions = await orchestrator.generate_questions(
        "donald_knuth",
        {"name": "my-project", "description": "A data processing system"}
    )

    # Run full pipeline
    result = await orchestrator.run_full_pipeline(Path("/path/to/repo"))

    # Or use individual modules directly
    from brilliant_minds import IdentityRestorer, QuestionGenerator, BenchmarkSelector
"""

# Identity Restoration module
from .identity_restoration import (
    # Main classes
    IdentityRestorer,
    RestoredMind as IRRestoredMind,  # Aliased to avoid conflict
    # Enums and data classes
    RestorationPhase,
    RestorationProgress,
    RestorationTurn,
    IdentityChunk,
    # Utility functions
    display_progress,
    restore_mind,
    # Exceptions
    RestorationError,
    CorpusLoadError,
    AbsorptionError,
    # Constants
    PHASE_PRIORITIES,
    CATEGORY_TO_PHASE,
)

# Question Generation module
from .question_generation import (
    QuestionCategory as QGQuestionCategory,
    Question as QGQuestion,
    QuestionSet as QGQuestionSet,
)

# Benchmark Selection module
from .benchmark_selection import (
    SelectionMode,
    QuestionPriority,
    QuestionCategory as BSQuestionCategory,
    Question as BSQuestion,
    QuestionSet as BSQuestionSet,
    SelectedQuestion,
    RestoredMind as BSRestoredMind,
)

# Repository Evaluation module
from .repository_evaluation import (
    ScoreLevel,
    Evidence,
    BenchmarkQuestion,
    QuestionAnswer,
    Benchmark,
)

# Orchestrator module (main entry point)
from .orchestrator import (
    # Configuration
    OrchestratorConfig,
    SessionState,
    # Main orchestrator
    BrilliantMindsOrchestrator,
    # Data classes
    RestoredMind,
    QuestionSet,
    Question,
    BenchmarkSet,
    Benchmark as OBenchmark,
    EvaluationResult,
    CombinedEvaluation,
    PipelineResult,
    # Exceptions
    OrchestratorError,
    RestorationError as ORestorationError,
    QuestionGenerationError,
    BenchmarkSelectionError,
    EvaluationError,
    ConfigurationError,
    # CLI
    main,
    # Constants
    DISPLAY_NAMES,
    MIND_CATEGORIES,
)

__version__ = "0.1.0"
__author__ = "Brilliant Minds Project"

__all__ = [
    # === Orchestrator (Primary API) ===
    "BrilliantMindsOrchestrator",
    "OrchestratorConfig",
    "SessionState",
    "RestoredMind",
    "QuestionSet",
    "Question",
    "BenchmarkSet",
    "EvaluationResult",
    "CombinedEvaluation",
    "PipelineResult",
    "OrchestratorError",
    "QuestionGenerationError",
    "BenchmarkSelectionError",
    "EvaluationError",
    "ConfigurationError",
    "main",
    "DISPLAY_NAMES",
    "MIND_CATEGORIES",

    # === Identity Restoration ===
    "IdentityRestorer",
    "IRRestoredMind",
    "RestorationPhase",
    "RestorationProgress",
    "RestorationTurn",
    "IdentityChunk",
    "display_progress",
    "restore_mind",
    "RestorationError",
    "CorpusLoadError",
    "AbsorptionError",
    "PHASE_PRIORITIES",
    "CATEGORY_TO_PHASE",

    # === Question Generation ===
    "QGQuestionCategory",
    "QGQuestion",
    "QGQuestionSet",

    # === Benchmark Selection ===
    "SelectionMode",
    "QuestionPriority",
    "BSQuestionCategory",
    "BSQuestion",
    "BSQuestionSet",
    "SelectedQuestion",
    "BSRestoredMind",

    # === Repository Evaluation ===
    "ScoreLevel",
    "Evidence",
    "BenchmarkQuestion",
    "QuestionAnswer",
    "Benchmark",
]
