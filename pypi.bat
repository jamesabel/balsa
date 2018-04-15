del /Q cmpa.egg-info\*.*
del /Q dist\*.*
copy /Y LICENSE LICENSE.txt
venv\Scripts\python.exe setup.py sdist upload -r pypi
