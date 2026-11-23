pushd .
cd ..
uv run sphinx-build -M html docs\source docs\build
copy /Y docs\source\readme.rst readme.rst
popd
