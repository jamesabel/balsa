REM set PYTHON_EXE environment variable before running if a different python is desired
if DEFINED PYTHON_EXE goto RUNVENV
REM default
set PYTHON_EXE="\Program Files\Python36\python.exe"
:RUNVENV
%PYTHON_EXE% -m venv --clear venv
venv\Scripts\pip3 install -U pip
venv\Scripts\pip3 install -U setuptools
venv\Scripts\pip3 install -U -r requirements.txt
