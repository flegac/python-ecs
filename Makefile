Cf. https://python-poetry.org/docs/#installation
Cf. https://stackoverflow.com/questions/68882603/using-python-poetry-to-publish-to-test-pypi-org

build:
    poetry version prerelease
    poetry version patch
	poetry build

deploy-test:
    poetry publish -r test-pypi

deploy-pypi:
    poetry publish
