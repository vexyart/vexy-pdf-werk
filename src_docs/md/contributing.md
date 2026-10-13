# Contributing

This page covers the development setup, tests, the documentation build and the release process.

## Set up a development environment

Prerequisites: Git, [uv](https://docs.astral.sh/uv/), and `ocrmypdf` and `qpdf` on your `PATH` for end-to-end runs.

1. Clone the repository:

    ```bash
    git clone https://github.com/vexyart/vexy-pdf-werk
    cd vexy-pdf-werk
    ```

2. Install the package in editable mode with the test and development extras:

    ```bash
    uv sync --extra test --extra dev
    ```

3. Check the command:

    ```bash
    uv run vpw version
    ```

## Repository layout

| Path | Contents |
|---|---|
| `src/vexy_pdf_werk/` | Package source. See [Architecture](architecture.md). |
| `tests/` | `pytest` tests, one file per module (`test_cli.py`, `test_markdown_converter.py`, ...). |
| `examples/` | Sample PDFs in `examples/data/`, plus Python and shell example scripts. |
| `src_docs/` | Documentation source (`src_docs/md/`), `mkdocs.yml` and `build.sh`. |
| `docs/` | Built documentation site, served by GitHub Pages. Do not edit by hand. |
| `build.sh`, `publish.sh` | Build and release scripts. |

## Run the tests

Run the whole suite:

```bash
uv run --extra test pytest
```

Run one file or one test:

```bash
uv run --extra test pytest tests/test_markdown_converter.py
uv run --extra test pytest tests/test_cli.py -k config
```

The `pytest` settings in `pyproject.toml` add `-v --durations=10` and set `asyncio_mode = "auto"`, so `async def` tests run without a decorator.

## Lint and type-check

```bash
uvx ruff check src tests
uvx ruff format --respect-gitignore src tests
uvx mypy src/vexy_pdf_werk
```

The `push.yml` workflow runs `ruff check` and `ruff format --check`, then the tests on Python 3.10, 3.11 and 3.12, then builds the wheel and sdist.

## Build the documentation

The site is built with [ProperDocs](https://pypi.org/project/properdocs/) and the MaterialX theme from the Markdown files in `src_docs/md/`.

1. Edit or add pages in `src_docs/md/`. Add new pages to the `nav` list in `src_docs/mkdocs.yml`.
2. Preview the site:

    ```bash
    src_docs/build.sh serve
    ```

    Open `http://127.0.0.1:8000` in a browser. The page reloads when you save a file.

3. Build the site into `docs/`:

    ```bash
    src_docs/build.sh
    ```

    The build runs in strict mode, so a warning, such as a link to a missing page, stops it.

You do not need to commit `docs/` yourself. The `docs.yml` workflow rebuilds `docs/` and commits it on every push to `main` that changes `src_docs/`.

## Build the package

```bash
./build.sh package
```

This deletes `dist/`, runs `uv build`, and checks the result with `twine check`. `./build.sh` with no argument also builds the documentation, and `./build.sh docs` builds only the documentation.

The version comes from the latest Git tag through `hatch-vcs`. Between tags, the built version is a development version such as `1.2.2.dev3`.

## Release a new version

Releases are made from a clean `main` branch with `publish.sh`.

Prerequisites: a PyPI token in `UV_PUBLISH_TOKEN` (or another credential that `uv publish` accepts), and push access to the repository.

1. Run:

    ```bash
    ./publish.sh
    ```

2. The script runs `uvx gitnextver`, which commits pending changes, creates the next `vX.Y.Z` tag and pushes it.
3. If `HEAD` now carries a `vX.Y.Z` tag, the script builds the package with `./build.sh package` and uploads `dist/*` with `uv publish`. If there was nothing to commit and no tag was made, it stops with an error.

Pushing the tag also starts the `release.yml` workflow. It builds the package again, uploads it to PyPI (skipping files that `publish.sh` already uploaded), and creates a GitHub release with the built files attached.

## Pull requests

1. Create a branch from `main`.
2. Make the change and add or update tests for it.
3. Run the tests and `ruff`.
4. If the change affects behaviour, update the pages in `src_docs/md/` and `CHANGELOG.md`.
5. Open a pull request against `main`.
