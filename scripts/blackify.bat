pushd .
cd ..
call venv\Scripts\activate.bat
python -m black -l 192 balsa test_balsa setup.py
call deactivate
popd
