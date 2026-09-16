# Beginner workflow

> [!TIP]
> Start with the source repository. An APK can show what was built, but it
> cannot tell the agent which source line needs fixing.

For continuous checks on every push and pull request, see the [GitHub Actions
guide](ci.md).

## 1. Start with the source repository

Point the assistant at the plugin source, not the downloaded APK:

```sh
python3 preflight.py path/to/plugin-source
```

This checks the project shape and runs the available source SAST, dependency,
secret, and configuration scans. It tells you which tools are missing before a
long build. A missing tool is reported as `GAP` and makes the run non-clean; do
not interpret it as a clean result. Use `--allow-gaps` only for exploration.

## 2. Build locally if the source checks are clean

> [!NOTE]
> The SDK is a restricted developer dependency. Download it from tak.gov and
> keep it outside the public repository. This project does not sign or publish
> an APK.

Download the matching ATAK SDK from tak.gov. Keep it outside the public
repository and provide its path to the build environment. You do not need TPP
credentials or a TPP signing key for local preflight.

Build a debug or unsigned local variant using the plugin's documented ATAK SDK.
This is only a compile/runtime check; this repository does not sign or publish
an APK. Record the ATAK API version used by the build. The plugin API must match
the ATAK runtime API.

## 3. Rerun after fixes

```sh
python3 preflight.py path/to/plugin-source
```

Start with the first `FAIL`, `WARN`, or `GAP`. The report gives the reason, evidence,
and the next action. Fix the source finding, rebuild, and rerun. Do not send an
source to TPP while a local source scan has an unexplained failure.

## 4. Test on a real ATAK runtime

Install your own locally built APK on the exact ATAK variant and API version you target. Confirm
that ATAK Package Management reports the plugin as compatible, then exercise
the plugin's important user journey. A successful local package check does not
prove runtime compatibility.

## 5. Send your package to TPP

> [!WARNING]
> A clean local report reduces avoidable surprises; it is not a TPP acceptance
> result and cannot replace Fortify.

Attach the local report and its SHA-256 receipt with your package. Expect TPP to
run Fortify and acceptance checks that this repository cannot reproduce locally.

## Finding vocabulary

| Label | Meaning |
| --- | --- |
| PASS | A local check completed successfully. |
| FAIL | A local requirement failed; fix it before submission. |
| WARN | Review this item; it may need a tool, runtime, or TPP decision. |
| GAP | This check needs Fortify, TPP, or a stock ATAK runtime. |
