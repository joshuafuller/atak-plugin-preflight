# ATAK SDK handoff

The ATAK SDK is a restricted developer dependency. The agent cannot download
it from this repository, place it in public source control, or use TPP
credentials on the user's behalf.

## Tell the user what to do

1. Sign in at the [TAK.gov user-builds portal](https://tak.gov/user_builds).
2. Download the SDK matching the ATAK API and variant being tested.
3. Extract it into a private local SDK directory.
4. Set `ATAK_SDK` to the extracted SDK directory.

Recommended locations are:

| Environment | Recommended location |
| --- | --- |
| Linux/macOS | `~/atak-sdks/ATAK-CIV-5.6.0/` |
| Windows | `%USERPROFILE%\\atak-sdks\\ATAK-CIV-5.6.0\\` |
| WSL using a Windows download | `/mnt/c/Users/<name>/atak-sdks/ATAK-CIV-5.6.0/` |

The exact directory name is not important. The path must point to the SDK root,
not the downloaded archive and not an extra nested directory created during
extraction.

Example:

```sh
export ATAK_SDK="$HOME/atak-sdks/ATAK-CIV-5.6.0"
```

PowerShell:

```powershell
$env:ATAK_SDK = "$env:USERPROFILE\atak-sdks\ATAK-CIV-5.6.0"
```

## Agent discovery order

When an SDK-backed build is requested, inspect these locations in order:

1. `ATAK_SDK` if set;
2. `./.atak-sdk` if the user explicitly created that local path;
3. `~/atak-sdks/` on Linux/macOS;
4. `%USERPROFILE%\\atak-sdks\\` on Windows, including `/mnt/c/Users/...`
   when running under WSL.

If none exists, explain that the SDK is behind the TAK.gov login and provide
the download and extraction instructions above. Do not silently substitute a
different ATAK version. Record the SDK path and version in build evidence, but
never copy SDK contents into this public repository.

## Container boundary

The current Docker image runs source scanners only. It does not mount or
consume `ATAK_SDK`; SDK-backed Gradle builds should run in the plugin's own
documented build environment, with the SDK mounted read-only when supported.

No SDK path proves compatibility by itself. The plugin API, variant,
obfuscation mapping, signing requirements, and runtime behavior still need to
match the target ATAK installation.
