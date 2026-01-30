# Brilliant Minds Orchestration System

## System Architecture Overview

The Brilliant Minds Orchestration System coordinates the complete lifecycle of identity restoration, question generation, benchmark selection, and repository evaluation. This document defines the interfaces, state management, and coordination protocols that unify all subsystems.

---

## 1. Pipeline Architecture

### 1.1 Complete System Flow

```
                                 BRILLIANT MINDS ORCHESTRATION SYSTEM
                                 ====================================

Phase 1: Identity Restoration
-----------------------------
+-------------------+     +----------------------+     +-------------------+
|   Identity        |     |    Identity          |     |    Restored       |
|   Corpus          | --> |    Restoration       | --> |    Mind           |
|   (IDENTITY.md)   |     |    Protocol          |     |    Agent          |
+-------------------+     +----------------------+     +--------+----------+
                                                               |
      +-----------------+                                      |
      |  Target Project |                                      |
      |  Metadata       |<-------------------------------------+
      +--------+--------+
               |
               v
Phase 2: Question Generation
----------------------------
+-------------------+     +----------------------+     +-------------------+
|    Target         |     |    Question          |     |    Question       |
|    Project        | --> |    Generation        | --> |    Bank           |
|    Analysis       |     |    Protocol          |     |    (15-30 Qs)     |
+-------------------+     +----------------------+     +--------+----------+
                                                               |
                                                               v
Phase 3: Benchmark Selection
----------------------------
+-------------------+     +----------------------+     +-------------------+
|    Question       |     |    Benchmark         |     |    Selected       |
|    Bank           | --> |    Selection         | --> |    Benchmark      |
|                   |     |    Protocol          |     |    Set (5-10 Qs)  |
+-------------------+     +----------------------+     +--------+----------+
                                                               |
                                                               v
Phase 4: Repository Evaluation
------------------------------
+-------------------+     +----------------------+     +-------------------+
|    Target         |     |    Repository        |     |    Evaluation     |
|    Repository     | --> |    Evaluation        | --> |    Report         |
|    Contents       |     |    Protocol          |     |                   |
+-------------------+     +----------------------+     +-------------------+
```

### 1.2 Data Flow Diagram

```
+-----------------------------------------------------------------------------+
|                           ORCHESTRATION LAYER                                |
+-----------------------------------------------------------------------------+
|                                                                             |
|  [Session Controller] <---> [State Manager] <---> [Persistence Layer]       |
|         |                         |                        |                |
|         v                         v                        v                |
|  +-------------+          +---------------+        +----------------+       |
|  | Progress    |          | Checkpoint    |        | Export         |       |
|  | Tracker     |          | Manager       |        | Manager        |       |
|  +-------------+          +---------------+        +----------------+       |
|                                                                             |
+-----------------------------------------------------------------------------+
         |                    |                    |                    |
         v                    v                    v                    v
+----------------+   +----------------+   +----------------+   +----------------+
|   Identity     |   |   Question     |   |   Benchmark    |   |   Repository   |
|   Restoration  |   |   Generation   |   |   Selection    |   |   Evaluation   |
|   Protocol     |   |   Protocol     |   |   Protocol     |   |   Protocol     |
+----------------+   +----------------+   +----------------+   +----------------+
```

---

## 2. Core Data Structures

### 2.1 Identity Corpus Schema

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

@dataclass
class IdentityCorpus:
    """Raw identity source material"""
    mind_name: str                           # e.g., "andrej_karpathy"
    display_name: str                        # e.g., "Andrej Karpathy"
    corpus_path: str                         # Path to IDENTITY.md

    # Parsed sections from IDENTITY.md
    core_identity: str                       # Core Identity Statement
    biographical_essence: Dict[str, Any]     # Birth, Education, Career
    intellectual_dna: Dict[str, Any]         # Domains, Contributions, Philosophy
    communication_patterns: Dict[str, Any]   # Voice, Phrases, Positions
    knowledge_benchmarks: Dict[str, List]    # Know Deeply, Moderately, Defer
    behavioral_traits: Dict[str, str]        # Problem-solving, Collaboration, etc.
    verification_questions: List[Dict]       # Q&A pairs for identity verification
    quotes: List[str]                        # Repository of authentic quotes

    # Metadata
    category: str                            # e.g., "AI Industry Leaders"
    word_count: int                          # Total corpus size
    section_count: int                       # Number of parsed sections
```

### 2.2 Restored Mind Agent

```python
class RestorationStage(Enum):
    INITIAL = "initial"
    CORE_ABSORBED = "core_absorbed"
    BIOGRAPHY_ABSORBED = "biography_absorbed"
    EXPERTISE_ABSORBED = "expertise_absorbed"
    VOICE_ABSORBED = "voice_absorbed"
    VERIFICATION_PASSED = "verification_passed"
    FULLY_RESTORED = "fully_restored"

@dataclass
class AbsorptionMetrics:
    """Quality metrics for identity restoration"""
    core_identity_clarity: float             # 0.0-1.0 clarity of core mission
    biographical_accuracy: float             # 0.0-1.0 factual accuracy
    expertise_calibration: float             # 0.0-1.0 correct domain confidence
    voice_authenticity: float                # 0.0-1.0 communication style match
    verification_score: float                # 0.0-1.0 passed verification questions

    @property
    def overall_quality(self) -> float:
        """Weighted average of all metrics"""
        weights = {
            'core_identity_clarity': 0.25,
            'biographical_accuracy': 0.15,
            'expertise_calibration': 0.25,
            'voice_authenticity': 0.20,
            'verification_score': 0.15
        }
        return sum(
            getattr(self, metric) * weight
            for metric, weight in weights.items()
        )

@dataclass
class RestoredMind:
    """A successfully restored identity agent"""
    mind_id: str                             # Unique session identifier
    corpus: IdentityCorpus                   # Source material

    # Restoration state
    stage: RestorationStage                  # Current restoration stage
    progress: float                          # 0.0-100.0 percentage
    absorption_turns: int                    # Number of absorption iterations

    # Quality metrics
    metrics: AbsorptionMetrics               # Absorption quality measurements

    # Behavioral state
    expertise_domains: Dict[str, float]      # Domain -> confidence mapping
    active_voice_patterns: List[str]         # Currently active communication patterns
    debate_positions: Dict[str, str]         # Position -> stance mapping

    # Session history
    conversation_history: List[Dict]         # Full conversation log
    restoration_log: List[str]               # Stage transition log

    def is_ready(self) -> bool:
        """Check if mind is ready for question generation"""
        return (
            self.stage == RestorationStage.FULLY_RESTORED and
            self.metrics.overall_quality >= 0.7
        )
```

### 2.3 Question Structures

```python
class QuestionCategory(Enum):
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    PHILOSOPHY = "philosophy"
    TRADEOFFS = "tradeoffs"
    PATTERNS = "patterns"
    TESTING = "testing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    SCALABILITY = "scalability"

class QuestionDifficulty(Enum):
    FOUNDATIONAL = "foundational"      # Basic understanding
    INTERMEDIATE = "intermediate"       # Applied knowledge
    ADVANCED = "advanced"              # Deep expertise
    EXPERT = "expert"                  # Novel insights required

