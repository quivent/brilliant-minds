"""
Repository Evaluation Engine

Uses restored brilliant minds to evaluate repositories
using their selected benchmark questions.

This module provides a comprehensive framework for:
1. Building repository context from filesystem analysis
2. Batched question answering using LLM APIs
3. Evidence extraction and linking to specific files/lines
4. Score aggregation and consensus across multiple minds
5. Report generation in multiple formats (markdown, JSON)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, Protocol, runtime_checkable
from pathlib import Path
from enum import Enum
from datetime import datetime
import json
import asyncio
import re
import os
import subprocess
from abc import ABC, abstractmethod


class ScoreLevel(Enum):
    """Score levels with ranges and descriptions."""
    DEFICIENT = (1, 3, "Serious deficiencies")
    BELOW = (4, 5, "Below expectations")
    MEETS = (6, 7, "Meets basic standards")
    EXCEEDS = (8, 9, "Exceeds expectations")
    EXEMPLARY = (10, 10, "Exemplary")

    @classmethod
    def from_score(cls, score: int) -> 'ScoreLevel':
        """Determine score level from numeric score."""
        score = max(1, min(10, score))  # Clamp to valid range
        for level in cls:
            if level.value[0] <= score <= level.value[1]:
                return level
        return cls.DEFICIENT

    @property
    def min_score(self) -> int:
        return self.value[0]

    @property
    def max_score(self) -> int:
        return self.value[1]

    @property
    def description(self) -> str:
        return self.value[2]


@dataclass
class Evidence:
    """Evidence supporting an assessment."""
    file_path: str
    line_numbers: Optional[Tuple[int, int]]  # (start, end) or None
    excerpt: str
    relevance: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_numbers": list(self.line_numbers) if self.line_numbers else None,
            "excerpt": self.excerpt,
            "relevance": self.relevance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evidence':
        return cls(
            file_path=data["file_path"],
            line_numbers=tuple(data["line_numbers"]) if data.get("line_numbers") else None,
            excerpt=data["excerpt"],
            relevance=data["relevance"]
        )

    def to_markdown(self) -> str:
        """Format evidence as markdown."""
        lines = []
        if self.line_numbers:
            lines.append(f"**File**: `{self.file_path}` (lines {self.line_numbers[0]}-{self.line_numbers[1]})")
        else:
            lines.append(f"**File**: `{self.file_path}`")
        lines.append(f"**Relevance**: {self.relevance}")
        lines.append("```")
        lines.append(self.excerpt[:500] + ("..." if len(self.excerpt) > 500 else ""))
        lines.append("```")
        return "\n".join(lines)


@runtime_checkable
class Question(Protocol):
    """Protocol for benchmark questions."""
    id: str
    text: str
    category: str
    weight: float


@dataclass
class BenchmarkQuestion:
    """A benchmark question for repository evaluation."""
    id: str
    text: str
    category: str
    weight: float = 1.0
    sub_questions: List[str] = field(default_factory=list)
    evaluation_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "weight": self.weight,
            "sub_questions": self.sub_questions,
            "evaluation_criteria": self.evaluation_criteria
        }


@dataclass
class QuestionAnswer:
    """Answer to a benchmark question with evidence."""
    question: BenchmarkQuestion
    answer: str
    score: int
    score_level: ScoreLevel
    evidence: List[Evidence]
    recommendations: List[str]
    confidence: float  # 0.0 to 1.0 - how confident the mind is in this assessment
    reasoning: str = ""  # Detailed reasoning for the score

    def __post_init__(self):
        if not isinstance(self.score_level, ScoreLevel):
            self.score_level = ScoreLevel.from_score(self.score)
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question.to_dict() if hasattr(self.question, 'to_dict') else str(self.question),
            "answer": self.answer,
            "score": self.score,
            "score_level": self.score_level.name,
            "evidence": [e.to_dict() for e in self.evidence],
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }

    def weighted_score(self) -> float:
        """Calculate confidence-weighted score."""
        weight = getattr(self.question, 'weight', 1.0)
        return self.score * self.confidence * weight

    def to_markdown(self) -> str:
        """Format answer as markdown."""
        lines = [
            f"### {self.question.text}",
            f"**Category**: {self.question.category}",
            f"**Score**: {self.score}/10 ({self.score_level.description})",
            f"**Confidence**: {self.confidence:.0%}",
            "",
            "#### Answer",
            self.answer,
            ""
        ]

        if self.reasoning:
            lines.extend(["#### Reasoning", self.reasoning, ""])

        if self.evidence:
            lines.append("#### Evidence")
            for i, ev in enumerate(self.evidence, 1):
                lines.append(f"\n**Evidence {i}**:")
                lines.append(ev.to_markdown())
            lines.append("")

        if self.recommendations:
            lines.append("#### Recommendations")
            for rec in self.recommendations:
                lines.append(f"- {rec}")

        return "\n".join(lines)


@dataclass
class Benchmark:
    """A complete benchmark with questions."""
    name: str
    description: str
    questions: List[BenchmarkQuestion]
    categories: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.categories:
            self.categories = list(set(q.category for q in self.questions))

    def questions_by_category(self) -> Dict[str, List[BenchmarkQuestion]]:
        """Group questions by category."""
        result: Dict[str, List[BenchmarkQuestion]] = {}
        for q in self.questions:
            if q.category not in result:
                result[q.category] = []
            result[q.category].append(q)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "questions": [q.to_dict() for q in self.questions],
            "categories": self.categories
        }


@dataclass
class EvaluationReport:
    """Complete evaluation report from a single mind."""
    mind_name: str
    repository_name: str
    answers: List[QuestionAnswer]
    overall_score: float
    executive_summary: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    timestamp: str
    evaluation_duration_seconds: float = 0.0
    repository_stats: Dict[str, Any] = field(default_factory=dict)

    def by_category(self) -> Dict[str, List[QuestionAnswer]]:
        """Group answers by question category."""
        result: Dict[str, List[QuestionAnswer]] = {}
        for answer in self.answers:
            category = answer.question.category
            if category not in result:
                result[category] = []
            result[category].append(answer)
        return result

    def category_scores(self) -> Dict[str, float]:
        """Calculate average score per category."""
        by_cat = self.by_category()
        return {
            cat: sum(a.score for a in answers) / len(answers) if answers else 0.0
            for cat, answers in by_cat.items()
        }

    def weighted_score(self) -> float:
        """Calculate weighted score based on question weights and confidence."""
        if not self.answers:
            return 0.0
        total_weight = sum(
            a.question.weight * a.confidence for a in self.answers
            if hasattr(a.question, 'weight')
        )
        if total_weight == 0:
            return self.overall_score
        weighted_sum = sum(a.weighted_score() for a in self.answers)
        return weighted_sum / total_weight

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Repository Evaluation Report: {self.repository_name}",
            f"**Evaluator**: {self.mind_name}",
            f"**Date**: {self.timestamp}",
            f"**Overall Score**: {self.overall_score:.1f}/10",
            "",
            "---",
            "",
            "## Executive Summary",
            self.executive_summary,
            "",
        ]

        # Repository stats if available
        if self.repository_stats:
            lines.extend([
                "## Repository Statistics",
                "| Metric | Value |",
                "|--------|-------|"
            ])
            for key, value in self.repository_stats.items():
                lines.append(f"| {key.replace('_', ' ').title()} | {value} |")
            lines.append("")

        # Category scores overview
        cat_scores = self.category_scores()
        if cat_scores:
            lines.extend([
                "## Score by Category",
                "| Category | Score |",
                "|----------|-------|"
            ])
            for cat, score in sorted(cat_scores.items()):
                level = ScoreLevel.from_score(int(score))
                lines.append(f"| {cat} | {score:.1f}/10 ({level.description}) |")
            lines.append("")

        # Strengths and Weaknesses
        lines.extend([
            "## Key Findings",
            "",
            "### Strengths"
        ])
        for s in self.strengths:
            lines.append(f"- {s}")

        lines.extend(["", "### Weaknesses"])
        for w in self.weaknesses:
            lines.append(f"- {w}")

        lines.extend(["", "### Recommendations"])
        for r in self.recommendations:
            lines.append(f"- {r}")

        # Detailed answers by category
        lines.extend(["", "---", "", "## Detailed Evaluation"])

        for category, answers in self.by_category().items():
            lines.extend([
                "",
                f"## Category: {category}",
                ""
            ])
            for answer in answers:
                lines.append(answer.to_markdown())
                lines.append("\n---\n")

        # Footer
        if self.evaluation_duration_seconds > 0:
            lines.append(f"\n*Evaluation completed in {self.evaluation_duration_seconds:.1f} seconds*")

        return "\n".join(lines)

    def to_json(self, path: str) -> None:
        """Save report to JSON file."""
        data = {
            "mind_name": self.mind_name,
            "repository_name": self.repository_name,
            "overall_score": self.overall_score,
            "weighted_score": self.weighted_score(),
            "executive_summary": self.executive_summary,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
            "evaluation_duration_seconds": self.evaluation_duration_seconds,
            "repository_stats": self.repository_stats,
            "category_scores": self.category_scores(),
            "answers": [a.to_dict() for a in self.answers]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: str) -> 'EvaluationReport':
        """Load report from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        answers = []
        for a_data in data.get("answers", []):
            q_data = a_data.get("question", {})
            if isinstance(q_data, dict):
                question = BenchmarkQuestion(
                    id=q_data.get("id", ""),
                    text=q_data.get("text", ""),
                    category=q_data.get("category", "General"),
                    weight=q_data.get("weight", 1.0)
                )
            else:
                question = BenchmarkQuestion(id="", text=str(q_data), category="General")

            evidence = [Evidence.from_dict(e) for e in a_data.get("evidence", [])]

            answers.append(QuestionAnswer(
                question=question,
                answer=a_data.get("answer", ""),
                score=a_data.get("score", 5),
                score_level=ScoreLevel[a_data.get("score_level", "MEETS")],
                evidence=evidence,
                recommendations=a_data.get("recommendations", []),
                confidence=a_data.get("confidence", 0.8),
                reasoning=a_data.get("reasoning", "")
            ))

        return cls(
            mind_name=data.get("mind_name", "Unknown"),
            repository_name=data.get("repository_name", "Unknown"),
            answers=answers,
            overall_score=data.get("overall_score", 0.0),
            executive_summary=data.get("executive_summary", ""),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            recommendations=data.get("recommendations", []),
            timestamp=data.get("timestamp", ""),
            evaluation_duration_seconds=data.get("evaluation_duration_seconds", 0.0),
            repository_stats=data.get("repository_stats", {})
        )


