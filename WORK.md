# this_file: WORK.md
---

# Current work

- The release guide now documents the existing GitHub Actions Trusted Publishing workflow. `actionlint .github/workflows/release.yml` and `bash -n publish.sh` passed. PyPI publisher registration is an owner action.
- `./build.sh docs` built 12 pages with fly-january 0.2.1 in strict mode with zero warnings. The contributor page and search index both contain the corrected release instructions.
- On Python 3.12.12, the full suite had 152 passed, 21 failed, 3 skipped and 2 warnings. The 21 failing test IDs match the previous run. The focused invalid-input and missing-metadata checks passed all 10 selected tests.
- Ruff 0.17.5 reported 200 findings with `ruff check --no-cache --statistics src/vexy_pdf_werk tests`.
- Direct checks of `validate_pdf_file` passed for all 10 inputs, including image-only, password-protected and corrupt PDFs.