@dataclass
class Question:
    """A question generated by a restored mind"""
    question_id: str                         # Unique identifier
    mind_id: str                             # Which mind generated this

    # Question content
    text: str                                # The question text
    category: QuestionCategory               # Classification
    difficulty: QuestionDifficulty           # Difficulty level

    # Rationale
    why_this_matters: str                    # Why the mind asks this
    expected_depth: str                      # What a good answer looks like
    expertise_domain: str                    # Which domain this tests

    # Scoring criteria
    rubric: Dict[str, str]                   # Scoring dimensions
    weight: float                            # Importance weight (0.0-1.0)

    # Metadata
    generated_at: datetime
    context_used: List[str]                  # Which project info informed this

@dataclass
class QuestionBank:
    """Collection of questions from one or more minds"""
    bank_id: str
    mind_ids: List[str]                      # Contributing minds
    questions: List[Question]

    # Statistics
    category_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, int]

    # Selection state
    selected_for_benchmark: List[str]        # Question IDs selected

    def get_by_category(self, category: QuestionCategory) -> List[Question]:
        return [q for q in self.questions if q.category == category]

    def get_by_difficulty(self, difficulty: QuestionDifficulty) -> List[Question]:
        return [q for q in self.questions if q.difficulty == difficulty]
```

### 2.4 Benchmark Set

```python
class BenchmarkMode(Enum):
    COMPREHENSIVE = "comprehensive"    # Cover all categories
    DEEP_DIVE = "deep_dive"           # Focus on specific areas
    QUICK_ASSESS = "quick_assess"     # Minimal critical questions
    CUSTOM = "custom"                 # User-selected questions

@dataclass
class BenchmarkSet:
    """Selected questions for repository evaluation"""
    benchmark_id: str
    source_bank: QuestionBank
    mode: BenchmarkMode

    # Selected questions
    questions: List[Question]
    selection_rationale: str               # Why these questions

    # Configuration
    time_limit_per_question: Optional[int]  # Seconds, None = unlimited
    require_evidence: bool                  # Must cite code
    allow_partial_credit: bool              # Partial scoring

    # Coverage analysis
    category_coverage: Dict[str, float]     # Category -> coverage %
    difficulty_balance: Dict[str, float]    # Difficulty -> proportion

    @property
    def total_weight(self) -> float:
        return sum(q.weight for q in self.questions)
```

### 2.5 Evaluation Results

```python
class EvidenceQuality(Enum):
    NO_EVIDENCE = "no_evidence"
    WEAK_EVIDENCE = "weak_evidence"
    ADEQUATE_EVIDENCE = "adequate_evidence"
    STRONG_EVIDENCE = "strong_evidence"

@dataclass
class QuestionEvaluation:
    """Evaluation of a repository against one question"""
    question: Question

    # Response
    response_text: str                      # The answer provided
    evidence_cited: List[str]               # File paths/code cited
    evidence_quality: EvidenceQuality

    # Scoring
    raw_score: float                        # 0.0-1.0
    weighted_score: float                   # raw_score * question.weight
    rubric_scores: Dict[str, float]         # Per-rubric-dimension scores

    # Mind's assessment
    mind_commentary: str                    # The mind's analysis
    strengths_identified: List[str]
    weaknesses_identified: List[str]
    suggestions: List[str]

    # Metadata
    evaluation_time: float                  # Seconds taken
    confidence: float                       # Mind's confidence in assessment

@dataclass
class EvaluationReport:
    """Complete evaluation of a repository"""
    report_id: str
    benchmark: BenchmarkSet
    repository_info: 'RepositoryInfo'

    # Results
    evaluations: List[QuestionEvaluation]

    # Aggregate scores
    total_score: float                      # Weighted average
    category_scores: Dict[str, float]       # Per-category averages
    difficulty_scores: Dict[str, float]     # Per-difficulty averages

    # Summary
    executive_summary: str                  # High-level findings
    key_strengths: List[str]
    key_weaknesses: List[str]
    recommendations: List[str]

    # Mind attribution
    evaluating_mind: str                    # Which mind performed evaluation
    confidence_in_report: float             # Mind's confidence

    # Metadata
    started_at: datetime
    completed_at: datetime

    @property
    def pass_fail(self) -> str:
        """Simple pass/fail based on configurable threshold"""
        threshold = 0.7  # Configurable
        return "PASS" if self.total_score >= threshold else "FAIL"
```

---

## 3. Session Management

### 3.1 Session Model

```python
@dataclass
class BrilliantMindSession:
    """Complete session state for a Brilliant Minds evaluation"""

    # Session identification
    session_id: str
    created_at: datetime
    last_active: datetime

    # Identity state
    identity_name: str                       # Target mind name
    restoration_progress: float              # 0-100%
    absorption_quality: float                # 0.0-1.0
    restored_mind: Optional[RestoredMind]

    # Project target
    target_project: Optional['ProjectInfo']
    target_repository: Optional['RepositoryInfo']

    # Generated content
    generated_questions: List[Question]
    question_bank: Optional[QuestionBank]

    # Benchmark state
    benchmark_mode: Optional[BenchmarkMode]
    selected_benchmarks: List[Question]
    benchmark_set: Optional[BenchmarkSet]

    # Evaluation state
    evaluation_progress: float               # 0-100%
    evaluations: List[QuestionEvaluation]
    evaluation_report: Optional[EvaluationReport]

    # Session configuration
    config: 'SessionConfig'

    # History and logging
    event_log: List['SessionEvent']
    checkpoints: List['SessionCheckpoint']

    def get_current_phase(self) -> str:
        """Determine current phase of the session"""
        if not self.restored_mind:
            return "identity_restoration"
        if not self.question_bank:
            return "question_generation"
        if not self.benchmark_set:
            return "benchmark_selection"
        if not self.evaluation_report:
            return "repository_evaluation"
        return "completed"

@dataclass
class SessionEvent:
    """Audit log entry for session"""
    timestamp: datetime
    event_type: str
    description: str
    data: Optional[Dict[str, Any]]

@dataclass
class SessionCheckpoint:
    """Saveable session state"""
    checkpoint_id: str
    session_id: str
    created_at: datetime
    phase: str
    state_snapshot: Dict[str, Any]
    file_path: str
```

### 3.2 Session Lifecycle

```python
class SessionState(Enum):
    INITIALIZING = "initializing"
    RESTORING_IDENTITY = "restoring_identity"
    GENERATING_QUESTIONS = "generating_questions"
    SELECTING_BENCHMARKS = "selecting_benchmarks"
    EVALUATING_REPOSITORY = "evaluating_repository"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"

