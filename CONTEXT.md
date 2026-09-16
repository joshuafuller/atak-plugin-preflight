# Project context

This repository is a source-first pre-flight assistant for authors of ATAK
plugins. It helps an author find and understand defects before submitting a
package to the Third Party Pipeline (TPP), the APK signing/submission service.

## Glossary

| Term | Meaning |
| --- | --- |
| Plugin source | The Android/Gradle repository from which a plugin is built. This is the primary input to preflight. |
| ATAK API version | The ATAK plugin API selected by the plugin build, such as `5.6.0`. It must match the runtime API exposed by the installed ATAK application. |
| Variant | The ATAK flavor, such as CIV or MIL. From ATAK 4.2 onward, a CIV plugin may run in any ATAK variant; a plugin built for a specific variant is restricted to that variant. |
| Plugin compatibility | The combined result of API version, variant, obfuscation mapping, and signing-key rules. Matching one factor does not prove compatibility. |
| Source preflight | Fast, repeatable checks over source, Gradle inputs, manifests, and dependency declarations before submission. |
| Runtime evidence | Evidence from installing and exercising the plugin on a particular ATAK build, Android image, device, and scenario. |
| TPP evidence | Evidence produced by the private Third Party Pipeline, including Fortify, dependency analysis, APK signing, and acceptance decisions. |
| Finding | A tool-reported condition that needs triage. A finding is not automatically a confirmed vulnerability or a false positive. |
| Gap | A check that was not available locally or can only be confirmed by Fortify, TPP, or a stock ATAK runtime. A gap is not a clean result. |
| Evidence ceiling | The strongest claim justified by the check that actually ran. A source scan cannot prove runtime loading or TPP acceptance. |

## Project boundaries

The project scans source and build inputs. It does not need TPP credentials, does
not sign an APK, and does not claim to reproduce Fortify or TAK.gov acceptance.
An unsigned/debug build and an emulator test are optional evidence layers after
the source checks.
