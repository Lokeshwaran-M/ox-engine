
# for pip update
pipreqs .

python setup.py sdist 
python setup.py bdist_wheel 

twine upload dist/*


keyring set https://upload.pypi.org/legacy/ your-username