class SessionLifecycle:
    """
    Session State Machine

    INITIALIZING
         |
         v
    RESTORING_IDENTITY -----> ERROR
         |                      ^
         v                      |
    GENERATING_QUESTIONS ------+
         |                      |
         v                      |
    SELECTING_BENCHMARKS ------+
         |                      |
         v                      |
    EVALUATING_REPOSITORY -----+
         |
         v
    COMPLETED

    Any state can transition to PAUSED and back.
    """

    VALID_TRANSITIONS = {
        SessionState.INITIALIZING: [SessionState.RESTORING_IDENTITY, SessionState.ERROR],
        SessionState.RESTORING_IDENTITY: [SessionState.GENERATING_QUESTIONS, SessionState.PAUSED, SessionState.ERROR],
        SessionState.GENERATING_QUESTIONS: [SessionState.SELECTING_BENCHMARKS, SessionState.PAUSED, SessionState.ERROR],
        SessionState.SELECTING_BENCHMARKS: [SessionState.EVALUATING_REPOSITORY, SessionState.PAUSED, SessionState.ERROR],
        SessionState.EVALUATING_REPOSITORY: [SessionState.COMPLETED, SessionState.PAUSED, SessionState.ERROR],
        SessionState.PAUSED: [
            SessionState.RESTORING_IDENTITY,
            SessionState.GENERATING_QUESTIONS,
            SessionState.SELECTING_BENCHMARKS,
            SessionState.EVALUATING_REPOSITORY,
        ],
        SessionState.COMPLETED: [],
        SessionState.ERROR: [SessionState.INITIALIZING],  # Can retry
    }
```

---

## 4. API Design

### 4.1 Core Protocol Interfaces

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

class IdentityRestorationProtocol(ABC):
    """Protocol for restoring a brilliant mind from corpus"""

    @abstractmethod
    async def restore_identity(
        self,
        mind_name: str,
        corpus_path: str,
        config: 'RestorationConfig'
    ) -> RestoredMind:
        """
        Restore a mind from identity corpus.

        Args:
            mind_name: Identifier for the mind (e.g., "andrej_karpathy")
            corpus_path: Path to IDENTITY.md file
            config: Restoration configuration

        Returns:
            RestoredMind agent ready for question generation

        Raises:
            RestorationError: If restoration fails quality threshold
            CorpusParseError: If corpus cannot be parsed
        """
        pass

    @abstractmethod
    async def stream_restoration(
        self,
        mind_name: str,
        corpus_path: str,
        config: 'RestorationConfig'
    ) -> AsyncIterator['RestorationProgress']:
        """Stream restoration progress for real-time UI updates"""
        pass

class QuestionGenerationProtocol(ABC):
    """Protocol for generating questions from a restored mind"""

    @abstractmethod
    async def generate_questions(
        self,
        mind: RestoredMind,
        project_info: 'ProjectInfo',
        config: 'QuestionConfig'
    ) -> QuestionBank:
        """
        Generate evaluation questions from the mind's perspective.

        Args:
            mind: A fully restored mind agent
            project_info: Information about the target project
            config: Question generation configuration

        Returns:
            QuestionBank containing 15-30 questions
        """
        pass

    @abstractmethod
    async def stream_questions(
        self,
        mind: RestoredMind,
        project_info: 'ProjectInfo',
        config: 'QuestionConfig'
    ) -> AsyncIterator[Question]:
        """Stream questions as they are generated"""
        pass

class BenchmarkSelectionProtocol(ABC):
    """Protocol for selecting benchmark questions"""

    @abstractmethod
    async def select_benchmarks(
        self,
        mind: RestoredMind,
        questions: QuestionBank,
        mode: BenchmarkMode,
        config: 'BenchmarkConfig'
    ) -> BenchmarkSet:
        """
        Select benchmark questions for evaluation.

        Args:
            mind: The mind that will use these benchmarks
            questions: Available questions to select from
            mode: Selection mode (comprehensive, deep_dive, etc.)
            config: Benchmark configuration

        Returns:
            BenchmarkSet of 5-10 selected questions
        """
        pass

class RepositoryEvaluationProtocol(ABC):
    """Protocol for evaluating a repository"""

    @abstractmethod
    async def evaluate_repository(
        self,
        mind: RestoredMind,
        repository: 'RepositoryInfo',
        benchmarks: BenchmarkSet,
        config: 'EvaluationConfig'
    ) -> EvaluationReport:
        """
        Evaluate a repository against benchmark questions.

        Args:
            mind: The mind performing evaluation
            repository: Repository to evaluate
            benchmarks: Questions to use for evaluation
            config: Evaluation configuration

        Returns:
            Complete evaluation report with scores and analysis
        """
        pass

    @abstractmethod
    async def stream_evaluation(
        self,
        mind: RestoredMind,
        repository: 'RepositoryInfo',
        benchmarks: BenchmarkSet,
        config: 'EvaluationConfig'
    ) -> AsyncIterator[QuestionEvaluation]:
        """Stream individual question evaluations"""
        pass
```

### 4.2 Orchestration API

```python
class BrilliantMindsOrchestrator:
    """Main orchestration interface"""

    def __init__(
        self,
        restoration_protocol: IdentityRestorationProtocol,
        question_protocol: QuestionGenerationProtocol,
        benchmark_protocol: BenchmarkSelectionProtocol,
        evaluation_protocol: RepositoryEvaluationProtocol,
        persistence: 'PersistenceManager',
        config: 'OrchestratorConfig'
    ):
        self.restoration = restoration_protocol
        self.questions = question_protocol
        self.benchmarks = benchmark_protocol
        self.evaluation = evaluation_protocol
        self.persistence = persistence
        self.config = config
        self._active_sessions: Dict[str, BrilliantMindSession] = {}

    # Session Management
    async def create_session(
        self,
        mind_name: str,
        config: Optional['SessionConfig'] = None
    ) -> BrilliantMindSession:
        """Create a new evaluation session"""
        pass

    async def resume_session(
        self,
        session_id: str
    ) -> BrilliantMindSession:
        """Resume a paused session from checkpoint"""
        pass

    async def pause_session(
        self,
        session_id: str
    ) -> SessionCheckpoint:
        """Pause session and create checkpoint"""
        pass

    # Full Pipeline Execution
    async def run_full_pipeline(
        self,
        mind_name: str,
        project_info: 'ProjectInfo',
        repository: 'RepositoryInfo',
        config: 'PipelineConfig'
    ) -> EvaluationReport:
        """Execute complete pipeline from identity to evaluation"""
        pass

    async def stream_pipeline(
        self,
        mind_name: str,
        project_info: 'ProjectInfo',
        repository: 'RepositoryInfo',
        config: 'PipelineConfig'
    ) -> AsyncIterator['PipelineProgress']:
        """Stream progress through entire pipeline"""
        pass

    # Individual Phase Execution
    async def restore_mind(
        self,
        session: BrilliantMindSession
    ) -> RestoredMind:
        """Execute identity restoration phase"""
        pass

    async def generate_questions(
        self,
        session: BrilliantMindSession
    ) -> QuestionBank:
        """Execute question generation phase"""
        pass

    async def select_benchmarks(
        self,
        session: BrilliantMindSession,
        mode: BenchmarkMode = BenchmarkMode.COMPREHENSIVE
    ) -> BenchmarkSet:
        """Execute benchmark selection phase"""
        pass

    async def evaluate_repository(
        self,
        session: BrilliantMindSession
    ) -> EvaluationReport:
        """Execute repository evaluation phase"""
        pass
```

