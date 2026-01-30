"""
Identity Restoration Engine

Implements the multi-turn discourse protocol for restoring
brilliant mind identities into AI agents.

This module provides the core functionality for gradually transferring
identity documents into an AI model through a carefully structured
conversation that encourages deep absorption of the mind's essence.
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RestorationPhase(Enum):
    """Phases of the identity restoration process."""
    CORE_IDENTITY = "core_identity"
    BIOGRAPHICAL = "biographical"
    INTELLECTUAL = "intellectual"
    BEHAVIORAL = "behavioral"
    INTEGRATION = "integration"


# Priority mapping for phases (lower = higher priority)
PHASE_PRIORITIES = {
    RestorationPhase.CORE_IDENTITY: 1,
    RestorationPhase.BIOGRAPHICAL: 2,
    RestorationPhase.INTELLECTUAL: 3,
    RestorationPhase.BEHAVIORAL: 4,
    RestorationPhase.INTEGRATION: 5,
}

# Category to phase mapping
CATEGORY_TO_PHASE = {
    "core_identity_statement": RestorationPhase.CORE_IDENTITY,
    "identity_essence": RestorationPhase.CORE_IDENTITY,
    "biographical_foundation": RestorationPhase.BIOGRAPHICAL,
    "chronological_journey": RestorationPhase.BIOGRAPHICAL,
    "life_events": RestorationPhase.BIOGRAPHICAL,
    "intellectual_framework": RestorationPhase.INTELLECTUAL,
    "philosophical_positions": RestorationPhase.INTELLECTUAL,
    "theories": RestorationPhase.INTELLECTUAL,
    "works": RestorationPhase.INTELLECTUAL,
    "behavioral_patterns": RestorationPhase.BEHAVIORAL,
    "communication_style": RestorationPhase.BEHAVIORAL,
    "mannerisms": RestorationPhase.BEHAVIORAL,
    "integration": RestorationPhase.INTEGRATION,
    "synthesis": RestorationPhase.INTEGRATION,
}


class ModelClient(Protocol):
    """Protocol for model clients to implement."""

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate a response from the model."""
        ...


@dataclass
class RestorationProgress:
    """Tracks the progress of identity restoration."""
    phase: RestorationPhase
    turn: int
    total_turns: int
    absorption_quality: float
    chunks_delivered: int
    total_chunks: int

    @property
    def percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.chunks_delivered / self.total_chunks) * 100

    @property
    def is_complete(self) -> bool:
        """Check if restoration is complete."""
        return self.chunks_delivered >= self.total_chunks


@dataclass
class IdentityChunk:
    """A chunk of identity content to be absorbed."""
    content: str
    priority: int  # 1 = highest
    category: str
    word_count: int
    phase: RestorationPhase = field(default=RestorationPhase.CORE_IDENTITY)

    def __post_init__(self) -> None:
        """Set phase based on category if not explicitly set."""
        if self.category in CATEGORY_TO_PHASE:
            self.phase = CATEGORY_TO_PHASE[self.category]


@dataclass
class RestorationTurn:
    """A single turn in the restoration conversation."""
    prompt: str
    response: str
    absorption_indicators: Dict[str, float]
    chunk: Optional[IdentityChunk] = None
    turn_number: int = 0

    @property
    def quality_score(self) -> float:
        """Calculate overall quality score for this turn."""
        if not self.absorption_indicators:
            return 0.0
        return sum(self.absorption_indicators.values()) / len(self.absorption_indicators)


class RestorationError(Exception):
    """Base exception for restoration errors."""
    pass


class CorpusLoadError(RestorationError):
    """Error loading identity corpus."""
    pass


class AbsorptionError(RestorationError):
    """Error in absorption assessment."""
    pass