# File extension to language mapping (module-level constant)
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    '.py': 'Python', '.pyi': 'Python',
    '.js': 'JavaScript', '.jsx': 'JavaScript',
    '.ts': 'TypeScript', '.tsx': 'TypeScript',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.c': 'C', '.h': 'C',
    '.cpp': 'C++', '.hpp': 'C++', '.cc': 'C++',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.cs': 'C#',
    '.sh': 'Shell', '.bash': 'Shell',
    '.sql': 'SQL',
    '.md': 'Markdown',
    '.yaml': 'YAML', '.yml': 'YAML',
    '.json': 'JSON',
    '.toml': 'TOML',
    '.xml': 'XML',
    '.html': 'HTML',
    '.css': 'CSS', '.scss': 'CSS', '.sass': 'CSS',
}

# Important files to always include (module-level constant)
IMPORTANT_FILES: List[str] = [
    'README.md', 'README.rst', 'README.txt', 'README',
    'setup.py', 'setup.cfg', 'pyproject.toml',
    'package.json', 'package-lock.json',
    'Cargo.toml', 'Cargo.lock',
    'go.mod', 'go.sum',
    'Makefile', 'CMakeLists.txt',
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    '.github/workflows/*.yml', '.github/workflows/*.yaml',
    'requirements.txt', 'requirements-dev.txt',
    'tox.ini', 'pytest.ini', '.pytest.ini',
    'LICENSE', 'LICENSE.md', 'LICENSE.txt',
    'CONTRIBUTING.md', 'CHANGELOG.md',
    '.gitignore', '.dockerignore',
    'tsconfig.json', 'webpack.config.js',
    'main.py', 'app.py', 'index.js', 'index.ts', 'main.go', 'main.rs',
]