### 4.3 Repository and Project Info

```python
@dataclass
class ProjectInfo:
    """Information about a target project for question generation"""
    name: str
    description: str
    domain: str                              # e.g., "web", "ml", "systems"
    languages: List[str]
    frameworks: List[str]
    repository_url: Optional[str]
    documentation_url: Optional[str]

    # Project characteristics
    size_category: str                       # "small", "medium", "large"
    maturity: str                            # "prototype", "production", "legacy"
    team_size: Optional[int]

    # Focus areas (optional, guides question generation)
    focus_areas: List[str]                   # e.g., ["security", "performance"]
    exclude_areas: List[str]                 # Areas to skip

@dataclass
class RepositoryInfo:
    """Information about a repository to evaluate"""
    path: str                                # Local path or URL
    name: str

    # Structure analysis
    file_tree: Dict[str, Any]                # Nested file structure
    file_count: int
    total_lines: int
    language_breakdown: Dict[str, int]       # Language -> line count

    # Key files
    readme_path: Optional[str]
    config_files: List[str]
    test_directories: List[str]
    documentation_directories: List[str]

    # Analysis results (populated during evaluation)
    indexed_files: Dict[str, str]            # Path -> content cache
    code_patterns: Dict[str, List[str]]      # Pattern type -> occurrences
```

---

## 5. Progress Tracking System

### 5.1 Progress Model

```python
@dataclass
class PhaseProgress:
    """Progress tracking for a single phase"""
    phase_name: str
    status: str                              # "pending", "active", "completed", "error"
    progress: float                          # 0-100
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    # Stage breakdown
    stages: List['StageProgress']
    current_stage: Optional[str]

    # Metrics
    items_total: Optional[int]
    items_completed: int = 0

    # Messages
    current_activity: str = ""
    last_message: str = ""
    errors: List[str] = field(default_factory=list)

@dataclass
class StageProgress:
    """Progress for a stage within a phase"""
    stage_name: str
    weight: float                            # Contribution to phase progress
    progress: float                          # 0-100
    status: str

@dataclass
class PipelineProgress:
    """Overall pipeline progress"""
    session_id: str
    overall_progress: float                  # 0-100
    current_phase: str

    phases: Dict[str, PhaseProgress]

    # Timing
    started_at: datetime
    estimated_completion: Optional[datetime]
    elapsed_seconds: float

    # Quality metrics
    current_quality: Optional[float]
    quality_trend: List[float]               # History of quality readings
```

### 5.2 Progress Display Specifications

```
IDENTITY RESTORATION PROGRESS
=============================

Mind: Andrej Karpathy
Stage: EXPERTISE_ABSORBED (4/6)

[################............] 62%

Current Activity: Absorbing communication patterns...

Stages:
  [x] Initial parsing                    100%
  [x] Core identity absorption           100%
  [x] Biographical integration           100%
  [x] Expertise calibration              100%
  [ ] Voice pattern learning              45%
  [ ] Verification testing                 0%

Quality Metrics:
  Core Identity Clarity:    0.92
  Biographical Accuracy:    0.88
  Expertise Calibration:    0.85
  Voice Authenticity:       0.67
  Verification Score:       ---

Overall Absorption Quality: 0.83

Time Elapsed: 2m 34s
Est. Remaining: 1m 45s
```

```
QUESTION GENERATION PROGRESS
============================

Mind: Andrej Karpathy
Target: mercenary-cli

[####################........] 67%

Questions Generated: 20/30

By Category:
  Architecture:     [####....] 4/6
  Implementation:   [######..] 6/8
  Philosophy:       [####....] 3/5
  Tradeoffs:        [##......] 2/6
  Patterns:         [#####...] 5/5

By Difficulty:
  Foundational:     5 questions
  Intermediate:     8 questions
  Advanced:         5 questions
  Expert:           2 questions

Current: Generating tradeoff question #3...
```

```
REPOSITORY EVALUATION PROGRESS
==============================

Mind: Andrej Karpathy
Repository: mercenary-cli
Benchmark: COMPREHENSIVE (8 questions)

[########################....] 75%

Questions Evaluated: 6/8

Scores So Far:
  Q1 (Architecture):    0.85  [Strong Evidence]
  Q2 (Implementation):  0.72  [Adequate Evidence]
  Q3 (Philosophy):      0.91  [Strong Evidence]
  Q4 (Tradeoffs):       0.68  [Adequate Evidence]
  Q5 (Patterns):        0.78  [Adequate Evidence]
  Q6 (Testing):         0.55  [Weak Evidence]
  Q7 (Performance):     --- evaluating ---
  Q8 (Security):        --- pending ---

Running Total: 0.75 (weighted)

Current: Evaluating Q7 - Performance optimization strategies...
```

### 5.3 Progress Tracker Implementation

```python
class ProgressTracker:
    """Real-time progress tracking with event emission"""

    def __init__(self, session: BrilliantMindSession):
        self.session = session
        self._listeners: List[Callable] = []
        self._phase_progress: Dict[str, PhaseProgress] = {}
        self._initialize_phases()

    def _initialize_phases(self):
        """Set up progress tracking for all phases"""
        self._phase_progress = {
            'identity_restoration': PhaseProgress(
                phase_name='Identity Restoration',
                status='pending',
                progress=0.0,
                stages=[
                    StageProgress('parsing', 0.10, 0.0, 'pending'),
                    StageProgress('core_identity', 0.20, 0.0, 'pending'),
                    StageProgress('biography', 0.15, 0.0, 'pending'),
                    StageProgress('expertise', 0.20, 0.0, 'pending'),
                    StageProgress('voice', 0.20, 0.0, 'pending'),
                    StageProgress('verification', 0.15, 0.0, 'pending'),
                ]
            ),
            'question_generation': PhaseProgress(
                phase_name='Question Generation',
                status='pending',
                progress=0.0,
                stages=[
                    StageProgress('project_analysis', 0.20, 0.0, 'pending'),
                    StageProgress('question_ideation', 0.50, 0.0, 'pending'),
                    StageProgress('question_refinement', 0.30, 0.0, 'pending'),
                ]
            ),
            'benchmark_selection': PhaseProgress(
                phase_name='Benchmark Selection',
                status='pending',
                progress=0.0,
                stages=[
                    StageProgress('coverage_analysis', 0.30, 0.0, 'pending'),
                    StageProgress('selection', 0.50, 0.0, 'pending'),
                    StageProgress('validation', 0.20, 0.0, 'pending'),
                ]
            ),
            'repository_evaluation': PhaseProgress(
                phase_name='Repository Evaluation',
                status='pending',
                progress=0.0,
                stages=[]  # Dynamic based on question count
            ),
        }

    def subscribe(self, listener: Callable[[PipelineProgress], None]):
        """Subscribe to progress updates"""
        self._listeners.append(listener)

    def update_phase(
        self,
        phase: str,
        progress: float,
        stage: Optional[str] = None,
        message: str = ""
    ):
        """Update progress for a phase"""
        if phase in self._phase_progress:
            pp = self._phase_progress[phase]
            pp.progress = progress
            pp.current_activity = message
            if stage:
                pp.current_stage = stage
            self._emit_progress()

    def _emit_progress(self):
        """Emit current progress to all listeners"""
        progress = self._calculate_pipeline_progress()
        for listener in self._listeners:
            listener(progress)

    def _calculate_pipeline_progress(self) -> PipelineProgress:
        """Calculate overall pipeline progress"""
        phase_weights = {
            'identity_restoration': 0.30,
            'question_generation': 0.25,
            'benchmark_selection': 0.10,
            'repository_evaluation': 0.35,
        }

        overall = sum(
            self._phase_progress[phase].progress * weight
            for phase, weight in phase_weights.items()
        )

        current_phase = next(
            (phase for phase, pp in self._phase_progress.items()
             if pp.status == 'active'),
            'completed'
        )

        return PipelineProgress(
            session_id=self.session.session_id,
            overall_progress=overall,
            current_phase=current_phase,
            phases=self._phase_progress,
            started_at=self.session.created_at,
            estimated_completion=self._estimate_completion(),
            elapsed_seconds=(datetime.now() - self.session.created_at).total_seconds()
        )
```

