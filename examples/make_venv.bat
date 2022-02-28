del /Q venv
"C:\Program Files\Python310\python.exe" -m venv --clear venv
call venv\Scripts\activate.bat 
python -m pip install --upgrade pip
python -m pip install -U balsa
call deactivate