@dataclass
class RepositoryContext:
    """Context about a repository for evaluation."""
    name: str
    path: Path
    structure: Dict[str, Any]  # Tree structure
    key_files: Dict[str, str]  # path -> content
    readme: Optional[str]
    languages: Dict[str, int]  # language -> line count
    dependencies: List[str]
    test_coverage: Optional[float]
    git_info: Dict[str, Any] = field(default_factory=dict)
    total_files: int = 0
    total_lines: int = 0

    @classmethod
    def from_path(cls, path: Path) -> 'RepositoryContext':
        """Build context from repository path."""
        path = Path(path).resolve()
        if not path.exists():
            raise ValueError(f"Repository path does not exist: {path}")

        name = path.name
        structure = cls._build_structure(path)
        key_files = cls._extract_key_files(path)
        readme = cls._find_readme(path)
        languages = cls._analyze_languages(path)
        dependencies = cls._extract_dependencies(path)
        test_coverage = cls._detect_test_coverage(path)
        git_info = cls._get_git_info(path)
        total_files, total_lines = cls._count_files_and_lines(path)

        return cls(
            name=name,
            path=path,
            structure=structure,
            key_files=key_files,
            readme=readme,
            languages=languages,
            dependencies=dependencies,
            test_coverage=test_coverage,
            git_info=git_info,
            total_files=total_files,
            total_lines=total_lines
        )

    @classmethod
    def _build_structure(cls, path: Path, max_depth: int = 4) -> Dict[str, Any]:
        """Build tree structure of repository."""
        def build_tree(current: Path, depth: int) -> Dict[str, Any]:
            if depth > max_depth:
                return {"type": "truncated"}

            result: Dict[str, Any] = {"type": "directory", "children": {}}

            try:
                items = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                for item in items:
                    # Skip hidden files and common ignore patterns
                    if item.name.startswith('.') and item.name not in ['.github', '.gitignore']:
                        continue
                    if item.name in ['node_modules', '__pycache__', 'venv', '.venv',
                                     'build', 'dist', '.git', '.idea', '.vscode',
                                     'target', '.pytest_cache', '.mypy_cache', 'coverage']:
                        continue

                    if item.is_dir():
                        result["children"][item.name] = build_tree(item, depth + 1)
                    else:
                        result["children"][item.name] = {"type": "file", "size": item.stat().st_size}
            except PermissionError:
                result["error"] = "Permission denied"

            return result

        return build_tree(path, 0)

    @classmethod
    def _extract_key_files(cls, path: Path, max_file_size: int = 50000) -> Dict[str, str]:
        """Extract content of key files."""
        key_files: Dict[str, str] = {}

        for pattern in IMPORTANT_FILES:
            if '*' in pattern:
                # Handle glob patterns
                matches = list(path.glob(pattern))
            else:
                matches = [path / pattern]

            for file_path in matches:
                if file_path.exists() and file_path.is_file():
                    try:
                        if file_path.stat().st_size <= max_file_size:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            rel_path = str(file_path.relative_to(path))
                            key_files[rel_path] = content
                    except (PermissionError, OSError):
                        continue

        return key_files

    @classmethod
    def _find_readme(cls, path: Path) -> Optional[str]:
        """Find and read README file."""
        readme_names = ['README.md', 'README.rst', 'README.txt', 'README', 'readme.md']
        for name in readme_names:
            readme_path = path / name
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding='utf-8', errors='ignore')
                except (PermissionError, OSError):
                    continue
        return None

    @classmethod
    def _analyze_languages(cls, path: Path) -> Dict[str, int]:
        """Analyze languages used in repository by line count."""
        languages: Dict[str, int] = {}
        ext_map = LANGUAGE_EXTENSIONS

        for file_path in path.rglob('*'):
            if not file_path.is_file():
                continue

            # Skip common ignore patterns
            path_str = str(file_path)
            if any(skip in path_str for skip in [
                'node_modules', '__pycache__', '.git', 'venv', '.venv',
                'build', 'dist', 'target', '.pytest_cache'
            ]):
                continue

            ext = file_path.suffix.lower()
            if ext in ext_map:
                try:
                    line_count = sum(1 for _ in file_path.open(encoding='utf-8', errors='ignore'))
                    lang = ext_map[ext]
                    languages[lang] = languages.get(lang, 0) + line_count
                except (PermissionError, OSError):
                    continue

        return dict(sorted(languages.items(), key=lambda x: -x[1]))

    @classmethod
    def _extract_dependencies(cls, path: Path) -> List[str]:
        """Extract project dependencies."""
        dependencies: List[str] = []

        # Python
        req_file = path / 'requirements.txt'
        if req_file.exists():
            try:
                content = req_file.read_text(encoding='utf-8', errors='ignore')
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        pkg = re.split(r'[<>=!~\[]', line)[0].strip()
                        if pkg:
                            dependencies.append(f"python:{pkg}")
            except (PermissionError, OSError):
                pass

        # Python pyproject.toml
        pyproject = path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding='utf-8', errors='ignore')
                # Simple parsing for dependencies
                in_deps = False
                for line in content.splitlines():
                    if 'dependencies' in line and '=' in line:
                        in_deps = True
                    elif in_deps:
                        if line.strip().startswith(']'):
                            in_deps = False
                        elif '"' in line or "'" in line:
                            match = re.search(r'["\']([^"\']+)["\']', line)
                            if match:
                                pkg = re.split(r'[<>=!~\[]', match.group(1))[0].strip()
                                if pkg:
                                    dependencies.append(f"python:{pkg}")
            except (PermissionError, OSError):
                pass

        # Node.js
        pkg_json = path / 'package.json'
        if pkg_json.exists():
            try:
                content = json.loads(pkg_json.read_text(encoding='utf-8'))
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in content:
                        for pkg in content[dep_type]:
                            dependencies.append(f"npm:{pkg}")
            except (json.JSONDecodeError, PermissionError, OSError):
                pass

        # Go
        go_mod = path / 'go.mod'
        if go_mod.exists():
            try:
                content = go_mod.read_text(encoding='utf-8', errors='ignore')
                for line in content.splitlines():
                    if line.strip().startswith('require') or '\t' in line:
                        parts = line.strip().split()
                        if len(parts) >= 1 and '/' in parts[0]:
                            dependencies.append(f"go:{parts[0]}")
            except (PermissionError, OSError):
                pass

        # Rust
        cargo_toml = path / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                content = cargo_toml.read_text(encoding='utf-8', errors='ignore')
                in_deps = False
                for line in content.splitlines():
                    if '[dependencies]' in line or '[dev-dependencies]' in line:
                        in_deps = True
                    elif line.startswith('[') and in_deps:
                        in_deps = False
                    elif in_deps and '=' in line:
                        pkg = line.split('=')[0].strip()
                        if pkg:
                            dependencies.append(f"cargo:{pkg}")
            except (PermissionError, OSError):
                pass

        return dependencies

    @classmethod
    def _detect_test_coverage(cls, path: Path) -> Optional[float]:
        """Try to detect test coverage from coverage reports."""
        coverage_files = [
            'coverage.xml', 'coverage.json', '.coverage',
            'htmlcov/index.html', 'coverage/lcov.info',
            'coverage-final.json'
        ]

        for cov_file in coverage_files:
            cov_path = path / cov_file
            if cov_path.exists():
                try:
                    content = cov_path.read_text(encoding='utf-8', errors='ignore')

                    # Try to extract coverage percentage
                    if cov_file.endswith('.xml'):
                        match = re.search(r'line-rate="([0-9.]+)"', content)
                        if match:
                            return float(match.group(1)) * 100
                    elif cov_file.endswith('.json'):
                        data = json.loads(content)
                        if 'totals' in data and 'percent_covered' in data['totals']:
                            return data['totals']['percent_covered']
                    elif 'lcov.info' in cov_file:
                        lines_found = lines_hit = 0
                        for line in content.splitlines():
                            if line.startswith('LF:'):
                                lines_found += int(line[3:])
                            elif line.startswith('LH:'):
                                lines_hit += int(line[3:])
                        if lines_found > 0:
                            return (lines_hit / lines_found) * 100
                except (json.JSONDecodeError, PermissionError, OSError, ValueError):
                    continue

        return None

    @classmethod
    def _get_git_info(cls, path: Path) -> Dict[str, Any]:
        """Get git repository information."""
        git_info: Dict[str, Any] = {}

        try:
            # Check if it's a git repo
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return git_info

            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                git_info['branch'] = result.stdout.strip()

            # Get commit count
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                git_info['commit_count'] = int(result.stdout.strip())

            # Get last commit info
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%s|%ai'],
                cwd=path, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) >= 3:
                    git_info['last_commit'] = {
                        'hash': parts[0][:8],
                        'message': parts[1],
                        'date': parts[2]
                    }

            # Get contributors count
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--all'],
                cwd=path, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                git_info['contributors'] = len(result.stdout.strip().splitlines())

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return git_info

    @classmethod
    def _count_files_and_lines(cls, path: Path) -> Tuple[int, int]:
        """Count total files and lines of code."""
        total_files = 0
        total_lines = 0
        code_extensions = set(LANGUAGE_EXTENSIONS.keys())

        for file_path in path.rglob('*'):
            if not file_path.is_file():
                continue

            path_str = str(file_path)
            if any(skip in path_str for skip in [
                'node_modules', '__pycache__', '.git', 'venv', '.venv',
                'build', 'dist', 'target'
            ]):
                continue

            total_files += 1

            if file_path.suffix.lower() in code_extensions:
                try:
                    total_lines += sum(1 for _ in file_path.open(encoding='utf-8', errors='ignore'))
                except (PermissionError, OSError):
                    continue

        return total_files, total_lines

    def to_prompt_context(self, max_tokens: int = 10000) -> str:
        """Generate prompt-friendly summary of repository."""
        lines = [
            f"# Repository: {self.name}",
            f"Path: {self.path}",
            ""
        ]

        # Stats
        lines.extend([
            "## Statistics",
            f"- Total Files: {self.total_files}",
            f"- Total Lines of Code: {self.total_lines}",
        ])

        if self.test_coverage is not None:
            lines.append(f"- Test Coverage: {self.test_coverage:.1f}%")

        if self.git_info:
            if 'commit_count' in self.git_info:
                lines.append(f"- Git Commits: {self.git_info['commit_count']}")
            if 'contributors' in self.git_info:
                lines.append(f"- Contributors: {self.git_info['contributors']}")

        lines.append("")

        # Languages
        if self.languages:
            lines.extend(["## Languages", ""])
            for lang, count in list(self.languages.items())[:10]:
                lines.append(f"- {lang}: {count:,} lines")
            lines.append("")

        # Dependencies (summarized)
        if self.dependencies:
            lines.extend(["## Key Dependencies", ""])
            # Group by package manager
            by_manager: Dict[str, List[str]] = {}
            for dep in self.dependencies[:50]:
                parts = dep.split(':', 1)
                manager = parts[0] if len(parts) > 1 else 'other'
                pkg = parts[1] if len(parts) > 1 else dep
                if manager not in by_manager:
                    by_manager[manager] = []
                by_manager[manager].append(pkg)

            for manager, pkgs in by_manager.items():
                lines.append(f"**{manager}**: {', '.join(pkgs[:15])}")
                if len(pkgs) > 15:
                    lines.append(f"  ... and {len(pkgs) - 15} more")
            lines.append("")

        # Structure (compact)
        lines.extend(["## Structure", "```"])
        lines.append(self._format_structure(self.structure, max_depth=3))
        lines.append("```\n")

        # README
        if self.readme:
            lines.extend(["## README (excerpt)", ""])
            readme_excerpt = self.readme[:2000]
            if len(self.readme) > 2000:
                readme_excerpt += "\n... [truncated]"
            lines.append(readme_excerpt)
            lines.append("")

        # Key files (if space permits)
        context = "\n".join(lines)
        estimated_tokens = len(context) // 4

        if estimated_tokens < max_tokens * 0.7:
            remaining_tokens = max_tokens - estimated_tokens
            chars_per_file = (remaining_tokens * 4) // max(len(self.key_files), 1)

            lines.extend(["## Key Files", ""])
            for filepath, content in list(self.key_files.items())[:10]:
                if filepath.lower() in ['readme.md', 'readme.rst', 'readme.txt', 'readme']:
                    continue  # Already included

                excerpt = content[:min(chars_per_file, 1500)]
                if len(content) > len(excerpt):
                    excerpt += "\n... [truncated]"

                lines.extend([
                    f"### {filepath}",
                    "```",
                    excerpt,
                    "```",
                    ""
                ])

        return "\n".join(lines)

    def _format_structure(self, structure: Dict[str, Any], indent: int = 0, max_depth: int = 3) -> str:
        """Format structure as tree string."""
        if indent > max_depth * 2:
            return ""

        lines = []
        children = structure.get("children", {})

        for name, info in list(children.items())[:30]:  # Limit items
            prefix = "  " * indent
            if info.get("type") == "directory":
                lines.append(f"{prefix}{name}/")
                if indent < max_depth * 2:
                    sub = self._format_structure(info, indent + 1, max_depth)
                    if sub:
                        lines.append(sub)
            else:
                size = info.get("size", 0)
                size_str = f" ({size:,} bytes)" if size > 10000 else ""
                lines.append(f"{prefix}{name}{size_str}")

        if len(children) > 30:
            lines.append(f"{'  ' * indent}... and {len(children) - 30} more")

        return "\n".join(lines)

    def get_file_content(self, relative_path: str, max_size: int = 100000) -> Optional[str]:
        """Get content of a specific file."""
        file_path = self.path / relative_path
        if not file_path.exists() or not file_path.is_file():
            return None

        try:
            if file_path.stat().st_size > max_size:
                return None
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except (PermissionError, OSError):
            return None

    def search_files(self, pattern: str, file_pattern: str = "*") -> List[Tuple[str, int, str]]:
        """Search for pattern in files, return (file, line_num, line_content)."""
        results: List[Tuple[str, int, str]] = []
        regex = re.compile(pattern, re.IGNORECASE)

        for file_path in self.path.rglob(file_pattern):
            if not file_path.is_file():
                continue

            path_str = str(file_path)
            if any(skip in path_str for skip in [
                'node_modules', '__pycache__', '.git', 'venv', '.venv'
            ]):
                continue

            try:
                with file_path.open(encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            rel_path = str(file_path.relative_to(self.path))
                            results.append((rel_path, line_num, line.strip()))

                            if len(results) >= 100:  # Limit results
                                return results
            except (PermissionError, OSError):
                continue

        return results


@runtime_checkable
class ModelClient(Protocol):
    """Protocol for LLM model clients."""
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Generate completion for prompt."""
        ...


@runtime_checkable
class RestoredMind(Protocol):
    """Protocol for restored minds."""
    name: str
    identity: str
    expertise_areas: List[str]


class RepositoryEvaluator:
    """Evaluates repositories using restored minds."""

    DEFAULT_BATCH_SIZE = 5
    MAX_RETRIES = 3

    def __init__(self, restored_mind: RestoredMind, model_client: ModelClient):
        self.mind = restored_mind
        self.model_client = model_client

    def build_evaluation_prompt(
        self,
        repo_context: RepositoryContext,
        benchmark: Benchmark,
        batch_size: int = 5
    ) -> str:
        """Build prompt for answering benchmark questions."""
        # Get context summary
        context_summary = repo_context.to_prompt_context(max_tokens=8000)

        # Build mind identity preamble
        mind_identity = f"""You are {self.mind.name}, evaluating this repository based on your expertise and perspective.

{self.mind.identity}

You will evaluate this repository according to your standards, principles, and areas of expertise."""

        # Build questions section
        questions_text = []
        for i, q in enumerate(benchmark.questions[:batch_size], 1):
            q_text = f"{i}. [{q.category}] {q.text}"
            if q.sub_questions:
                for sq in q.sub_questions:
                    q_text += f"\n   - {sq}"
            if q.evaluation_criteria:
                q_text += f"\n   Criteria: {', '.join(q.evaluation_criteria)}"
            questions_text.append(q_text)

        prompt = f"""{mind_identity}

# Repository Context

{context_summary}

# Evaluation Task

Evaluate this repository by answering the following benchmark questions. For each question:

1. Provide a detailed answer based on the repository evidence
2. Assign a score from 1-10 where:
   - 1-3: Serious deficiencies
   - 4-5: Below expectations
   - 6-7: Meets basic standards
   - 8-9: Exceeds expectations
   - 10: Exemplary
3. Cite specific evidence from the repository (file paths, code excerpts)
4. Provide actionable recommendations
5. Rate your confidence (0.0-1.0) in this assessment

# Questions to Answer

{chr(10).join(questions_text)}

# Response Format

For each question, respond in this exact JSON format:

```json
{{
  "answers": [
    {{
      "question_id": "Q1",
      "answer": "Your detailed answer here",
      "score": 7,
      "reasoning": "Explanation of why this score was given",
      "evidence": [
        {{
          "file_path": "path/to/file.py",
          "line_numbers": [10, 25],
          "excerpt": "relevant code excerpt",
          "relevance": "Why this evidence matters"
        }}
      ],
      "recommendations": [
        "Specific recommendation 1",
        "Specific recommendation 2"
      ],
      "confidence": 0.85
    }}
  ]
}}
```

Provide your evaluation now, staying true to your identity and expertise as {self.mind.name}."""

        return prompt

    def parse_answers(
        self,
        response: str,
        questions: List[BenchmarkQuestion]
    ) -> List[QuestionAnswer]:
        """Parse answers from model response."""
        answers: List[QuestionAnswer] = []

        # Try to extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*"answers".*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Fallback: create default answers
                return self._create_fallback_answers(questions, response)

        try:
            data = json.loads(json_str)
            answer_list = data.get("answers", [])

            for i, q in enumerate(questions):
                if i < len(answer_list):
                    a_data = answer_list[i]

                    # Parse evidence
                    evidence = []
                    for e_data in a_data.get("evidence", []):
                        line_nums = e_data.get("line_numbers")
                        if isinstance(line_nums, list) and len(line_nums) >= 2:
                            line_nums = (line_nums[0], line_nums[1])
                        else:
                            line_nums = None

                        evidence.append(Evidence(
                            file_path=e_data.get("file_path", ""),
                            line_numbers=line_nums,
                            excerpt=e_data.get("excerpt", ""),
                            relevance=e_data.get("relevance", "")
                        ))

                    score = int(a_data.get("score", 5))
                    score = max(1, min(10, score))

                    answers.append(QuestionAnswer(
                        question=q,
                        answer=a_data.get("answer", "No answer provided"),
                        score=score,
                        score_level=ScoreLevel.from_score(score),
                        evidence=evidence,
                        recommendations=a_data.get("recommendations", []),
                        confidence=float(a_data.get("confidence", 0.7)),
                        reasoning=a_data.get("reasoning", "")
                    ))
                else:
                    # Question not answered
                    answers.append(self._create_unanswered(q))

        except json.JSONDecodeError:
            return self._create_fallback_answers(questions, response)

        return answers

    def _create_fallback_answers(
        self,
        questions: List[BenchmarkQuestion],
        response: str
    ) -> List[QuestionAnswer]:
        """Create fallback answers when parsing fails."""
        return [
            QuestionAnswer(
                question=q,
                answer=f"Unable to parse structured response. Raw response excerpt: {response[:500]}...",
                score=5,
                score_level=ScoreLevel.MEETS,
                evidence=[],
                recommendations=["Re-run evaluation with improved prompting"],
                confidence=0.3,
                reasoning="Parsing failed, using fallback"
            )
            for q in questions
        ]

    def _create_unanswered(self, question: BenchmarkQuestion) -> QuestionAnswer:
        """Create placeholder for unanswered question."""
        return QuestionAnswer(
            question=question,
            answer="Question was not answered in the evaluation",
            score=5,
            score_level=ScoreLevel.MEETS,
            evidence=[],
            recommendations=[],
            confidence=0.0,
            reasoning="Question not answered by evaluator"
        )

    async def evaluate_question_batch(
        self,
        repo_context: RepositoryContext,
        questions: List[BenchmarkQuestion],
        benchmark: Optional[Benchmark] = None
    ) -> List[QuestionAnswer]:
        """Evaluate a batch of questions."""
        if not questions:
            return []

        # Create a temporary benchmark for this batch
        batch_benchmark = Benchmark(
            name="Batch Evaluation",
            description="Batch of questions for evaluation",
            questions=questions
        )

        prompt = self.build_evaluation_prompt(
            repo_context,
            batch_benchmark,
            batch_size=len(questions)
        )

        # Call model with retries
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.model_client.complete(prompt)
                answers = self.parse_answers(response, questions)

                # Validate we got answers
                if answers and all(a.confidence > 0 for a in answers):
                    return answers

            except Exception as e:
                if attempt == self.MAX_RETRIES - 1:
                    # Return fallback on final failure
                    return self._create_fallback_answers(
                        questions,
                        f"Evaluation failed after {self.MAX_RETRIES} attempts: {str(e)}"
                    )

        return self._create_fallback_answers(questions, "Max retries exceeded")

    async def evaluate_repository(
        self,
        repo_path: Path,
        benchmark: Benchmark
    ) -> EvaluationReport:
        """Full repository evaluation."""
        start_time = datetime.now()

        # Build repository context
        repo_context = RepositoryContext.from_path(repo_path)

        # Evaluate in batches
        all_answers: List[QuestionAnswer] = []
        batch_size = self.DEFAULT_BATCH_SIZE

        for i in range(0, len(benchmark.questions), batch_size):
            batch = benchmark.questions[i:i + batch_size]
            batch_answers = await self.evaluate_question_batch(
                repo_context, batch, benchmark
            )
            all_answers.extend(batch_answers)

        # Calculate overall score
        if all_answers:
            total_weight = sum(
                a.question.weight * a.confidence for a in all_answers
                if hasattr(a.question, 'weight')
            )
            if total_weight > 0:
                overall_score = sum(a.weighted_score() for a in all_answers) / total_weight
            else:
                overall_score = sum(a.score for a in all_answers) / len(all_answers)
        else:
            overall_score = 0.0

        # Generate summary
        executive_summary, strengths, weaknesses, recommendations = await self._generate_summary(
            repo_context, all_answers
        )

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Build repository stats
        repo_stats = {
            "total_files": repo_context.total_files,
            "total_lines": repo_context.total_lines,
            "primary_language": list(repo_context.languages.keys())[0] if repo_context.languages else "Unknown",
            "dependency_count": len(repo_context.dependencies),
        }
        if repo_context.test_coverage is not None:
            repo_stats["test_coverage"] = f"{repo_context.test_coverage:.1f}%"
        if repo_context.git_info.get("commit_count"):
            repo_stats["commits"] = repo_context.git_info["commit_count"]

        return EvaluationReport(
            mind_name=self.mind.name,
            repository_name=repo_context.name,
            answers=all_answers,
            overall_score=overall_score,
            executive_summary=executive_summary,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            evaluation_duration_seconds=duration,
            repository_stats=repo_stats
        )

    async def _generate_summary(
        self,
        repo_context: RepositoryContext,
        answers: List[QuestionAnswer]
    ) -> Tuple[str, List[str], List[str], List[str]]:
        """Generate executive summary, strengths, weaknesses, and recommendations."""
        # Analyze answers
        high_scores = [a for a in answers if a.score >= 8]
        low_scores = [a for a in answers if a.score <= 4]

        # Extract strengths from high-scoring answers
        strengths = []
        for a in high_scores[:5]:
            if a.reasoning:
                strengths.append(f"{a.question.category}: {a.reasoning[:100]}...")
            else:
                strengths.append(f"{a.question.category}: Scored {a.score}/10")

        # Extract weaknesses from low-scoring answers
        weaknesses = []
        for a in low_scores[:5]:
            if a.reasoning:
                weaknesses.append(f"{a.question.category}: {a.reasoning[:100]}...")
            else:
                weaknesses.append(f"{a.question.category}: Scored only {a.score}/10")

        # Collect unique recommendations
        recommendations = []
        seen_recs = set()
        for a in answers:
            for rec in a.recommendations:
                rec_key = rec.lower()[:50]
                if rec_key not in seen_recs:
                    seen_recs.add(rec_key)
                    recommendations.append(rec)
                    if len(recommendations) >= 10:
                        break
            if len(recommendations) >= 10:
                break

        # Generate executive summary
        avg_score = sum(a.score for a in answers) / len(answers) if answers else 0
        level = ScoreLevel.from_score(int(avg_score))

        category_scores = {}
        for a in answers:
            cat = a.question.category
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(a.score)

        cat_avgs = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_scores.items()
        }
        best_cat = max(cat_avgs.items(), key=lambda x: x[1])[0] if cat_avgs else "N/A"
        worst_cat = min(cat_avgs.items(), key=lambda x: x[1])[0] if cat_avgs else "N/A"

        executive_summary = f"""This repository **{repo_context.name}** has been evaluated from the perspective of {self.mind.name}.

**Overall Assessment**: {level.description} (Score: {avg_score:.1f}/10)

The repository shows its greatest strength in **{best_cat}** and has the most room for improvement in **{worst_cat}**.

**Key Statistics**:
- {repo_context.total_files:,} files analyzed
- {repo_context.total_lines:,} lines of code
- Primary language: {list(repo_context.languages.keys())[0] if repo_context.languages else 'Unknown'}
- {len(high_scores)} areas of excellence identified
- {len(low_scores)} areas requiring attention

This evaluation reflects the standards and principles associated with {self.mind.name}'s expertise and philosophy."""

        return executive_summary, strengths, weaknesses, recommendations

    async def deep_dive(
        self,
        repo_context: RepositoryContext,
        area: str
    ) -> Dict[str, Any]:
        """Request deeper examination of specific area."""
        prompt = f"""You are {self.mind.name}. Perform a deep dive analysis of the "{area}" aspect of this repository.

# Repository: {repo_context.name}

{repo_context.to_prompt_context(max_tokens=10000)}

# Deep Dive Request

Provide an in-depth analysis of: **{area}**

Cover:
1. Current state assessment
2. Specific findings with file/line references
3. Best practices comparison
4. Detailed recommendations
5. Priority ranking of issues

Respond in JSON format:
```json
{{
  "area": "{area}",
  "overall_assessment": "summary",
  "findings": [
    {{
      "title": "Finding title",
      "severity": "high|medium|low",
      "description": "detailed description",
      "file_path": "path/to/file",
      "line_numbers": [start, end],
      "recommendation": "what to do"
    }}
  ],
  "best_practices": ["practice 1", "practice 2"],
  "action_items": [
    {{
      "priority": 1,
      "action": "specific action",
      "effort": "low|medium|high",
      "impact": "low|medium|high"
    }}
  ]
}}
```"""

        try:
            response = await self.model_client.complete(prompt)

            # Parse JSON response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try raw JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            return {
                "area": area,
                "overall_assessment": response[:500],
                "findings": [],
                "best_practices": [],
                "action_items": [],
                "raw_response": response
            }

        except Exception as e:
            return {
                "area": area,
                "error": str(e),
                "findings": [],
                "best_practices": [],
                "action_items": []
            }