---

## 6. Multi-Mind Coordination

### 6.1 Parallel Restoration

```python
@dataclass
class MultiMindSession:
    """Session for coordinating multiple minds"""
    session_id: str
    mind_names: List[str]

    # Individual mind states
    minds: Dict[str, RestoredMind]
    restoration_progress: Dict[str, float]

    # Aggregated results
    aggregated_questions: QuestionBank
    aggregated_benchmarks: BenchmarkSet
    aggregated_report: Optional['AggregatedReport']

    # Coordination state
    consensus_mode: 'ConsensusMode'
    voting_results: Dict[str, Dict]

class ConsensusMode(Enum):
    UNANIMOUS = "unanimous"           # All minds must agree
    MAJORITY = "majority"             # >50% agreement
    WEIGHTED = "weighted"             # Weight by expertise
    UNION = "union"                   # Include all unique perspectives

class MultiMindOrchestrator:
    """Orchestrate multiple minds in parallel"""

    async def restore_minds_parallel(
        self,
        mind_names: List[str],
        config: 'MultiMindConfig'
    ) -> Dict[str, RestoredMind]:
        """
        Restore multiple minds in parallel.

        Example:
            minds = await orchestrator.restore_minds_parallel([
                "andrej_karpathy",
                "linus_torvalds",
                "donald_knuth"
            ])
        """
        tasks = [
            self._restore_single_mind(name, config)
            for name in mind_names
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        minds = {}
        for name, result in zip(mind_names, results):
            if isinstance(result, Exception):
                self._handle_restoration_error(name, result)
            else:
                minds[name] = result

        return minds

    async def generate_questions_parallel(
        self,
        minds: Dict[str, RestoredMind],
        project_info: ProjectInfo,
        config: 'QuestionConfig'
    ) -> Dict[str, QuestionBank]:
        """Generate questions from all minds in parallel"""
        tasks = {
            name: self.questions.generate_questions(mind, project_info, config)
            for name, mind in minds.items()
        }

        results = await asyncio.gather(*tasks.values())
        return dict(zip(tasks.keys(), results))

    def aggregate_questions(
        self,
        question_banks: Dict[str, QuestionBank],
        mode: ConsensusMode = ConsensusMode.UNION
    ) -> QuestionBank:
        """
        Aggregate questions from multiple minds.

        Modes:
        - UNION: Include all unique questions
        - MAJORITY: Include questions similar minds asked
        - WEIGHTED: Weight by mind expertise in relevant domain
        """
        if mode == ConsensusMode.UNION:
            return self._union_aggregate(question_banks)
        elif mode == ConsensusMode.MAJORITY:
            return self._majority_aggregate(question_banks)
        elif mode == ConsensusMode.WEIGHTED:
            return self._weighted_aggregate(question_banks)

    async def collaborative_evaluation(
        self,
        minds: Dict[str, RestoredMind],
        repository: RepositoryInfo,
        benchmarks: BenchmarkSet,
        config: 'EvaluationConfig'
    ) -> 'AggregatedReport':
        """
        Each mind evaluates the repository, then aggregate results.

        This provides:
        - Multiple perspectives on the same questions
        - Cross-validation of findings
        - Richer analysis from diverse expertise
        """
        # Each mind evaluates
        evaluations = await asyncio.gather(*[
            self.evaluation.evaluate_repository(mind, repository, benchmarks, config)
            for mind in minds.values()
        ])

        # Aggregate results
        return self._aggregate_reports(
            dict(zip(minds.keys(), evaluations)),
            config.consensus_mode
        )
```

### 6.2 Aggregated Reporting

```python
@dataclass
class AggregatedReport:
    """Evaluation report from multiple minds"""
    report_id: str
    minds_participated: List[str]
    consensus_mode: ConsensusMode

    # Individual reports
    mind_reports: Dict[str, EvaluationReport]

    # Aggregated scores
    consensus_score: float
    score_variance: float
    score_by_mind: Dict[str, float]

    # Cross-mind analysis
    areas_of_agreement: List[str]
    areas_of_disagreement: List[str]
    unique_insights: Dict[str, List[str]]     # Mind -> unique observations

    # Final synthesis
    synthesized_summary: str
    synthesized_recommendations: List[str]
    confidence_level: str                      # "high", "medium", "low"
```

---

## 7. Persistence Layer

### 7.1 Checkpoint Format

```python
@dataclass
class CheckpointSchema:
    """Schema for session checkpoints"""
    version: str = "1.0"

    # Session identification
    session_id: str
    created_at: str                           # ISO 8601
    checkpoint_at: str                        # ISO 8601

    # Session state
    state: str                                # SessionState value
    current_phase: str

    # Identity state
    mind_name: str
    restoration_stage: str
    restoration_progress: float
    absorption_metrics: Dict[str, float]

    # Generated content
    questions: List[Dict]                     # Serialized questions
    selected_benchmarks: List[str]            # Question IDs

    # Evaluation state
    evaluations_completed: List[Dict]         # Serialized evaluations
    evaluation_progress: float

    # Configuration
    config: Dict[str, Any]

class PersistenceManager:
    """Manage session persistence"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        session: BrilliantMindSession
    ) -> SessionCheckpoint:
        """Save session state to checkpoint file"""
        checkpoint_id = f"{session.session_id}_{datetime.now().isoformat()}"
        file_path = self.storage_path / f"{checkpoint_id}.json"

        schema = self._serialize_session(session)

        with open(file_path, 'w') as f:
            json.dump(asdict(schema), f, indent=2, default=str)

        return SessionCheckpoint(
            checkpoint_id=checkpoint_id,
            session_id=session.session_id,
            created_at=datetime.now(),
            phase=session.get_current_phase(),
            state_snapshot=asdict(schema),
            file_path=str(file_path)
        )

    def load_checkpoint(
        self,
        checkpoint_id: str
    ) -> BrilliantMindSession:
        """Load session from checkpoint"""
        file_path = self.storage_path / f"{checkpoint_id}.json"

        with open(file_path, 'r') as f:
            data = json.load(f)

        return self._deserialize_session(data)

    def list_checkpoints(
        self,
        session_id: Optional[str] = None
    ) -> List[SessionCheckpoint]:
        """List available checkpoints"""
        checkpoints = []
        for file_path in self.storage_path.glob("*.json"):
            with open(file_path, 'r') as f:
                data = json.load(f)

            if session_id and data['session_id'] != session_id:
                continue

            checkpoints.append(SessionCheckpoint(
                checkpoint_id=file_path.stem,
                session_id=data['session_id'],
                created_at=datetime.fromisoformat(data['checkpoint_at']),
                phase=data['current_phase'],
                state_snapshot=data,
                file_path=str(file_path)
            ))

        return sorted(checkpoints, key=lambda c: c.created_at, reverse=True)

    def auto_checkpoint(
        self,
        session: BrilliantMindSession,
        interval_minutes: int = 5
    ):
        """Set up automatic checkpointing"""
        # Implementation: background task that saves periodically
        pass
```

