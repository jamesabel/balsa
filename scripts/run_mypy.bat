pushd .
cd ..
call venv\Scripts\activate.bat 
mypy -m balsa
mypy -m test_balsa
call deactivate
popd
