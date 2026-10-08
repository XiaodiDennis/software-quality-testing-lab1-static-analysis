"""Static-analysis wrapper for KPI Software Quality and Testing Laboratory Work #1.

The module executes pylint, flake8 and bandit when installed. It also performs a
small dependency-free AST/text fallback analysis so the module remains usable
when third-party tools are unavailable.
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Issue:
    tool: str
    severity: str
    line: int
    code: str
    message: str


def run_tool(command: list[str], output_file: Path) -> dict[str, object]:
    """Run an external analysis tool and save both stdout and stderr."""
    executable = shutil.which(command[0])
    if executable is None:
        output_file.write_text(
            f"{command[0]} is not installed. Run: pip install pylint flake8 bandit\n",
            encoding="utf-8",
        )
        return {"tool": command[0], "available": False, "returncode": None}

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    output_file.write_text(
        result.stdout + ("\n--- STDERR ---\n" + result.stderr if result.stderr else ""),
        encoding="utf-8",
    )
    return {
        "tool": command[0],
        "available": True,
        "returncode": result.returncode,
    }


def builtin_analysis(path: Path) -> list[Issue]:
    """Perform a compact fallback static inspection using AST and source text."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    issues: list[Issue] = []

    imported: dict[str, int] = {}
    used_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported[alias.asname or alias.name.split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported[alias.asname or alias.name] = node.lineno
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used_names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", node.name):
                issues.append(Issue("builtin", "warning", node.lineno, "N001", f"Function name '{node.name}' is not snake_case"))
            if ast.get_docstring(node) is None:
                issues.append(Issue("builtin", "info", node.lineno, "D001", f"Function '{node.name}' has no docstring"))
        elif isinstance(node, ast.ClassDef):
            if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", node.name):
                issues.append(Issue("builtin", "warning", node.lineno, "N002", f"Class name '{node.name}' is not PascalCase"))
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and "password" in target.id.lower():
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        issues.append(Issue("builtin", "high", node.lineno, "S001", "Hard-coded password-like string"))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        issues.append(Issue("builtin", "high", node.lineno, "S002", "subprocess.run(..., shell=True) may allow command injection"))
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"randint", "random", "choice"}:
                root = node.func.value
                if isinstance(root, ast.Name) and root.id == "random":
                    issues.append(Issue("builtin", "medium", node.lineno, "S003", "Pseudo-random generator used where security-sensitive use may require secrets"))

    for name, line in imported.items():
        if name not in used_names:
            issues.append(Issue("builtin", "warning", line, "F401", f"Imported name '{name}' is unused"))

    for line_no, line in enumerate(source.splitlines(), start=1):
        if len(line) > 88:
            issues.append(Issue("builtin", "warning", line_no, "E501", f"Line too long ({len(line)} > 88 characters)"))
        if re.match(r"\s*unused_[A-Za-z0-9_]*\s*=", line):
            issues.append(Issue("builtin", "warning", line_no, "F841", "Local variable appears intentionally unused"))

    return sorted(issues, key=lambda item: (item.line, item.code))


def write_builtin_report(issues: list[Issue], target: Path) -> None:
    lines = ["BUILT-IN STATIC ANALYSIS REPORT", "=" * 34, ""]
    for issue in issues:
        lines.append(f"L{issue.line:03d} [{issue.severity.upper():7}] {issue.code}: {issue.message}")
    lines.extend(["", f"Total issues: {len(issues)}"])
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html_report(source_file: Path, issues: list[Issue], tool_status: list[dict[str, object]], target: Path) -> None:
    severity_counts: dict[str, int] = {}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    rows = "\n".join(
        f"<tr><td>{i.line}</td><td>{html.escape(i.severity)}</td><td>{html.escape(i.code)}</td><td>{html.escape(i.message)}</td></tr>"
        for i in issues
    )
    statuses = "".join(
        f"<li>{html.escape(str(item['tool']))}: {'available' if item['available'] else 'not installed'}</li>"
        for item in tool_status
    )
    target.write_text(
        f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><title>Static Analysis Report</title>
<style>body{{font-family:Arial,sans-serif;max-width:1000px;margin:40px auto;line-height:1.5}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:8px;text-align:left}}th{{background:#eee}}code{{background:#f5f5f5;padding:2px 4px}}</style></head>
<body><h1>Static Analysis Report</h1><p><strong>File:</strong> {html.escape(source_file.name)}</p>
<p><strong>Built-in issues:</strong> {len(issues)}; counts by severity: {html.escape(str(severity_counts))}</p>
<h2>External tool status</h2><ul>{statuses}</ul>
<h2>Detected issues</h2><table><thead><tr><th>Line</th><th>Severity</th><th>Code</th><th>Message</th></tr></thead><tbody>{rows}</tbody></table>
<p>Raw outputs are stored as <code>pylint_report.txt</code>, <code>flake8_report.txt</code>, and <code>bandit_report.txt</code>.</p></body></html>""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run static software analysis on a Python source file.")
    parser.add_argument("file", type=Path, help="Python source file to inspect")
    parser.add_argument("--output", type=Path, default=Path("reports"), help="Report directory")
    args = parser.parse_args()

    source_file = args.file.resolve()
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tool_status = [
        run_tool(["pylint", str(source_file)], output_dir / "pylint_report.txt"),
        run_tool(["flake8", str(source_file)], output_dir / "flake8_report.txt"),
        run_tool(["bandit", "-r", str(source_file)], output_dir / "bandit_report.txt"),
    ]

    issues = builtin_analysis(source_file)
    write_builtin_report(issues, output_dir / "builtin_analysis_report.txt")
    write_html_report(source_file, issues, tool_status, output_dir / "static_analysis_report.html")

    summary = {
        "source_file": source_file.name,
        "built_in_issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "tools": tool_status,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Analysis complete. Reports: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
