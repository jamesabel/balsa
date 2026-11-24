pushd .
cd ..
uv run pytest --cov-report=html --cov
popd
