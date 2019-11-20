del /Q balsa.egg-info\*.*
del /Q build\*.*
del /Q dist\*.*
copy /Y LICENSE LICENSE.txt
copy /Y docs\source\readme.rst readme.rst
copy /Y docs\source\readme.rst balsa\readme.rst
venv\Scripts\python.exe setup.py bdist_wheel
twine upload dist/*
