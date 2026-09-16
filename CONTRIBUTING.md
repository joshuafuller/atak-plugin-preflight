# Contributing

Contributions should keep this project source-first and honest about its
evidence limits.

Before opening a pull request:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 preflight.py --help
```

Changes to scanner commands should include a small test or fixture that proves
the report file, exit status, and finding level. Do not add ATAK SDKs, APKs,
signing keys, TPP credentials, or private scan results to the repository.

Security-sensitive changes should explain the data flow and the evidence they
add. A local check must not be described as Fortify or TPP equivalence.
