pushd .
cd ..
REM format, then lint (configuration is in pyproject.toml)
uv run ruff format
uv run ruff check
popd
