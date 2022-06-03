py setup.py sdist
py setup.py bdist_wheel
twine upload --repository pypi dist/*