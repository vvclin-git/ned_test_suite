# Changelog

## Unreleased

- Add runtime dependencies to `pyproject.toml` based on the repo's actual imaging, plotting, and numeric imports.
- Document Python/Tkinter requirements and the `uv sync` setup step in `README.md`.
- Remove stale `imp` and `msilib` imports that fail on Python 3.12+ and were not used by the code.
