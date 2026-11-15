pushd .
cd ..
call venv\Scripts\activate.bat
python -m black -l 192 balsa test_balsa
call deactivate
popd
