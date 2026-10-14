"""Check the linked project foundation without application dependencies."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TASK = r"(?:DOC|BE|FE|REL)-\d{3}"
REQUIREMENT = r"(?:FR|NFR|DATA|SEC)-\d{3}"
CONCEPT_NAMES = (
    "Requirements analysis",
    "High-level architecture",
    "Low-level design",
    "Separation of concerns",
    "Modular monolith",
    "Data-flow design",
    "API contract design",
    "Architecture decision records",
    "Component-driven architecture",
    "Component composition",
    "Separation of UI and business logic",
    "State management",
    "Server state versus UI state",
    "API client architecture",
    "UI state machine",
    "Responsive design",
    "Accessibility",
    "Data visualization architecture",
    "Frontend performance",
    "Error recovery",
    "Frontend testing",
    "Layered architecture",
    "REST API design",
    "Request validation",
    "Provider adapter pattern",
    "Data ingestion pipeline",
    "Climate-analysis engine",
    "Data normalization",
    "Error-handling architecture",
    "Idempotency",
    "Asynchronous processing",
    "Dependency injection",
    "Background jobs",
    "API versioning",
    "MongoDB Atlas data modeling",
    "Indexing",
    "Data integrity",
    "Persistent caching",
    "Analysis-result caching",
    "Cache invalidation",
    "Cache-key design",
    "Cache concurrency",
    "Data provenance",
    "Data retention",
    "Provider fallback",
    "Timeouts",
    "Bounded retries",
    "Backoff",
    "Circuit breaker",
    "Rate limiting",
    "Graceful degradation",
    "Provider health monitoring",
    "Data-consistency policy",
    "Partial-data handling",
    "Heatwave detection algorithm",
    "Percentile baseline",
    "Temporal aggregation",
    "Spatial aggregation",
    "Missing-data strategy",
    "Boundary conditions",
    "Trend estimation",
    "Statistical significance",
    "Reproducibility",
    "Insight generation",
    "Secret management",
    "Input security",
    "Network security",
    "External request security",
    "Resource limits",
    "Observability",
    "Performance measurement",
    "Scaling strategy",
    "Dependency management",
    "Deployment configuration",
    "Health checks",
    "Unit testing",
    "Integration testing",
    "Contract testing",
    "End-to-end testing",
    "Failure testing",
    "Responsive testing",
    "Task traceability",
    "Small changes and commits",
    "Documentation maintenance",
    "Continuous integration",
)

REQUIRED = (
    "AGENTS.md", "README.md", "PRD.md", "ARCHITECTURE.md", "AI_WORKFLOW.md",
    "INTEGRATION_CONTRACT.md", "PROJECT_STATE.md", "PRODUCT.md", "DESIGN.md",
    "TASKS.md", "docs/skills-and-tools.md", "docs/ai-development-workflow.md", "docs/workspace-audit.md",
    "docs/verification.md", "frontend/AGENTS.md", "backend/AGENTS.md",
    "frontend/docs/system.frontend.md", "backend/docs/system.backend.md",
    "frontend/docs/design.md", "frontend/docs/responsiveness.md", "frontend/docs/memory.permissions.md",
    "backend/docs/climate-methodology.md", "backend/docs/database.md",
    "docs/system-design-audit.md", "docs/system-design-coverage.md",
)


def links_and_fences(documents: dict[Path, str]) -> list[str]:
    errors = []
    for path, source in documents.items():
        if len(re.findall(r"^```", source, re.MULTILINE)) % 2:
            errors.append(f"{path.name}: unbalanced fenced code")
        prose = re.sub(r"```.*?```", "", source, flags=re.DOTALL)
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", prose):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            destination = path.parent / unquote(parsed.path)
            if not destination.exists():
                errors.append(f"{path.name}: missing link target {target}")
    return errors


def task_checks(documents: dict[Path, str]) -> tuple[list[str], int]:
    errors = []
    definitions: dict[str, str] = {}
    for path, source in documents.items():
        sections = re.split(r"(?=^## )", source, flags=re.MULTILINE)
        for section in sections:
            match = re.match(rf"## ({TASK})\b", section)
            if not match:
                continue
            task_id = match[1]
            if task_id in definitions:
                errors.append(f"duplicate task definition {task_id}")
            definitions[task_id] = section
            status = re.search(r"Status: ([A-Z_]+)\.", section)
            if not status or status[1] not in {"TODO", "IN_PROGRESS", "BLOCKED", "DONE"}:
                errors.append(f"{task_id}: missing/invalid status")
            for label in ("Priority:", "Requirements:", "Dependencies:", "Acceptance:", "Evidence:",
                          "Description:", "Ownership:", "Concepts:", "Required tests:",
                          "Documents/files:", "Blockers:"):
                if label.lower() not in section.lower():
                    errors.append(f"{task_id}: missing {label}")
            owner = re.search(r"Ownership: (shared|frontend|backend)\.", section)
            if not owner:
                errors.append(f"{task_id}: missing/invalid ownership")
            concepts = re.search(r"Concepts: ([\d, ]+)\.", section)
            numbers = [int(n) for n in re.findall(r"\d+", concepts[1])] if concepts else []
            if not numbers or len(numbers) != len(set(numbers)) or any(n < 1 or n > 85 for n in numbers):
                errors.append(f"{task_id}: missing/invalid concept IDs")
            if status and status[1] == "DONE":
                evidence = re.search(r"Evidence: ([^\n]+)", section)
                if not evidence or evidence[1].strip().lower().startswith(("none", "pending")):
                    errors.append(f"{task_id}: DONE without evidence")
    for path, source in documents.items():
        for task_id in set(re.findall(rf"\b{TASK}\b", source)) - definitions.keys():
            errors.append(f"{path.name}: undefined task {task_id}")
    graph = {}
    for task_id, section in definitions.items():
        dependencies = re.search(r"Dependencies: ([^.\n]+)", section)
        graph[task_id] = re.findall(TASK, dependencies[1]) if dependencies else []
    visited, active = set(), set()

    def visit(task_id: str) -> None:
        if task_id in active:
            errors.append(f"dependency cycle at {task_id}")
            return
        if task_id in visited or task_id not in graph:
            return
        active.add(task_id)
        for dependency in graph[task_id]:
            visit(dependency)
        active.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)
    for path, source in documents.items():
        for task_id, summary_status in re.findall(
            rf"^\| ({TASK}) \| (TODO|IN_PROGRESS|BLOCKED|DONE) \|", source, re.MULTILINE
        ):
            definition = definitions.get(task_id, "")
            actual = re.search(r"Status: ([A-Z_]+)\.", definition)
            if not actual or actual[1] != summary_status:
                errors.append(f"{path.name}: summary status differs for {task_id}")
    return errors, len(definitions)


def concept_checks(documents: dict[Path, str]) -> list[str]:
    errors = []
    source = documents.get(ROOT / "docs/system-design-coverage.md", "")
    rows = [line for line in source.splitlines() if re.match(r"^\| \d+ \|", line)]
    ids = [int(line.split("|")[1].strip()) for line in rows]
    if len(ids) != 85 or set(ids) != set(range(1, 86)):
        errors.append("coverage: expected IDs 1–85 exactly once")
    task_concepts = {}
    for text in documents.values():
        for section in re.split(r"(?=^## )", text, flags=re.MULTILINE):
            match = re.match(rf"## ({TASK})\b", section)
            if match:
                concepts = re.search(r"Concepts: ([\d, ]+)\.", section)
                task_concepts[match[1]] = set(map(int, re.findall(r"\d+", concepts[1]))) if concepts else set()
    mapped = {task: set() for task in task_concepts}
    for row in rows:
        cells = [part.strip() for part in row.strip("|").split("|")]
        if len(cells) != 9 or any(not cell for cell in cells):
            errors.append("coverage: each row needs nine nonempty fields")
            continue
        number = int(cells[0])
        if not 1 <= number <= 85:
            continue
        if cells[1] != CONCEPT_NAMES[number - 1]:
            errors.append(f"concept {number}: original name changed")
        if not re.search(r"\[[^\]]+\]\([^)]+\)", cells[3]):
            errors.append(f"concept {number}: no linked authority")
        if cells[6] not in {"Documented", "Planned", "Implemented", "Verified", "Deferred", "Blocked"}:
            errors.append(f"concept {number}: invalid status")
        tasks = re.findall(TASK, cells[5])
        if not tasks:
            errors.append(f"concept {number}: no task")
        for task in tasks:
            if task not in task_concepts:
                errors.append(f"concept {number}: undefined task {task}")
            else:
                mapped[task].add(number)
    for task, declared in task_concepts.items():
        if declared != mapped[task]:
            errors.append(f"{task}: concept mappings are not reciprocal")
    return errors


def requirement_checks(documents: dict[Path, str], prd: str) -> tuple[list[str], int]:
    defined = re.findall(rf"^\| ({REQUIREMENT}) \|", prd, re.MULTILINE)
    errors = []
    if len(defined) != len(set(defined)):
        errors.append("duplicate requirement definition in PRD")
    for path, source in documents.items():
        for ref in set(re.findall(rf"\b{REQUIREMENT}\b", source)) - set(defined):
            errors.append(f"{path.name}: undefined requirement {ref}")
    return errors, len(defined)


def contrast(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
        return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def design_checks(source: str) -> tuple[list[str], list[str]]:
    """Check the canonical monochrome tokens, not rendered UI accessibility."""
    tokens = dict(re.findall(r"\| `(--color-[\w-]+)` \| `([^`]+)`", source))
    errors, reports = [], []
    for name, value in tokens.items():
        if re.fullmatch(r"#[\dA-Fa-f]{6}", value):
            if len({value[i:i + 2].lower() for i in (1, 3, 5)}) != 1:
                errors.append(f"non-grayscale design token {name}")
        else:
            rgba = re.fullmatch(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*(0(?:\.\d+)?|1(?:\.0+)?)\)", value)
            if not rgba or len(set(rgba.group(1, 2, 3))) != 1 or int(rgba[1]) > 255:
                errors.append(f"unsupported/non-grayscale design token {name}")
    pairs = (
        ("text-primary", "bg", 4.5), ("text-primary", "surface-1", 4.5),
        ("text-secondary", "surface-1", 4.5), ("text-secondary", "surface-2", 4.5),
        ("text-secondary", "surface-hover", 4.5), ("text-supporting", "surface-2", 4.5),
        ("control-primary-text", "control-primary", 4.5),
        ("control-border", "surface-2", 3), ("control-border", "surface-hover", 3),
        ("focus", "surface-2", 3), ("chart-primary", "surface-2", 3),
        ("chart-secondary", "surface-2", 3), ("chart-tertiary", "surface-2", 3),
    )
    for foreground, background, minimum in pairs:
        values = [tokens.get(f"--color-{name}", "") for name in (foreground, background)]
        if not all(re.fullmatch(r"#[\dA-Fa-f]{6}", value) for value in values):
            errors.append(f"missing/non-opaque contrast tokens: {foreground}/{background}")
            continue
        ratio = contrast(*values)
        reports.append(f"CONTRAST {foreground}/{background}: {ratio:.2f}:1 (minimum {minimum}:1)")
        if ratio < minimum:
            errors.append(f"contrast below target: {foreground}/{background}")
    return errors, reports


def self_test() -> None:
    good = ROOT / "good.md"
    with patch.object(Path, "exists", return_value=True):
        assert not links_and_fences({good: "[self](good.md)"})
    with patch.object(Path, "exists", return_value=False):
        assert links_and_fences({good: "[missing](absent.md)"})
    assert links_and_fences({good: "```python\nunclosed"})
    section = ("## BE-001 Example\nPriority: P0. Status: TODO. Requirements: FR-001. "
               "Dependencies: BE-002.\nAcceptance: checked. Evidence: none.\n")
    second = section.replace("## BE-001", "## BE-002").replace("Dependencies: BE-002", "Dependencies: BE-001")
    assert any("cycle" in e for e in task_checks({good: section + second})[0])
    assert any("duplicate" in e for e in task_checks({good: section + section})[0])
    assert any("undefined" in e for e in task_checks({good: section})[0])
    assert requirement_checks({good: "FR-002"}, "| FR-001 | example |")[0]
    assert abs(contrast("#000000", "#FFFFFF") - 21) < 1e-9
    assert contrast("#101010", "#101010") == 1
    assert any("missing Description" in e for e in task_checks({good: section})[0])
    coverage_path = ROOT / "docs/system-design-coverage.md"
    valid_rows = "\n".join(
        f"| {n} | {name} | Decision | [Doc](../PRD.md) | Module | BE-001 | Planned | Test | Pending |"
        for n, name in enumerate(CONCEPT_NAMES, 1)
    )
    task_text = "## BE-001 Example\nConcepts: " + ", ".join(map(str, range(1, 86))) + ".\n"
    assert not concept_checks({coverage_path: valid_rows, good: task_text})
    assert concept_checks({coverage_path: valid_rows.split("\n", 1)[1], good: task_text})
    assert concept_checks({coverage_path: valid_rows + "\n" + valid_rows.splitlines()[0], good: task_text})
    assert concept_checks({coverage_path: valid_rows.replace("| Planned |", "| DONE |", 1), good: task_text})
    assert concept_checks({coverage_path: valid_rows.replace("BE-001", "BE-099", 1), good: task_text})
    assert concept_checks({coverage_path: valid_rows, good: "## BE-001 Example\nConcepts: 1.\n"})
    summary = section + "\n| BE-001 | DONE | incorrect summary |"
    assert any("summary status" in e for e in task_checks({good: summary})[0])
    palette = {
        "bg": "#000000", "surface-1": "#0A0A0A", "surface-2": "#111111",
        "surface-hover": "#1C1C1C", "text-primary": "#FFFFFF", "text-secondary": "#888888",
        "text-supporting": "#B3B3B3", "control-primary-text": "#000000",
        "control-primary": "#FFFFFF", "control-border": "#737373", "focus": "#FFFFFF",
        "chart-primary": "#FFFFFF", "chart-secondary": "#A3A3A3", "chart-tertiary": "#707070",
        "overlay": "rgba(0, 0, 0, 0.68)",
    }
    design = "\n".join(f"| `--color-{name}` | `{value}` | Use |" for name, value in palette.items())
    assert not design_checks(design)[0]
    assert any("non-grayscale" in e for e in design_checks(design.replace("#FFFFFF", "#F5B942", 1))[0])
    assert any("contrast below" in e for e in design_checks(design.replace("#737373", "#454545"))[0])
    assert design_checks(design.replace("rgba(0, 0, 0, 0.68)", "rgba(0, 0, 10, 0.68)"))[0]
    assert design_checks("")[0]
    print("PASS: documentation checker self-tests")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    documents = {
        path: path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*.md")
        if not {"node_modules", ".git", ".venv", ".agents", ".uv-cache", ".pytest_cache", ".ruff_cache"}.intersection(path.relative_to(ROOT).parts)
    }
    errors = [f"missing required document {name}" for name in REQUIRED if not (ROOT / name).is_file()]
    errors += links_and_fences(documents)
    task_errors, task_count = task_checks(documents)
    errors += task_errors
    errors += concept_checks(documents)
    requirement_errors, requirement_count = requirement_checks(documents, documents.get(ROOT / "PRD.md", ""))
    errors += requirement_errors
    design_errors, reports = design_checks(documents.get(ROOT / "frontend/docs/design.md", ""))
    errors += design_errors
    for report in reports:
        print(report)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {len(documents)} Markdown files; {requirement_count} requirements; {task_count} unique tasks; 85 concepts; links, fences, metadata, reciprocal mappings, summary statuses, dependency graph, grayscale palette and {len(reports)} token contrast pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