### 7.2 Export Formats

```python
class ExportFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"

class ExportManager:
    """Export session results in various formats"""

    def export_report(
        self,
        report: EvaluationReport,
        format: ExportFormat,
        output_path: str
    ) -> str:
        """Export evaluation report"""
        if format == ExportFormat.JSON:
            return self._export_json(report, output_path)
        elif format == ExportFormat.MARKDOWN:
            return self._export_markdown(report, output_path)
        elif format == ExportFormat.HTML:
            return self._export_html(report, output_path)
        # ... other formats

    def _export_markdown(
        self,
        report: EvaluationReport,
        output_path: str
    ) -> str:
        """Export as Markdown document"""
        md = f"""# Evaluation Report

## Summary

**Repository**: {report.repository_info.name}
**Evaluating Mind**: {report.evaluating_mind}
**Overall Score**: {report.total_score:.2f}
**Result**: {report.pass_fail}

## Executive Summary

{report.executive_summary}

## Key Findings

### Strengths
{self._format_list(report.key_strengths)}

### Weaknesses
{self._format_list(report.key_weaknesses)}

## Detailed Evaluations

"""
        for eval in report.evaluations:
            md += f"""### {eval.question.category.value.title()}: {eval.question.text[:50]}...

**Score**: {eval.raw_score:.2f}
**Evidence Quality**: {eval.evidence_quality.value}

{eval.mind_commentary}

---

"""

        md += f"""## Recommendations

{self._format_list(report.recommendations)}
"""

        with open(output_path, 'w') as f:
            f.write(md)

        return output_path
```

---

## 8. Configuration System

### 8.1 Master Configuration Schema

```yaml
# brilliant_minds_config.yaml

# System-wide settings
system:
  log_level: "INFO"
  storage_path: "./sessions"
  checkpoint_interval_minutes: 5
  max_concurrent_minds: 4

# Identity restoration settings
restoration:
  # Chunking for large corpora
  chunk_size: 500                    # Max tokens per absorption turn
  max_chunks_per_stage: 10           # Max iterations per stage

  # Quality thresholds
  min_absorption_quality: 0.70       # Minimum to proceed
  target_absorption_quality: 0.85    # Target quality

  # Verification
  verification_questions_required: 5  # Min verification Qs to pass
  verification_pass_threshold: 0.80   # Min correct answers

  # Limits
  max_turns: 15                       # Max conversation turns
  timeout_minutes: 10                 # Max time per restoration

# Question generation settings
question_generation:
  # Quantity
  min_questions: 15
  max_questions: 30
  target_questions: 20

  # Distribution targets (percentages)
  category_distribution:
    architecture: 0.20
    implementation: 0.20
    philosophy: 0.10
    tradeoffs: 0.15
    patterns: 0.15
    testing: 0.10
    performance: 0.05
    security: 0.05

  difficulty_distribution:
    foundational: 0.20
    intermediate: 0.40
    advanced: 0.30
    expert: 0.10

  # Quality
  require_rationale: true
  require_rubric: true

  # Timeouts
  timeout_minutes: 15

# Benchmark selection settings
benchmark_selection:
  # Mode configurations
  comprehensive:
    min_questions: 8
    max_questions: 12
    require_all_categories: true
    difficulty_balance: true

  deep_dive:
    min_questions: 5
    max_questions: 8
    focus_categories: []             # Set dynamically
    min_advanced_ratio: 0.50

  quick_assess:
    questions: 5
    priority_categories:
      - architecture
      - implementation
      - security

# Repository evaluation settings
evaluation:
  # Scoring
  scoring_rubric: "standard"          # or "strict", "lenient"
  require_evidence: true
  min_evidence_quality: "adequate"
  allow_partial_credit: true

  # Weights
  evidence_weight: 0.30
  completeness_weight: 0.40
  depth_weight: 0.30

  # Thresholds
  pass_threshold: 0.70
  excellence_threshold: 0.90

  # Limits
  max_file_size_kb: 500              # Skip files larger than this
  max_files_to_index: 1000
  timeout_per_question_minutes: 5

# Multi-mind settings
multi_mind:
  default_consensus_mode: "weighted"
  min_agreement_threshold: 0.60
  aggregate_unique_insights: true
  cross_validate_findings: true

# Progress tracking settings
progress:
  emit_interval_ms: 500
  show_quality_metrics: true
  show_time_estimates: true

# Export settings
export:
  default_format: "markdown"
  include_raw_data: false
  include_conversation_logs: false
```

### 8.2 Configuration Classes

```python
@dataclass
class RestorationConfig:
    """Configuration for identity restoration"""
    chunk_size: int = 500
    max_chunks_per_stage: int = 10
    min_absorption_quality: float = 0.70
    target_absorption_quality: float = 0.85
    verification_questions_required: int = 5
    verification_pass_threshold: float = 0.80
    max_turns: int = 15
    timeout_minutes: int = 10

@dataclass
class QuestionConfig:
    """Configuration for question generation"""
    min_questions: int = 15
    max_questions: int = 30
    target_questions: int = 20
    category_distribution: Dict[str, float] = field(default_factory=dict)
    difficulty_distribution: Dict[str, float] = field(default_factory=dict)
    require_rationale: bool = True
    require_rubric: bool = True
    timeout_minutes: int = 15

@dataclass
class BenchmarkConfig:
    """Configuration for benchmark selection"""
    mode: BenchmarkMode = BenchmarkMode.COMPREHENSIVE
    min_questions: int = 5
    max_questions: int = 12
    require_all_categories: bool = True
    focus_categories: List[str] = field(default_factory=list)

@dataclass
class EvaluationConfig:
    """Configuration for repository evaluation"""
    scoring_rubric: str = "standard"
    require_evidence: bool = True
    min_evidence_quality: str = "adequate"
    allow_partial_credit: bool = True
    pass_threshold: float = 0.70
    max_file_size_kb: int = 500
    max_files_to_index: int = 1000
    timeout_per_question_minutes: int = 5

@dataclass
class SessionConfig:
    """Configuration for a session"""
    restoration: RestorationConfig = field(default_factory=RestorationConfig)
    questions: QuestionConfig = field(default_factory=QuestionConfig)
    benchmarks: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)

    @classmethod
    def from_yaml(cls, path: str) -> 'SessionConfig':
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(
            restoration=RestorationConfig(**data.get('restoration', {})),
            questions=QuestionConfig(**data.get('question_generation', {})),
            benchmarks=BenchmarkConfig(**data.get('benchmark_selection', {})),
            evaluation=EvaluationConfig(**data.get('evaluation', {})),
        )
```