class MultiMindEvaluator:
    """Coordinates evaluation by multiple minds."""

    def __init__(self, minds: List[RestoredMind], model_client: ModelClient):
        self.minds = minds
        self.model_client = model_client
        self.evaluators = [
            RepositoryEvaluator(mind, model_client)
            for mind in minds
        ]

    async def evaluate_with_all_minds(
        self,
        repo_path: Path,
        benchmarks: Dict[str, Benchmark]  # mind_name -> benchmark
    ) -> 'AggregatedReport':
        """Get evaluations from all minds."""
        # Resolve path to get proper name
        resolved_path = Path(repo_path).resolve()

        # Run evaluations concurrently
        tasks = []
        for evaluator in self.evaluators:
            benchmark = benchmarks.get(evaluator.mind.name)
            if benchmark:
                tasks.append(
                    evaluator.evaluate_repository(repo_path, benchmark)
                )

        reports = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_reports: List[EvaluationReport] = [
            r for r in reports
            if isinstance(r, EvaluationReport)
        ]

        return AggregatedReport.from_reports(
            repository_name=resolved_path.name,
            reports=valid_reports
        )

    async def evaluate_with_single_benchmark(
        self,
        repo_path: Path,
        benchmark: Benchmark
    ) -> 'AggregatedReport':
        """Evaluate with all minds using the same benchmark."""
        benchmarks = {mind.name: benchmark for mind in self.minds}
        return await self.evaluate_with_all_minds(repo_path, benchmarks)


