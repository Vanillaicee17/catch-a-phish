from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def summarize_sca(path: Path) -> dict:
    data = load_json(path)
    if data is None:
        return {"status": "missing", "findings": 0, "details": "No SCA report was produced."}

    vulnerabilities = data.get("vulnerabilities", {}) if isinstance(data, dict) else {}
    warnings = data.get("warnings", {}) if isinstance(data, dict) else {}
    vuln_list = vulnerabilities.get("list") or vulnerabilities.get("found") or []

    if isinstance(vulnerabilities.get("count"), int):
        finding_count = vulnerabilities["count"]
    elif isinstance(vuln_list, list):
        finding_count = len(vuln_list)
    elif vulnerabilities.get("found") is True:
        finding_count = 1
    else:
        finding_count = 0

    warning_count = 0
    if isinstance(warnings, dict):
        for value in warnings.values():
            if isinstance(value, list):
                warning_count += len(value)
            elif isinstance(value, dict) and isinstance(value.get("list"), list):
                warning_count += len(value["list"])

    status = "findings" if finding_count or warning_count else "clean"
    details = f"{finding_count} dependency vulnerabilities, {warning_count} warnings."
    return {
        "status": status,
        "findings": finding_count + warning_count,
        "details": details,
    }


def summarize_semgrep(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        return {"status": "missing", "findings": 0, "details": "No SAST report was produced."}

    results = data.get("results", [])
    severities = Counter()
    for result in results:
        severity = (
            result.get("extra", {})
            .get("severity")
            or result.get("extra", {})
            .get("metadata", {})
            .get("severity")
            or "unknown"
        )
        severities[str(severity).lower()] += 1

    details = ", ".join(f"{count} {severity}" for severity, count in sorted(severities.items())) or "No findings."
    return {
        "status": "findings" if results else "clean",
        "findings": len(results),
        "details": details,
    }


def summarize_trivy(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        return {"status": "missing", "findings": 0, "details": "No container scan report was produced."}

    results = data.get("Results", [])
    severity_counts = Counter()
    finding_count = 0
    for result in results:
        for vulnerability in result.get("Vulnerabilities") or []:
            finding_count += 1
            severity_counts[(vulnerability.get("Severity") or "UNKNOWN").lower()] += 1

    details = ", ".join(f"{count} {severity}" for severity, count in sorted(severity_counts.items())) or "No findings."
    return {
        "status": "findings" if finding_count else "clean",
        "findings": finding_count,
        "details": details,
    }


def summarize_gitleaks(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, list):
        return {"status": "missing", "findings": 0, "details": "No secret detection report was produced."}

    rule_counts = Counter(item.get("RuleID", "unknown") for item in data)
    details = ", ".join(f"{count} {rule_id}" for rule_id, count in sorted(rule_counts.items())) or "No findings."
    return {
        "status": "findings" if data else "clean",
        "findings": len(data),
        "details": details,
    }


def summarize_zap(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        return {"status": "missing", "findings": 0, "details": "No DAST report was produced."}

    severity_counts = Counter()
    finding_count = 0
    for site in data.get("site", []):
        for alert in site.get("alerts", []):
            instances = len(alert.get("instances", [])) or 1
            finding_count += instances
            severity_counts[(alert.get("riskdesc") or alert.get("riskcode") or "unknown").split(" ", 1)[0].lower()] += instances

    details = ", ".join(f"{count} {severity}" for severity, count in sorted(severity_counts.items())) or "No findings."
    return {
        "status": "findings" if finding_count else "clean",
        "findings": finding_count,
        "details": details,
    }


def summarize_branch_protection(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data, dict):
        return {"status": "missing", "findings": 0, "details": "No branch protection audit was produced."}

    if data.get("status") == "configured":
        contexts = ", ".join(data.get("required_status_checks", {}).get("contexts", [])) or "No required checks configured."
        details = (
            f"Protected branch is enabled. "
            f"Approvals required: {data.get('required_pull_request_reviews', {}).get('required_approving_review_count', 0)}. "
            f"Checks: {contexts}."
        )
        return {"status": "configured", "findings": 0, "details": details}

    if data.get("status") == "missing":
        return {
            "status": "action-needed",
            "findings": 1,
            "details": f"Branch `{data.get('branch', 'main')}` is not protected.",
        }

    return {
        "status": "error",
        "findings": 1,
        "details": data.get("error", "Unable to determine branch protection state."),
    }


def render_report(report_data: dict[str, dict]) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# DevSecOps Consolidated Report",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "## Executive Summary",
        "",
        "| Control | Status | Findings | Notes |",
        "| --- | --- | ---: | --- |",
    ]

    total_findings = 0
    for label, summary in report_data.items():
        total_findings += summary["findings"]
        lines.append(
            f"| {label} | {summary['status']} | {summary['findings']} | {summary['details']} |"
        )

    lines.extend(
        [
            "",
            f"Total reported findings across the pipeline: **{total_findings}**",
            "",
            "## Findings By Control",
            "",
        ]
    )

    for label, summary in report_data.items():
        lines.extend(
            [
                f"### {label}",
                "",
                f"- Status: `{summary['status']}`",
                f"- Findings: `{summary['findings']}`",
                f"- Details: {summary['details']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Vulnerability Management Notes",
            "",
            "- SARIF-producing scans are uploaded to GitHub code scanning when available.",
            "- Dependabot configuration is included to keep Cargo, Docker, and GitHub Actions dependencies current.",
            "- This workflow is intentionally non-blocking for findings, so triage must happen from the report artifact and the Security tab.",
            "",
            "## Branch Protection Notes",
            "",
            "- The branch protection audit reports the current state of the default branch.",
            "- Repository admins should require the security workflow checks before merging to `main`.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge DevSecOps scan outputs into a single Markdown report.")
    parser.add_argument("--artifacts-dir", required=True, help="Directory containing downloaded scan artifacts.")
    parser.add_argument("--output", required=True, help="Output Markdown file path.")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    report_data = {
        "Software Composition Analysis (SCA)": summarize_sca(artifacts_dir / "security-sca" / "cargo-audit.json"),
        "Static Application Security Testing (SAST)": summarize_semgrep(artifacts_dir / "security-sast" / "semgrep.json"),
        "Container Scanning": summarize_trivy(artifacts_dir / "security-container" / "trivy-image.json"),
        "Secret Detection": summarize_gitleaks(artifacts_dir / "security-secrets" / "gitleaks.json"),
        "Dynamic Application Security Testing (DAST)": summarize_zap(artifacts_dir / "security-dast" / "zap-api.json"),
        "Branch Protection Audit": summarize_branch_protection(artifacts_dir / "security-branch-protection" / "branch-protection.json"),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(report_data), encoding="utf-8")
    print(output_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
