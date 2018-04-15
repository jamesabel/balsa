del /Q cmpa.egg-info\*.*
del /Q dist\*.*
copy /Y LICENSE LICENSE.txt
copy /Y docs\source\readme.rst readme.rst
venv\Scripts\python.exe setup.py sdist upload -r pypi
