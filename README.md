# Python Starter Template

This is a simple Python starter template that you can use to start your Python project. 

## Setup

We use `poetry` for managing dependencies. To install `poetry`, follow the instructions at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation). To install the dependencies, run:
```
poetry install
```

Then run:
```
poetry shell
```
to activate the virtual environment. Alternatively, you can run commands in the virtual environment by prefixing them with `poetry run`.

## Development

### Setup

In addition to the setup above, please run the following command to install the `pre-commit` git hook (described in [this section](#linting)):
```
pre-commit install
```

### Testing

We use `pytest` for our unit testing and `coverage` for determining our codebase test coverage.

To generage coverage reports:

```
coverage run -m pytest demo/tests/test_main.py
coverage report -m
```

Unit tests are automatically run in the Github workflow defined in `.github/workflows/python.yml`.

### Linting

We use `pre-commit` git hooks to run linters. These tools are configured:
* `autoflake` - remove unused imports and variables
* `black` - code formatter
* `isort` - sort imports
* `flake8` - linter

The linters should run automatically before each commit. If you want to run them manually, you can run:
```
pre-commit run --all-files
```
This will run all the linters on all the files in the repository, not just the ones that are staged for commit.

## Contact

Patrick Liu
