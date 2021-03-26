pushd .
cd ..
call venv\Scripts\activate.bat 
mypy -m balsa
call deactivate
popd
