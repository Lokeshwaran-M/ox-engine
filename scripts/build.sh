
# for pip update
pipreqs . --force 

python setup.py sdist 
python setup.py bdist_wheel 

twine upload dist/*


keyring set https://upload.pypi.org/legacy/ your-username


# for pyinstaller build

pyinstaller --onefile ox_db.shell.py