---

## 9. Error Handling

### 9.1 Exception Hierarchy

```python
class BrilliantMindsError(Exception):
    """Base exception for all Brilliant Minds errors"""
    pass

# Identity Restoration Errors
class RestorationError(BrilliantMindsError):
    """Error during identity restoration"""
    pass

class CorpusParseError(RestorationError):
    """Failed to parse identity corpus"""
    pass

class AbsorptionQualityError(RestorationError):
    """Absorption quality below threshold"""
    def __init__(self, quality: float, threshold: float):
        self.quality = quality
        self.threshold = threshold
        super().__init__(
            f"Absorption quality {quality:.2f} below threshold {threshold:.2f}"
        )

class VerificationFailedError(RestorationError):
    """Identity verification failed"""
    def __init__(self, score: float, required: float):
        self.score = score
        self.required = required
        super().__init__(
            f"Verification score {score:.2f} below required {required:.2f}"
        )

# Question Generation Errors
class QuestionGenerationError(BrilliantMindsError):
    """Error during question generation"""
    pass

class InsufficientQuestionsError(QuestionGenerationError):
    """Not enough questions generated"""
    pass

class CategoryImbalanceError(QuestionGenerationError):
    """Question categories too imbalanced"""
    pass

# Evaluation Errors
class EvaluationError(BrilliantMindsError):
    """Error during repository evaluation"""
    pass

class RepositoryAccessError(EvaluationError):
    """Cannot access repository"""
    pass

class EvidenceNotFoundError(EvaluationError):
    """Required evidence not found in repository"""
    pass

# Session Errors
class SessionError(BrilliantMindsError):
    """Error in session management"""
    pass

class InvalidStateTransitionError(SessionError):
    """Invalid session state transition attempted"""
    pass

class CheckpointNotFoundError(SessionError):
    """Checkpoint file not found"""
    pass
```

### 9.2 Error Recovery Strategies

```python
class ErrorRecovery:
    """Error recovery strategies for the orchestration system"""

    @staticmethod
    async def handle_restoration_error(
        error: RestorationError,
        session: BrilliantMindSession,
        orchestrator: BrilliantMindsOrchestrator
    ) -> RestoredMind:
        """Attempt to recover from restoration errors"""

        if isinstance(error, AbsorptionQualityError):
            # Try additional absorption iterations
            if session.restored_mind and session.restored_mind.absorption_turns < 15:
                return await orchestrator._continue_absorption(session)
            else:
                # Fallback to lower quality threshold
                session.config.restoration.min_absorption_quality *= 0.9
                return await orchestrator.restore_mind(session)

        elif isinstance(error, VerificationFailedError):
            # Try different verification questions
            return await orchestrator._retry_verification(session)

        elif isinstance(error, CorpusParseError):
            # Cannot recover - corpus is invalid
            raise error

        raise error

    @staticmethod
    async def handle_evaluation_error(
        error: EvaluationError,
        session: BrilliantMindSession,
        question: Question
    ) -> QuestionEvaluation:
        """Attempt to recover from evaluation errors"""

        if isinstance(error, RepositoryAccessError):
            # Skip this question, mark as unable to evaluate
            return QuestionEvaluation(
                question=question,
                response_text="Unable to access repository for evaluation",
                evidence_cited=[],
                evidence_quality=EvidenceQuality.NO_EVIDENCE,
                raw_score=0.0,
                weighted_score=0.0,
                rubric_scores={},
                mind_commentary="Evaluation skipped due to repository access error",
                strengths_identified=[],
                weaknesses_identified=["Could not access repository"],
                suggestions=["Ensure repository is accessible"],
                evaluation_time=0.0,
                confidence=0.0
            )

        raise error
```

---

## 10. Integration Hooks

### 10.1 Event System

```python
from typing import Callable, Awaitable

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]

class EventType(Enum):
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_PAUSED = "session.paused"
    SESSION_RESUMED = "session.resumed"
    SESSION_COMPLETED = "session.completed"
    SESSION_ERROR = "session.error"

    # Restoration events
    RESTORATION_STARTED = "restoration.started"
    RESTORATION_STAGE_COMPLETE = "restoration.stage_complete"
    RESTORATION_COMPLETE = "restoration.complete"
    RESTORATION_FAILED = "restoration.failed"

    # Question events
    QUESTIONS_STARTED = "questions.started"
    QUESTION_GENERATED = "questions.generated"
    QUESTIONS_COMPLETE = "questions.complete"

    # Benchmark events
    BENCHMARKS_SELECTED = "benchmarks.selected"

    # Evaluation events
    EVALUATION_STARTED = "evaluation.started"
    QUESTION_EVALUATED = "evaluation.question_evaluated"
    EVALUATION_COMPLETE = "evaluation.complete"

    # Progress events
    PROGRESS_UPDATE = "progress.update"
    CHECKPOINT_SAVED = "checkpoint.saved"

class EventBus:
    """Central event bus for system integration"""

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler
    ):
        """Subscribe to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any]
    ):
        """Emit an event to all subscribers"""
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler({
                    'type': event_type.value,
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                })
```

### 10.2 Integration Examples

```python
# CLI Integration
async def cli_progress_handler(event: Dict):
    """Handle progress events for CLI display"""
    if event['type'] == 'progress.update':
        progress = event['data']['progress']
        print(f"\r[{'#' * int(progress/10)}{' ' * (10 - int(progress/10))}] {progress:.0f}%", end='')

# Web API Integration
async def api_event_handler(event: Dict):
    """Forward events to WebSocket clients"""
    await websocket_manager.broadcast(json.dumps(event))

# Logging Integration
async def logging_handler(event: Dict):
    """Log all events for audit trail"""
    logger.info(f"{event['type']}: {event['data']}")

# Usage
event_bus = EventBus()
event_bus.subscribe(EventType.PROGRESS_UPDATE, cli_progress_handler)
event_bus.subscribe(EventType.SESSION_COMPLETED, api_event_handler)
event_bus.subscribe(EventType.SESSION_ERROR, logging_handler)
```

---

## 11. Usage Examples

### 11.1 Basic Usage

