#!/usr/bin/env python3
"""Small, agent-readable ATAK plugin source preflight."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess

DEFAULT_SEMGREP_CONFIG = Path(__file__).with_name("semgrep.yml")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(result: dict, severity: str, title: str, detail: str, next_action: str) -> None:
    result["findings"].append({"severity": severity, "title": title,
                               "detail": detail, "next_action": next_action})


def run_json_scan(command: list[str], report: Path, log: Path) -> int:
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=600)
        report.write_text(process.stdout)
        log.write_text(process.stderr)
        return process.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        report.write_text("{}\n")
        log.write_text(str(error) + "\n")
        return 127


def record_tool(result: dict, name: str, path: str) -> None:
    try:
        version = subprocess.run([path, "--version"], capture_output=True,
                                 text=True, timeout=30, check=False)
        detail = (version.stdout or version.stderr).strip().splitlines()[0]
    except (OSError, subprocess.TimeoutExpired):
        detail = "version unavailable"
    result.setdefault("tools", {})[name] = {"path": path, "version": detail}


def inspect_source(source: Path, result: dict) -> None:
    if not source.is_dir():
        check(result, "FAIL", "Source directory not found", str(source),
              "Provide the root of the plugin source repository.")
        return
    ignored = {".git", ".gradle", "build", "target", ".cache", "reports",
               ".test-subjects", ".venv", "__pycache__", "graphify-out"}
    files = [path for path in source.rglob("*") if path.is_file() and
             not ignored.intersection(path.relative_to(source).parts)]
    result["source_root"] = str(source)
    result["source_files"] = len(files)
    result["source_inventory"] = [{"path": str(path.relative_to(source)), "sha256": sha256(path)}
                                   for path in sorted(files)]
    result["source_sha256"] = hashlib.sha256(json.dumps(result["source_inventory"], sort_keys=True).encode()).hexdigest()
    gradle = next((path for path in files if path.name in {"build.gradle", "build.gradle.kts"}), None)
    if gradle:
        check(result, "PASS", "Gradle build files found", str(gradle.relative_to(source)), "No action.")
    else:
        check(result, "FAIL", "Gradle build files missing",
              "No build.gradle or build.gradle.kts was found.",
              "Open the plugin repository root or add the ATAK Gradle build files.")
    manifests = [path for path in files if path.name == "AndroidManifest.xml"]
    manifest = next((path for path in manifests if "main" in path.parts), manifests[0] if manifests else None)
    if manifest:
        text = manifest.read_text(errors="replace")
        result["source_manifest"] = str(manifest.relative_to(source))
        check(result, "PASS", "Android manifest found", str(manifest.relative_to(source)), "No action.")
        if "plugin-api" in text or "atakApiVersion" in text:
            check(result, "PASS", "ATAK API metadata appears configured",
                  "The source manifest or build configuration references plugin-api/atakApiVersion.",
                  "Confirm the value matches every ATAK runtime you intend to support.")
        else:
            check(result, "WARN", "ATAK API metadata not obvious",
                  "The source manifest did not visibly contain plugin-api metadata.",
                  "Inspect the merged manifest produced by the Gradle build.")
    else:
        check(result, "FAIL", "Android manifest missing",
              "No source AndroidManifest.xml under a src directory was found.",
              "Open the plugin repository root and verify its Android module.")
    if shutil.which("semgrep"):
        record_tool(result, "semgrep", shutil.which("semgrep") or "")
        check(result, "PASS", "Semgrep available", shutil.which("semgrep") or "", "No action.")
    else:
        check(result, "GAP", "Source SAST not installed",
              "Semgrep Community Edition was not found.",
              "Install the pinned Semgrep version before treating source results as complete.")


def run_source_scans(source: Path, output: Path, result: dict) -> None:
    scans = output / "scans"
    scans.mkdir(parents=True, exist_ok=True)
    semgrep = shutil.which("semgrep")
    if semgrep:
        record_tool(result, "semgrep", semgrep)
        config = Path(os.environ["SEMGREP_CONFIG"]) if os.environ.get("SEMGREP_CONFIG") else DEFAULT_SEMGREP_CONFIG
        config_value = str(config) if config.exists() else "auto"
        command = [semgrep, "scan", "--config", config_value, "--metrics", "off",
                   "--no-git-ignore", "--error", "--json", str(source)]
        result.setdefault("scan_commands", {})["semgrep"] = command
        code = run_json_scan(command,
                             scans / "semgrep.json", scans / "semgrep.log")
        check(result, "PASS" if code == 0 else "FAIL", "Semgrep source scan",
              "Semgrep completed with no findings." if code == 0 else "Semgrep reported findings or failed.",
              "Open scans/semgrep.json, fix every finding, and rerun." if code else "No action.")
    trivy = shutil.which("trivy")
    if trivy:
        record_tool(result, "trivy", trivy)
        report = scans / "trivy.json"
        command = [trivy, "fs", "--scanners", "vuln,secret,misconfig",
                              "--skip-dirs", ".git,.gradle,build,target,.cache,reports",
                              "--exit-code", "1", "--format", "json", str(source)]
        result.setdefault("scan_commands", {})["trivy"] = command
        code = run_json_scan(command, report, scans / "trivy.log")
        check(result, "PASS" if code == 0 else "FAIL", "Trivy source scan",
              "Trivy found no vulnerabilities, secrets, or misconfigurations." if code == 0
              else "Trivy reported findings or failed.",
              "Open scans/trivy.json, fix every finding, and rerun." if code else "No action.")
    else:
        check(result, "GAP", "Trivy source scan unavailable",
              "Trivy was not found on PATH.",
              "Install Trivy before treating dependency and secret results as complete.")
    osv = shutil.which("osv-scanner")
    if osv:
        record_tool(result, "osv-scanner", osv)
        command = [osv, "scan", "source", "--format", "json", "--recursive",
                   "--no-ignore", "--allow-no-lockfiles", str(source)]
        result.setdefault("scan_commands", {})["osv-scanner"] = command
        code = run_json_scan(command,
                             scans / "osv.json", scans / "osv.log")
        check(result, "PASS" if code == 0 else "FAIL", "OSV dependency scan",
              "OSV-Scanner completed without reported advisories." if code == 0
              else "OSV-Scanner reported advisories or failed.",
              "Open scans/osv.json, update or disposition every advisory, and rerun." if code else "No action.")
    else:
        check(result, "GAP", "OSV dependency scan unavailable",
              "OSV-Scanner was not found on PATH.",
              "Install OSV-Scanner before treating dependency results as complete.")


def is_clean(result: dict) -> bool:
    blocked = {"FAIL", "WARN", "GAP"}
    return not any(row["severity"] in blocked for row in result["findings"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=Path("."),
                        help="plugin source repository (default: current directory)")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true", help="Print the complete JSON receipt")
    parser.add_argument("--allow-gaps", action="store_true",
                        help="Allow missing scanners without calling the run clean")
    args = parser.parse_args()
    source = args.source.resolve()
    started = datetime.now(timezone.utc).isoformat()
    result = {"tool": "atak-plugin-preflight", "version": 1, "started_at_utc": started,
              "source": str(source), "findings": []}
    inspect_source(source, result)
    output = (args.output or Path("reports") /
              f"preflight-{datetime.now():%Y%m%d-%H%M%S-%f}").resolve()
    output.mkdir(parents=True, exist_ok=True)
    run_source_scans(source, output, result)
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["passed"] = is_clean(result)
    has_failures = any(row["severity"] == "FAIL" for row in result["findings"])
    has_gaps = any(row["severity"] == "GAP" for row in result["findings"])
    has_review = any(row["severity"] == "WARN" for row in result["findings"])
    result["status"] = ("FAIL" if has_failures else "PARTIAL" if has_gaps
                         else "REVIEW" if has_review else "PASS")
    result["partial"] = result["status"] == "PARTIAL"
    result["report_dir"] = str(output)
    (output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
        html.escape(row["severity"]), html.escape(row["title"]),
        html.escape(row["detail"]), html.escape(row["next_action"]))
        for row in result["findings"])
    (output / "report.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>ATAK Plugin Preflight</title>"
        f"<h1>ATAK Plugin Preflight</h1><p><b>Source:</b> {html.escape(str(source))}</p>"
        f"<p><b>Source SHA-256:</b> {result.get('source_sha256', 'unavailable')}</p>"
        f"<p><b>Status:</b> {result['status']}</p><p><b>Passed:</b> {result['passed']}</p>"
        "<table border='1' cellpadding='6'>"
        "<tr><th>Level</th><th>Finding</th><th>Evidence</th><th>Next action</th></tr>"
        f"{rows}</table>")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for row in result["findings"]:
            print(f"{row['severity']:>4}  {row['title']}: {row['detail']}")
        print(f"Report: {output}")
    return 0 if result["passed"] or (args.allow_gaps and result["status"] == "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