@dataclass
class AggregatedReport:
    """Aggregated report from multiple minds."""
    repository_name: str
    individual_reports: List[EvaluationReport]
    consensus_score: float
    score_variance: float
    consensus_strengths: List[str]
    consensus_weaknesses: List[str]
    dissenting_opinions: Dict[str, str]
    category_consensus: Dict[str, float] = field(default_factory=dict)
    evaluation_timestamp: str = ""

    @classmethod
    def from_reports(
        cls,
        repository_name: str,
        reports: List[EvaluationReport]
    ) -> 'AggregatedReport':
        """Create aggregated report from individual reports."""
        if not reports:
            return cls(
                repository_name=repository_name,
                individual_reports=[],
                consensus_score=0.0,
                score_variance=0.0,
                consensus_strengths=[],
                consensus_weaknesses=[],
                dissenting_opinions={},
                category_consensus={},
                evaluation_timestamp=datetime.now().isoformat()
            )

        # Calculate consensus score
        scores = [r.overall_score for r in reports]
        consensus_score = sum(scores) / len(scores)

        # Calculate variance
        if len(scores) > 1:
            mean = consensus_score
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            score_variance = variance ** 0.5
        else:
            score_variance = 0.0

        # Find consensus strengths (mentioned by multiple minds)
        strength_counts: Dict[str, int] = {}
        for report in reports:
            for strength in report.strengths:
                # Normalize strength for comparison
                key = strength.lower()[:50]
                strength_counts[key] = strength_counts.get(key, 0) + 1

        consensus_strengths = [
            s for s, count in sorted(strength_counts.items(), key=lambda x: -x[1])
            if count >= max(2, len(reports) // 2)
        ][:5]

        # Find consensus weaknesses
        weakness_counts: Dict[str, int] = {}
        for report in reports:
            for weakness in report.weaknesses:
                key = weakness.lower()[:50]
                weakness_counts[key] = weakness_counts.get(key, 0) + 1

        consensus_weaknesses = [
            w for w, count in sorted(weakness_counts.items(), key=lambda x: -x[1])
            if count >= max(2, len(reports) // 2)
        ][:5]

        # Find dissenting opinions (scores far from mean)
        dissenting_opinions: Dict[str, str] = {}
        if score_variance > 1.0:  # Significant disagreement
            for report in reports:
                diff = abs(report.overall_score - consensus_score)
                if diff > score_variance:
                    direction = "higher" if report.overall_score > consensus_score else "lower"
                    dissenting_opinions[report.mind_name] = (
                        f"Scored {report.overall_score:.1f} ({direction} than consensus of {consensus_score:.1f}). "
                        f"Key perspective: {report.executive_summary[:200]}..."
                    )

        # Category consensus
        category_scores: Dict[str, List[float]] = {}
        for report in reports:
            for cat, score in report.category_scores().items():
                if cat not in category_scores:
                    category_scores[cat] = []
                category_scores[cat].append(score)

        category_consensus = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_scores.items()
        }

        return cls(
            repository_name=repository_name,
            individual_reports=reports,
            consensus_score=consensus_score,
            score_variance=score_variance,
            consensus_strengths=consensus_strengths,
            consensus_weaknesses=consensus_weaknesses,
            dissenting_opinions=dissenting_opinions,
            category_consensus=category_consensus,
            evaluation_timestamp=datetime.now().isoformat()
        )

    def to_markdown(self) -> str:
        """Generate aggregated markdown report."""
        lines = [
            f"# Multi-Mind Repository Evaluation: {self.repository_name}",
            f"**Evaluation Date**: {self.evaluation_timestamp}",
            f"**Evaluators**: {len(self.individual_reports)} minds",
            "",
            "---",
            "",
            "## Consensus Overview",
            "",
            f"**Consensus Score**: {self.consensus_score:.1f}/10",
            f"**Score Variance**: {self.score_variance:.2f} ({"High disagreement" if self.score_variance > 1.5 else "Moderate agreement" if self.score_variance > 0.5 else "Strong consensus"})",
            ""
        ]

        # Individual scores table
        lines.extend([
            "### Individual Evaluator Scores",
            "| Mind | Score | Level |",
            "|------|-------|-------|"
        ])
        for report in sorted(self.individual_reports, key=lambda r: -r.overall_score):
            level = ScoreLevel.from_score(int(report.overall_score))
            lines.append(f"| {report.mind_name} | {report.overall_score:.1f}/10 | {level.description} |")
        lines.append("")

        # Category consensus
        if self.category_consensus:
            lines.extend([
                "### Category Consensus",
                "| Category | Consensus Score |",
                "|----------|-----------------|"
            ])
            for cat, score in sorted(self.category_consensus.items(), key=lambda x: -x[1]):
                level = ScoreLevel.from_score(int(score))
                lines.append(f"| {cat} | {score:.1f}/10 ({level.description}) |")
            lines.append("")

        # Consensus findings
        if self.consensus_strengths:
            lines.extend(["## Consensus Strengths", ""])
            for s in self.consensus_strengths:
                lines.append(f"- {s}")
            lines.append("")

        if self.consensus_weaknesses:
            lines.extend(["## Consensus Weaknesses", ""])
            for w in self.consensus_weaknesses:
                lines.append(f"- {w}")
            lines.append("")

        # Dissenting opinions
        if self.dissenting_opinions:
            lines.extend([
                "## Dissenting Opinions",
                "",
                "The following evaluators had significantly different perspectives:",
                ""
            ])
            for mind, opinion in self.dissenting_opinions.items():
                lines.extend([
                    f"### {mind}",
                    opinion,
                    ""
                ])

        # Individual report summaries
        lines.extend([
            "---",
            "",
            "## Individual Evaluations",
            ""
        ])

        for report in self.individual_reports:
            lines.extend([
                f"### {report.mind_name}",
                f"**Score**: {report.overall_score:.1f}/10",
                "",
                "#### Executive Summary",
                report.executive_summary[:500] + ("..." if len(report.executive_summary) > 500 else ""),
                "",
                "#### Key Strengths",
            ])
            for s in report.strengths[:3]:
                lines.append(f"- {s}")

            lines.append("\n#### Key Weaknesses")
            for w in report.weaknesses[:3]:
                lines.append(f"- {w}")

            lines.extend(["", "---", ""])

        return "\n".join(lines)

    def to_json(self, path: str) -> None:
        """Save aggregated report to JSON."""
        data = {
            "repository_name": self.repository_name,
            "evaluation_timestamp": self.evaluation_timestamp,
            "consensus_score": self.consensus_score,
            "score_variance": self.score_variance,
            "consensus_strengths": self.consensus_strengths,
            "consensus_weaknesses": self.consensus_weaknesses,
            "dissenting_opinions": self.dissenting_opinions,
            "category_consensus": self.category_consensus,
            "individual_scores": {
                r.mind_name: r.overall_score for r in self.individual_reports
            },
            "individual_reports": [
                {
                    "mind_name": r.mind_name,
                    "overall_score": r.overall_score,
                    "executive_summary": r.executive_summary,
                    "strengths": r.strengths,
                    "weaknesses": r.weaknesses,
                    "recommendations": r.recommendations,
                    "category_scores": r.category_scores(),
                    "answer_count": len(r.answers)
                }
                for r in self.individual_reports
            ]
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Utility functions for common operations

def create_default_benchmark() -> Benchmark:
    """Create a default benchmark for general repository evaluation."""
    return Benchmark(
        name="General Repository Quality",
        description="Standard benchmark for evaluating code repository quality",
        questions=[
            BenchmarkQuestion(
                id="code-quality-1",
                text="How well is the code organized and structured?",
                category="Code Quality",
                weight=1.5,
                sub_questions=[
                    "Is there clear separation of concerns?",
                    "Are files and directories logically organized?",
                    "Is the code modular and reusable?"
                ],
                evaluation_criteria=["Organization", "Modularity", "Readability"]
            ),
            BenchmarkQuestion(
                id="code-quality-2",
                text="How well does the code follow language-specific best practices?",
                category="Code Quality",
                weight=1.0,
                evaluation_criteria=["Style", "Idioms", "Patterns"]
            ),
            BenchmarkQuestion(
                id="docs-1",
                text="How comprehensive and helpful is the documentation?",
                category="Documentation",
                weight=1.2,
                sub_questions=[
                    "Is there a clear README?",
                    "Are APIs well-documented?",
                    "Are there usage examples?"
                ]
            ),
            BenchmarkQuestion(
                id="testing-1",
                text="How thorough is the test coverage?",
                category="Testing",
                weight=1.3,
                evaluation_criteria=["Coverage", "Quality", "Types of tests"]
            ),
            BenchmarkQuestion(
                id="security-1",
                text="Are there any obvious security concerns?",
                category="Security",
                weight=1.5,
                sub_questions=[
                    "Are secrets properly managed?",
                    "Are dependencies secure?",
                    "Is input validation present?"
                ]
            ),
            BenchmarkQuestion(
                id="maintainability-1",
                text="How maintainable is this codebase?",
                category="Maintainability",
                weight=1.2,
                evaluation_criteria=["Complexity", "Dependencies", "Technical debt"]
            ),
        ]
    )


async def quick_evaluate(
    repo_path: str,
    mind_name: str,
    mind_identity: str,
    model_client: ModelClient
) -> EvaluationReport:
    """Quick evaluation with minimal setup."""

    @dataclass
    class SimpleMind:
        name: str
        identity: str
        expertise_areas: List[str] = field(default_factory=list)

    mind = SimpleMind(name=mind_name, identity=mind_identity)
    evaluator = RepositoryEvaluator(mind, model_client)
    benchmark = create_default_benchmark()

    return await evaluator.evaluate_repository(Path(repo_path), benchmark)


# Example mock client for testing
class MockModelClient:
    """Mock model client for testing."""

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Return mock response."""
        return '''```json
{
  "answers": [
    {
      "question_id": "Q1",
      "answer": "The repository demonstrates good organization with clear separation of concerns.",
      "score": 7,
      "reasoning": "Code is modular but could benefit from better documentation.",
      "evidence": [
        {
          "file_path": "src/main.py",
          "line_numbers": [1, 50],
          "excerpt": "# Main module with clear structure",
          "relevance": "Shows good organization"
        }
      ],
      "recommendations": [
        "Add more inline documentation",
        "Consider splitting large modules"
      ],
      "confidence": 0.85
    }
  ]
}
```'''


if __name__ == "__main__":
    # Example usage demonstration
    import asyncio

    async def demo():
        # Create mock client
        client = MockModelClient()

        # Create a simple mind
        @dataclass
        class DemoMind:
            name: str = "Demo Evaluator"
            identity: str = "A software quality expert focused on clean code principles."
            expertise_areas: List[str] = field(default_factory=lambda: ["Code Quality", "Testing"])

        mind = DemoMind()
        evaluator = RepositoryEvaluator(mind, client)

        # Create benchmark
        benchmark = create_default_benchmark()

        print("Repository Evaluation Engine Demo")
        print("=" * 50)
        print(f"Mind: {mind.name}")
        print(f"Benchmark: {benchmark.name}")
        print(f"Questions: {len(benchmark.questions)}")
        print()

        # Show benchmark questions
        for q in benchmark.questions:
            print(f"  [{q.category}] {q.text}")

        print()
        print("To evaluate a repository, use:")
        print("  report = await evaluator.evaluate_repository(Path('/path/to/repo'), benchmark)")
        print("  print(report.to_markdown())")

    asyncio.run(demo())