```python
import asyncio
from brilliant_minds import BrilliantMindsOrchestrator, SessionConfig

async def evaluate_repository():
    # Initialize orchestrator
    orchestrator = BrilliantMindsOrchestrator.from_config("config.yaml")

    # Create session
    session = await orchestrator.create_session(
        mind_name="andrej_karpathy"
    )

    # Run full pipeline
    report = await orchestrator.run_full_pipeline(
        mind_name="andrej_karpathy",
        project_info=ProjectInfo(
            name="mercenary-cli",
            description="Strategic command center for contractors",
            domain="cli",
            languages=["Go", "Rust"],
            frameworks=["Cobra", "Tauri"]
        ),
        repository=RepositoryInfo(
            path="/path/to/mercenary",
            name="mercenary"
        ),
        config=SessionConfig()
    )

    # Export report
    orchestrator.export_report(report, ExportFormat.MARKDOWN, "report.md")

    print(f"Score: {report.total_score:.2f} ({report.pass_fail})")

asyncio.run(evaluate_repository())
```

### 11.2 Multi-Mind Evaluation

```python
async def multi_mind_evaluation():
    orchestrator = MultiMindOrchestrator.from_config("config.yaml")

    # Restore multiple minds in parallel
    minds = await orchestrator.restore_minds_parallel([
        "andrej_karpathy",    # AI/ML perspective
        "linus_torvalds",     # Systems programming perspective
        "donald_knuth",       # Algorithmic perspective
    ])

    # Generate questions from each
    question_banks = await orchestrator.generate_questions_parallel(
        minds=minds,
        project_info=project_info,
        config=QuestionConfig()
    )

    # Aggregate questions
    aggregated = orchestrator.aggregate_questions(
        question_banks,
        mode=ConsensusMode.WEIGHTED
    )

    # Collaborative evaluation
    report = await orchestrator.collaborative_evaluation(
        minds=minds,
        repository=repository,
        benchmarks=BenchmarkSet.from_questions(aggregated.questions[:10]),
        config=EvaluationConfig()
    )

    print(f"Consensus Score: {report.consensus_score:.2f}")
    print(f"Score Variance: {report.score_variance:.2f}")

asyncio.run(multi_mind_evaluation())
```

### 11.3 Streaming Progress

```python
async def evaluate_with_progress():
    orchestrator = BrilliantMindsOrchestrator.from_config("config.yaml")

    async for progress in orchestrator.stream_pipeline(
        mind_name="geoffrey_hinton",
        project_info=project_info,
        repository=repository,
        config=SessionConfig()
    ):
        # Clear screen and redraw
        print("\033c", end="")
        print(f"""
BRILLIANT MINDS EVALUATION
==========================

Overall Progress: [{('#' * int(progress.overall_progress/5)):<20}] {progress.overall_progress:.0f}%

Current Phase: {progress.current_phase}

Phase Progress:
  Identity Restoration:  {progress.phases['identity_restoration'].progress:>5.1f}%
  Question Generation:   {progress.phases['question_generation'].progress:>5.1f}%
  Benchmark Selection:   {progress.phases['benchmark_selection'].progress:>5.1f}%
  Repository Evaluation: {progress.phases['repository_evaluation'].progress:>5.1f}%

Elapsed: {progress.elapsed_seconds:.0f}s
""")
        await asyncio.sleep(0.1)  # Throttle updates

asyncio.run(evaluate_with_progress())
```

---

## 12. System Diagram Summary

```
+===========================================================================+
|                     BRILLIANT MINDS ORCHESTRATION SYSTEM                   |
+===========================================================================+

                              +-------------------+
                              |    USER / CLI     |
                              +--------+----------+
                                       |
                                       v
                              +-------------------+
                              | ORCHESTRATOR API  |
                              +--------+----------+
                                       |
            +------------+-------------+-------------+------------+
            |            |             |             |            |
            v            v             v             v            v
     +-----------+ +-----------+ +-----------+ +-----------+ +-----------+
     | Session   | | Progress  | | Persist.  | | Event     | | Export    |
     | Manager   | | Tracker   | | Manager   | | Bus       | | Manager   |
     +-----------+ +-----------+ +-----------+ +-----------+ +-----------+
            |            |             |             |            |
            +------------+-------------+-------------+------------+
                                       |
                                       v
                    +------------------+------------------+
                    |                                     |
                    v                                     v
          +-------------------+               +-------------------+
          | SINGLE MIND       |               | MULTI-MIND        |
          | PIPELINE          |               | COORDINATOR       |
          +-------------------+               +-------------------+
                    |                                     |
    +---------------+---------------+           +---------+---------+
    |       |       |       |       |           |                   |
    v       v       v       v       v           v                   v
+-------+-------+-------+-------+-------+ +-------+           +-------+
|Restore|Gen Qs |Select |Eval   |Report | |Parallel|           |Aggreg.|
|Mind   |       |Bench  |Repo   |       | |Restore|           |Results|
+-------+-------+-------+-------+-------+ +-------+           +-------+

                    IDENTITY CORPUS LAYER
          +------------------------------------+
          | alan_turing/IDENTITY.md            |
          | andrej_karpathy/IDENTITY.md        |
          | geoffrey_hinton/IDENTITY.md        |
          | donald_knuth/IDENTITY.md           |
          | linus_torvalds/IDENTITY.md         |
          | ... (25 brilliant minds)           |
          +------------------------------------+

                    PROTOCOL LAYER
          +------------------------------------+
          | protocols/identity_restoration/    |
          | protocols/question_generation/     |
          | protocols/benchmark_selection/     |
          | protocols/repository_evaluation/   |
          +------------------------------------+
```

---

## Appendix A: File Structure

```
brilliant_minds/
+-- protocols/
|   +-- orchestration/
|   |   +-- SYSTEM.md              # This document
|   +-- identity_restoration/
|   |   +-- PROTOCOL.md
|   +-- question_generation/
|   |   +-- PROTOCOL.md
|   +-- benchmark_selection/
|   |   +-- PROTOCOL.md
|   +-- repository_evaluation/
|       +-- PROTOCOL.md
|
+-- [mind_name]/
|   +-- IDENTITY.md                # Identity corpus
|   +-- 01_overview.md             # Additional documents
|   +-- 02_technical_contributions.md
|
+-- sessions/                      # Checkpoint storage
|   +-- [session_id]_[timestamp].json
|
+-- config/
|   +-- default.yaml               # Default configuration
|
+-- exports/                       # Generated reports
    +-- [report_id].md
    +-- [report_id].html
    +-- [report_id].json
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Identity Corpus** | The IDENTITY.md file containing comprehensive information about a brilliant mind |
| **Restored Mind** | An AI agent that has absorbed an identity corpus and can think/respond as that person |
| **Absorption Quality** | Metric measuring how well the identity has been internalized (0.0-1.0) |
| **Question Bank** | Collection of questions generated by a restored mind for a target project |
| **Benchmark Set** | Selected subset of questions used for actual evaluation |
| **Evaluation Report** | Complete assessment of a repository against benchmark questions |
| **Multi-Mind Session** | Session using multiple restored minds for diverse perspectives |
| **Consensus Mode** | Strategy for aggregating results from multiple minds |
| **Checkpoint** | Saved session state that can be resumed later |

---

*Document Version: 1.0*
*Last Updated: 2026-01-23*
*System: Brilliant Minds Orchestration Protocol*