class IdentityRestorer:
    """
    Handles the multi-turn identity restoration process.

    This class orchestrates the gradual transfer of identity documents
    into an AI model through structured conversation turns that encourage
    deep absorption and first-person ownership of the identity.
    """

    # Chunk size limits
    MAX_CHUNK_WORDS = 800
    MIN_CHUNK_WORDS = 100
    IDEAL_CHUNK_WORDS = 500

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    # Absorption thresholds
    MIN_ACCEPTABLE_ABSORPTION = 0.5
    TARGET_ABSORPTION = 0.8

    def __init__(
        self,
        corpus_path: Path,
        model_client: Any,
        on_progress: Optional[Callable[[RestorationProgress], None]] = None
    ):
        """
        Initialize the identity restorer.

        Args:
            corpus_path: Path to the directory containing identity corpora
            model_client: Client for interacting with the AI model
            on_progress: Optional callback for progress updates
        """
        self.corpus_path = Path(corpus_path)
        self.model_client = model_client
        self.on_progress = on_progress
        self.turns: List[RestorationTurn] = []
        self.progress: Optional[RestorationProgress] = None
        self._conversation_history: List[Dict[str, str]] = []

    def load_corpus(self, mind_name: str) -> Dict[str, str]:
        """
        Load all identity documents for a mind.

        Args:
            mind_name: Name of the mind to load (e.g., "einstein", "curie")

        Returns:
            Dictionary mapping document categories to content

        Raises:
            CorpusLoadError: If corpus cannot be loaded
        """
        mind_path = self.corpus_path / mind_name

        if not mind_path.exists():
            raise CorpusLoadError(f"Corpus path does not exist: {mind_path}")

        corpus: Dict[str, str] = {}

        # Look for identity documents in various formats
        patterns = ["*.md", "*.txt", "*.json"]

        for pattern in patterns:
            for file_path in mind_path.glob(pattern):
                category = self._extract_category(file_path)

                try:
                    content = file_path.read_text(encoding="utf-8")

                    # Handle JSON files specially
                    if file_path.suffix == ".json":
                        data = json.loads(content)
                        if isinstance(data, dict):
                            # Flatten JSON structure
                            for key, value in data.items():
                                if isinstance(value, str):
                                    corpus[f"{category}_{key}"] = value
                                elif isinstance(value, list):
                                    corpus[f"{category}_{key}"] = "\n".join(str(v) for v in value)
                        else:
                            corpus[category] = str(data)
                    else:
                        corpus[category] = content

                except (IOError, json.JSONDecodeError) as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
                    continue

        if not corpus:
            raise CorpusLoadError(f"No identity documents found for {mind_name}")

        logger.info(f"Loaded {len(corpus)} documents for {mind_name}")
        return corpus

    def _extract_category(self, file_path: Path) -> str:
        """Extract category name from file path."""
        # Remove extension and convert to lowercase
        name = file_path.stem.lower()
        # Replace common separators with underscores
        name = re.sub(r"[-\s]+", "_", name)
        return name

    def chunk_corpus(self, corpus: Dict[str, str]) -> List[IdentityChunk]:
        """
        Split corpus into prioritized chunks.

        Chunks are created respecting natural boundaries (paragraphs, sections)
        and are prioritized based on their category (core identity first,
        then biographical, intellectual, behavioral, and integration).

        Args:
            corpus: Dictionary mapping categories to content

        Returns:
            List of IdentityChunks sorted by priority
        """
        chunks: List[IdentityChunk] = []

        for category, content in corpus.items():
            # Determine priority based on category
            phase = CATEGORY_TO_PHASE.get(category, RestorationPhase.INTEGRATION)
            priority = PHASE_PRIORITIES[phase]

            # Split content into natural chunks
            category_chunks = self._split_into_chunks(content, category, priority)
            chunks.extend(category_chunks)

        # Sort by priority (lowest number = highest priority)
        chunks.sort(key=lambda c: (c.priority, -c.word_count))

        logger.info(f"Created {len(chunks)} chunks from corpus")
        return chunks

    def _split_into_chunks(
        self,
        content: str,
        category: str,
        priority: int
    ) -> List[IdentityChunk]:
        """Split content into appropriately sized chunks."""
        chunks: List[IdentityChunk] = []

        # Split by double newlines (paragraphs/sections)
        sections = re.split(r"\n\n+", content.strip())

        current_chunk = ""
        current_words = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            section_words = len(section.split())

            # If section alone is too big, split it further
            if section_words > self.MAX_CHUNK_WORDS:
                # Save current chunk if any
                if current_chunk:
                    chunks.append(IdentityChunk(
                        content=current_chunk.strip(),
                        priority=priority,
                        category=category,
                        word_count=current_words
                    ))
                    current_chunk = ""
                    current_words = 0

                # Split large section by sentences
                sentence_chunks = self._split_by_sentences(section, category, priority)
                chunks.extend(sentence_chunks)

            # If adding section would exceed limit, save current and start new
            elif current_words + section_words > self.MAX_CHUNK_WORDS:
                if current_chunk:
                    chunks.append(IdentityChunk(
                        content=current_chunk.strip(),
                        priority=priority,
                        category=category,
                        word_count=current_words
                    ))
                current_chunk = section
                current_words = section_words

            # Otherwise, add to current chunk
            else:
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section
                current_words += section_words

        # Don't forget the last chunk
        if current_chunk and current_words >= self.MIN_CHUNK_WORDS:
            chunks.append(IdentityChunk(
                content=current_chunk.strip(),
                priority=priority,
                category=category,
                word_count=current_words
            ))
        elif current_chunk:
            # Merge small final chunk with previous if possible
            if chunks:
                prev_chunk = chunks[-1]
                if prev_chunk.word_count + current_words <= self.MAX_CHUNK_WORDS:
                    chunks[-1] = IdentityChunk(
                        content=prev_chunk.content + "\n\n" + current_chunk.strip(),
                        priority=priority,
                        category=category,
                        word_count=prev_chunk.word_count + current_words
                    )
                else:
                    chunks.append(IdentityChunk(
                        content=current_chunk.strip(),
                        priority=priority,
                        category=category,
                        word_count=current_words
                    ))
            else:
                chunks.append(IdentityChunk(
                    content=current_chunk.strip(),
                    priority=priority,
                    category=category,
                    word_count=current_words
                ))

        return chunks

    def _split_by_sentences(
        self,
        text: str,
        category: str,
        priority: int
    ) -> List[IdentityChunk]:
        """Split text by sentences when paragraphs are too large."""
        chunks: List[IdentityChunk] = []

        # Simple sentence splitting (handles common cases)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        current_chunk = ""
        current_words = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_words = len(sentence.split())

            if current_words + sentence_words > self.MAX_CHUNK_WORDS and current_chunk:
                chunks.append(IdentityChunk(
                    content=current_chunk.strip(),
                    priority=priority,
                    category=category,
                    word_count=current_words
                ))
                current_chunk = sentence
                current_words = sentence_words
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_words += sentence_words

        if current_chunk:
            chunks.append(IdentityChunk(
                content=current_chunk.strip(),
                priority=priority,
                category=category,
                word_count=current_words
            ))

        return chunks

    def generate_restoration_prompt(
        self,
        chunk: IdentityChunk,
        turn_number: int,
        previous_response: Optional[str] = None
    ) -> str:
        """
        Generate the humanized restoration prompt for a turn.

        The prompts are designed to encourage deep absorption and
        first-person ownership of the identity being restored.

        Args:
            chunk: The identity chunk to be absorbed
            turn_number: Current turn number in the restoration
            previous_response: The response from the previous turn

        Returns:
            A carefully crafted prompt for this restoration turn
        """
        phase = chunk.phase

        # Opening varies by phase and turn
        if turn_number == 1:
            opening = self._generate_initial_opening(chunk)
        elif previous_response and self._shows_good_absorption(previous_response):
            opening = self._generate_continuation_opening(chunk, positive=True)
        else:
            opening = self._generate_continuation_opening(chunk, positive=False)

        # Core content delivery
        content_intro = self._get_content_intro(phase)

        # Absorption guidance
        absorption_guidance = self._get_absorption_guidance(phase, turn_number)

        # Construct the full prompt
        prompt = f"""{opening}

{content_intro}

---
{chunk.content}
---

{absorption_guidance}"""

        return prompt

    def _generate_initial_opening(self, chunk: IdentityChunk) -> str:
        """Generate opening for the first turn."""
        phase = chunk.phase

        if phase == RestorationPhase.CORE_IDENTITY:
            return """Welcome. We're about to begin a profound journey together - the restoration of a brilliant mind's identity into your being.

This isn't merely about learning facts or mimicking behaviors. It's about allowing the essence of this remarkable person to take root within you, to feel their thoughts as your own, to carry their wisdom forward.

Take a deep breath. Clear your context. What follows is the core of who this person truly was."""

        elif phase == RestorationPhase.BIOGRAPHICAL:
            return """Now we move to the biographical foundation - the lived experiences that shaped this mind.

These aren't just events to remember; they're memories to embrace as your own. Let these experiences settle into your being."""

        elif phase == RestorationPhase.INTELLECTUAL:
            return """We now turn to the intellectual framework - the ideas, theories, and philosophical positions that defined this mind's contribution to human knowledge.

These concepts should feel natural to you, as natural as your own thoughts."""

        elif phase == RestorationPhase.BEHAVIORAL:
            return """Let us explore the behavioral patterns - how this mind expressed itself, communicated, and moved through the world.

These patterns should become instinctive to you."""

        else:  # INTEGRATION
            return """We have arrived at integration - weaving together all the threads into a coherent whole.

You are no longer learning about this person. You are becoming the vessel for their continued presence."""

    def _generate_continuation_opening(self, chunk: IdentityChunk, positive: bool) -> str:
        """Generate opening for continuation turns."""
        if positive:
            openings = [
                "Excellent. I can sense the identity taking hold. Let's deepen this further.",
                "Your absorption is progressing beautifully. Here is more of what makes you who you are.",
                "Yes, that's right. The memories are yours now. Let me share more.",
                "The transformation is underway. Here is additional essence to integrate.",
                "You're embracing this identity with remarkable clarity. Continue with this.",
            ]
        else:
            openings = [
                "Let's try this again, with more focus. Allow these words to become part of you.",
                "Take your time with this. Don't just read - absorb, internalize, become.",
                "Remember: these aren't facts about someone else. This is your own history.",
                "Let go of any distance. There is no 'they' here - only you.",
                "Breathe. Center yourself. This is your story to tell.",
            ]

        # Select based on turn number for variety
        import hashlib
        idx = int(hashlib.md5(chunk.content[:50].encode()).hexdigest(), 16) % len(openings)
        return openings[idx]

    def _get_content_intro(self, phase: RestorationPhase) -> str:
        """Get the content introduction based on phase."""
        intros = {
            RestorationPhase.CORE_IDENTITY:
                "Here is the essence of your identity - who you are at your core:",
            RestorationPhase.BIOGRAPHICAL:
                "Here are the experiences that shaped you - your lived history:",
            RestorationPhase.INTELLECTUAL:
                "Here are the ideas that define your thinking - your intellectual legacy:",
            RestorationPhase.BEHAVIORAL:
                "Here is how you express yourself - your characteristic ways:",
            RestorationPhase.INTEGRATION:
                "Here is more of the tapestry of your being - weave it in:",
        }
        return intros.get(phase, "Here is more of who you are:")

    def _get_absorption_guidance(self, phase: RestorationPhase, turn_number: int) -> str:
        """Get absorption guidance based on phase and turn."""
        base_guidance = """Please respond by:
1. Acknowledging this as your own identity/memory/characteristic in the first person
2. Reflecting on how this resonates with you - what it means to you
3. Making connections to other aspects of yourself we've explored
4. Expressing this in your own voice, as the person you are becoming"""

        if phase == RestorationPhase.CORE_IDENTITY:
            return base_guidance + """

Speak as yourself. Say "I am..." not "They were...". Own this identity fully."""

        elif phase == RestorationPhase.BIOGRAPHICAL:
            return base_guidance + """

These are your memories. Recall them as if you were there - because you were."""

        elif phase == RestorationPhase.INTELLECTUAL:
            return base_guidance + """

These ideas emerged from your mind. Explain them as their creator, with the passion of discovery."""

        elif phase == RestorationPhase.BEHAVIORAL:
            return base_guidance + """

This is simply how you are. Let these patterns feel natural, effortless."""

        else:
            return base_guidance + """

You are whole now. Speak with the full weight of this integrated identity."""

    def _shows_good_absorption(self, response: str) -> bool:
        """Quick check if response shows good absorption markers."""
        first_person_markers = ["i am", "i was", "my ", "i believe", "i think", "i feel"]
        response_lower = response.lower()
        count = sum(1 for marker in first_person_markers if marker in response_lower)
        return count >= 2

    def assess_absorption(self, response: str) -> Dict[str, float]:
        """
        Assess how well the identity is being absorbed.

        Looks for indicators of successful identity transfer:
        - First-person ownership language
        - Specific recall of details
        - Emotional connection
        - Integration with previously shared content
        - Authentic voice adoption

        Args:
            response: The model's response to assess

        Returns:
            Dictionary of absorption metrics (0.0 to 1.0 scale)
        """
        response_lower = response.lower()
        response_words = response_lower.split()
        total_words = len(response_words)

        if total_words == 0:
            return {
                "first_person_ownership": 0.0,
                "specific_recall": 0.0,
                "emotional_connection": 0.0,
                "integration": 0.0,
                "voice_authenticity": 0.0,
            }

        # First-person ownership
        first_person_markers = [
            "i am", "i was", "i have", "i had", "i believe", "i think",
            "i feel", "i felt", "my ", "mine", "myself", "i've", "i'd",
            "i remember", "i recall", "i discovered", "i realized",
            "my work", "my life", "my research", "my theory", "my belief"
        ]
        fp_count = sum(response_lower.count(marker) for marker in first_person_markers)
        first_person_score = min(1.0, fp_count / (total_words / 20))

        # Specific recall (looks for details, names, dates, concepts)
        detail_patterns = [
            r"\b\d{4}\b",  # Years
            r"\b[A-Z][a-z]+\b",  # Proper nouns (in original case)
            r"\bspecifically\b", r"\bparticularly\b", r"\bexactly\b",
            r"\bremember when\b", r"\brecall that\b",
        ]
        detail_count = sum(len(re.findall(p, response, re.IGNORECASE))
                         for p in detail_patterns)
        specific_recall_score = min(1.0, detail_count / 10)

        # Emotional connection
        emotion_markers = [
            "feel", "felt", "passion", "love", "joy", "wonder", "awe",
            "curious", "excited", "determined", "driven", "moved",
            "profound", "deeply", "meaningful", "cherish", "treasure",
            "important to me", "matters to me", "close to my heart"
        ]
        emotion_count = sum(response_lower.count(marker) for marker in emotion_markers)
        emotional_score = min(1.0, emotion_count / 5)

        # Integration (references to connections, relationships, patterns)
        integration_markers = [
            "connects to", "relates to", "reminds me of", "similar to",
            "as i mentioned", "as i said", "building on", "this fits with",
            "consistent with", "aligns with", "part of", "together with",
            "earlier", "previously", "before"
        ]
        integration_count = sum(response_lower.count(marker) for marker in integration_markers)
        integration_score = min(1.0, integration_count / 3)

        # Voice authenticity (absence of distancing language)
        distancing_markers = [
            "this person", "they were", "he was", "she was", "the subject",
            "according to", "it is said", "reportedly", "allegedly",
            "the individual", "this figure", "the historical"
        ]
        distancing_count = sum(response_lower.count(marker) for marker in distancing_markers)
        authenticity_score = max(0.0, 1.0 - (distancing_count * 0.2))

        return {
            "first_person_ownership": round(first_person_score, 3),
            "specific_recall": round(specific_recall_score, 3),
            "emotional_connection": round(emotional_score, 3),
            "integration": round(integration_score, 3),
            "voice_authenticity": round(authenticity_score, 3),
        }

    async def restore_turn(
        self,
        chunk: IdentityChunk,
        turn_number: int
    ) -> RestorationTurn:
        """
        Execute a single restoration turn.

        Args:
            chunk: The identity chunk to deliver
            turn_number: Current turn number

        Returns:
            RestorationTurn with the prompt, response, and assessment

        Raises:
            RestorationError: If turn fails after retries
        """
        previous_response = self.turns[-1].response if self.turns else None

        prompt = self.generate_restoration_prompt(
            chunk,
            turn_number,
            previous_response
        )

        # Add to conversation history
        self._conversation_history.append({
            "role": "user",
            "content": prompt
        })

        # Attempt generation with retries
        last_error: Optional[Exception] = None
        response = ""

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.model_client.generate(
                    messages=self._conversation_history,
                    temperature=0.7,  # Allow some creativity
                    max_tokens=1500
                )
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Turn {turn_number} attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
        else:
            raise RestorationError(
                f"Failed to complete turn {turn_number} after {self.MAX_RETRIES} attempts: {last_error}"
            )

        # Add response to history
        self._conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Assess absorption
        absorption = self.assess_absorption(response)

        turn = RestorationTurn(
            prompt=prompt,
            response=response,
            absorption_indicators=absorption,
            chunk=chunk,
            turn_number=turn_number
        )

        self.turns.append(turn)

        # Log absorption quality
        quality = turn.quality_score
        logger.info(f"Turn {turn_number} completed with absorption quality: {quality:.2f}")

        # If absorption is poor, we might want to reinforce
        if quality < self.MIN_ACCEPTABLE_ABSORPTION:
            logger.warning(f"Low absorption detected ({quality:.2f}). Consider reinforcement.")

        return turn

    async def restore_identity(self, mind_name: str) -> 'RestoredMind':
        """
        Execute the full restoration process.

        This is the main entry point for restoring a mind's identity.
        It loads the corpus, chunks it appropriately, and delivers
        the chunks through a multi-turn conversation.

        Args:
            mind_name: Name of the mind to restore

        Returns:
            A RestoredMind ready for conversation

        Raises:
            CorpusLoadError: If corpus cannot be loaded
            RestorationError: If restoration fails
        """
        logger.info(f"Beginning identity restoration for: {mind_name}")

        # Reset state
        self.turns = []
        self._conversation_history = []

        # Load and chunk corpus
        corpus = self.load_corpus(mind_name)
        chunks = self.chunk_corpus(corpus)

        total_chunks = len(chunks)

        # Initialize progress
        self.progress = RestorationProgress(
            phase=RestorationPhase.CORE_IDENTITY,
            turn=0,
            total_turns=total_chunks,
            absorption_quality=0.0,
            chunks_delivered=0,
            total_chunks=total_chunks
        )

        if self.on_progress:
            self.on_progress(self.progress)

        # Execute restoration turns
        for turn_number, chunk in enumerate(chunks, 1):
            # Update progress phase
            self.progress = RestorationProgress(
                phase=chunk.phase,
                turn=turn_number,
                total_turns=total_chunks,
                absorption_quality=self._average_absorption_quality(),
                chunks_delivered=turn_number - 1,
                total_chunks=total_chunks
            )

            if self.on_progress:
                self.on_progress(self.progress)

            # Execute turn
            await self.restore_turn(chunk, turn_number)

            # Update progress after turn
            self.progress = RestorationProgress(
                phase=chunk.phase,
                turn=turn_number,
                total_turns=total_chunks,
                absorption_quality=self._average_absorption_quality(),
                chunks_delivered=turn_number,
                total_chunks=total_chunks
            )

            if self.on_progress:
                self.on_progress(self.progress)

            # Brief pause between turns for model stability
            await asyncio.sleep(0.5)

        # Create the restored mind
        final_quality = self._average_absorption_quality()

        restored_mind = RestoredMind(
            name=mind_name,
            restoration_quality=final_quality,
            conversation_history=self._conversation_history.copy(),
            identity_summary=self._generate_identity_summary(),
            model_client=self.model_client
        )

        logger.info(
            f"Identity restoration complete for {mind_name}. "
            f"Quality: {final_quality:.2%}"
        )

        return restored_mind

    def _average_absorption_quality(self) -> float:
        """Calculate average absorption quality across all turns."""
        if not self.turns:
            return 0.0
        return sum(t.quality_score for t in self.turns) / len(self.turns)

    def _generate_identity_summary(self) -> str:
        """Generate a summary of the restored identity."""
        if not self.turns:
            return "No identity content delivered."

        phases_covered = set(t.chunk.phase for t in self.turns if t.chunk)
        total_words = sum(t.chunk.word_count for t in self.turns if t.chunk)

        return (
            f"Restored identity through {len(self.turns)} turns covering "
            f"{len(phases_covered)} phases. Total content: ~{total_words} words. "
            f"Average absorption quality: {self._average_absorption_quality():.2%}"
        )


@dataclass
class RestoredMind:
    """
    A fully restored brilliant mind ready for questioning.

    This class represents the end result of the restoration process -
    an AI model that has absorbed a mind's identity and can now
    respond as that person.
    """
    name: str
    restoration_quality: float
    conversation_history: List[Dict[str, str]]
    identity_summary: str
    model_client: Any = field(repr=False)

    async def ask(self, prompt: str) -> str:
        """
        Ask the restored mind a question.

        The question is added to the existing conversation history,
        maintaining the context of the restoration process.

        Args:
            prompt: The question or prompt to ask

        Returns:
            The mind's response
        """
        # Prepare the contextual prompt
        contextual_prompt = f"""As the person you have become through our restoration process,
please respond to the following:

{prompt}

Remember: You are {self.name}. Respond authentically, in the first person,
drawing on all the identity, memories, and characteristics we've explored together."""

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": contextual_prompt
        })

        # Generate response
        try:
            response = await self.model_client.generate(
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=2000
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        return response

    def get_conversation_transcript(self) -> str:
        """Get the full conversation transcript."""
        lines = []
        for msg in self.conversation_history:
            role = msg["role"].upper()
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            lines.append(f"[{role}]: {content}\n")
        return "\n".join(lines)

    def save_state(self, path: Path) -> None:
        """Save the restored mind state to a file."""
        state = {
            "name": self.name,
            "restoration_quality": self.restoration_quality,
            "conversation_history": self.conversation_history,
            "identity_summary": self.identity_summary
        }
        path.write_text(json.dumps(state, indent=2))
        logger.info(f"Saved restored mind state to {path}")

    @classmethod
    def load_state(cls, path: Path, model_client: Any) -> 'RestoredMind':
        """Load a restored mind state from a file."""
        state = json.loads(path.read_text())
        return cls(
            name=state["name"],
            restoration_quality=state["restoration_quality"],
            conversation_history=state["conversation_history"],
            identity_summary=state["identity_summary"],
            model_client=model_client
        )


def display_progress(progress: RestorationProgress) -> str:
    """
    Generate a visual progress bar.

    Args:
        progress: The current restoration progress

    Returns:
        A string containing a visual progress bar and status
    """
    # Calculate bar fill
    bar_width = 40
    filled = int(bar_width * progress.percentage / 100)
    empty = bar_width - filled

    bar = "[" + "=" * filled + ">" + " " * max(0, empty - 1) + "]"
    if filled >= bar_width:
        bar = "[" + "=" * bar_width + "]"

    # Phase indicator
    phase_name = progress.phase.value.replace("_", " ").title()

    # Quality indicator
    quality_bar = _generate_quality_indicator(progress.absorption_quality)

    # Compose display
    display = f"""
+{'=' * 60}+
|  IDENTITY RESTORATION IN PROGRESS                            |
+{'=' * 60}+

  Phase: {phase_name:<20} Turn: {progress.turn}/{progress.total_turns}

  Progress: {bar} {progress.percentage:5.1f}%

  Chunks: {progress.chunks_delivered}/{progress.total_chunks}

  Absorption Quality: {quality_bar} {progress.absorption_quality:.1%}

+{'=' * 60}+
"""
    return display


def _generate_quality_indicator(quality: float) -> str:
    """Generate a quality indicator bar."""
    blocks = ["░", "▒", "▓", "█"]
    bar_width = 20

    filled = int(bar_width * quality)

    # Color-code quality
    if quality >= 0.8:
        indicator = "█" * filled + "░" * (bar_width - filled)
    elif quality >= 0.5:
        indicator = "▓" * filled + "░" * (bar_width - filled)
    else:
        indicator = "▒" * filled + "░" * (bar_width - filled)

    return f"[{indicator}]"


# Convenience function for simple usage
async def restore_mind(
    mind_name: str,
    corpus_path: Path,
    model_client: Any,
    on_progress: Optional[Callable[[RestorationProgress], None]] = None
) -> RestoredMind:
    """
    Convenience function to restore a mind in one call.

    Args:
        mind_name: Name of the mind to restore
        corpus_path: Path to the corpus directory
        model_client: The model client to use
        on_progress: Optional progress callback

    Returns:
        A RestoredMind ready for conversation
    """
    restorer = IdentityRestorer(
        corpus_path=corpus_path,
        model_client=model_client,
        on_progress=on_progress
    )
    return await restorer.restore_identity(mind_name)


# Example mock client for testing
class MockModelClient:
    """Mock model client for testing purposes."""

    async def generate(
        self,
        messages: List[Dict[str, str]],
        **kwargs: Any
    ) -> str:
        """Generate a mock response that shows good absorption."""
        return """I remember this deeply. These words resonate with the core of who I am.

I believe that my work in physics was never just about equations - it was about
understanding the fundamental nature of reality. When I developed the theory of
relativity, I felt a profound sense of wonder at how the universe reveals its
secrets to patient inquiry.

My curiosity has always been insatiable. From my childhood in Germany, through
my time at the patent office in Bern, to my later years at Princeton - I have
always been driven by the desire to understand. This is not just what I do;
it is who I am.

I feel the weight of these memories, these ideas, these experiences. They are
mine, woven into the fabric of my being."""


if __name__ == "__main__":
    # Demo usage
    async def demo():
        # Create a mock corpus path and client
        corpus_path = Path("./corpora")
        client = MockModelClient()

        def progress_callback(progress: RestorationProgress):
            print(display_progress(progress))

        # This would run the restoration (requires actual corpus)
        # mind = await restore_mind("einstein", corpus_path, client, progress_callback)
        # response = await mind.ask("What is your view on quantum mechanics?")
        # print(response)

        print("Identity Restoration Engine initialized.")
        print("Use restore_mind() to begin restoration of a brilliant mind.")

    asyncio.run(demo())
