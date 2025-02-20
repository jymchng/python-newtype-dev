# Building python-newtype

This guide covers how to build and package python-newtype for development and distribution.

## Prerequisites

Before building python-newtype, ensure you have the following installed:

- Python 3.8 or later
- Poetry (for dependency management)
- pytest (for testing)
- build (for building packages)

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-newtype.git
cd python-newtype
```

2. Create a new virtual environment using `venv`:

For Linux:

```bash
python3 -m venv venv
source .venv/bin/activate
```
For Windows:

```bash
python -m venv venv
.\.venv\Scripts\activate
```

3. Install `poetry`:

```bash
pip install poetry
```

4. Get poetry to use the virtual environment in the project directory:

```bash
poetry config virtualenvs.in-project true
```

This will ensure that Poetry uses the current virtual environment located in the project directory.
You can also set the virtual environment path explicitly if needed.
For example:

```bash
poetry config virtualenvs.path /path/to/your/venvs
```

Then, you can install all development dependencies using

```bash
poetry install --with dev --no-root --no-interaction
```

## Project Structure

```
python-newtype/
├── newtype/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_basic_examples.py
│   └── test_advanced_examples.py
├── docs/
│   └── ...
├── pyproject.toml
├── README.md
└── LICENSE
```

## Building the Package

### Using Poetry

1. Build the package:
```bash
poetry build
```

This will create both wheel and source distributions in the `dist/` directory.

2. Install the package locally for testing:
```bash
pip install dist/python_newtype-*.whl
```

### Using Build

Alternatively, you can use Python's build module:

```bash
poetry build
```

## Running Tests

1. Run all tests:
```bash
python -m pytest tests -s -vv
```
Or:
```bash
make test
```

2. Run tests with coverage:
```bash
pytest --cov=newtype
```

3. Run specific test files:
For example,
```bash
make test-file FILE=tests/test_advanced_examples.py
```

## Code Quality

### Type Checking

We use mypy for static type checking:

```bash
mypy newtype
```

### Code Style

Use `ruff` and `cppcheck` for style checking:

```bash
make check
```

### Formatting

We use `ruff` and `clang-format` for code formatting:

```bash
make format
```

## Documentation

### Building Documentation

We use MkDocs for documentation:

1. Install Docs MkDocs:
```bash
poetry install --with docs
```

2. Build the documentation:
```bash
mkdocs build
```

3. Serve documentation locally:
```bash
mkdocs serve
```

### Documentation Structure

- `/docs/index.md`: Main documentation page
- `/docs/user-guide/`: User guides and tutorials
- `/docs/api/`: API reference documentation
- `/docs/examples/`: Code examples
- `/docs/development/`: Development guides


## Release Process

### Poetry Dynamic Versioning
To use dynamic versioning, you need to install the poetry-dynamic-versioning plugin. You can do this by running:

```bash
poetry self add poetry-dynamic-versioning
```

### To Release a New Version

0. Make sure the Pull Request is merged into main.

1. Make sure you are on the main branch:

```bash
git checkout main
```

Or

```bash
git switch main
```

2. Set the version to the next patch version:
```
poetry version patch
```

3. Set the tag to the new version:
```
git tag v0.1.3
```

4. Commit your changes and push to the repository.

```bash
git commit -m "Release version 0.1.3"
```

5. Push the changes to the repository:
```
git push --tags
```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public APIs
- Keep functions focused and small

### Testing

- Write tests for all new features
- Maintain high test coverage
- Include both unit and integration tests
- Test edge cases and error conditions

### Documentation

- Update docs with new features
- Include code examples
- Keep API reference up to date
- Document breaking changes

## Performance Optimization

### Profiling

Use cProfile for performance profiling:

```python
import cProfile

def profile_newtype():
    # Your test code here
    pass

cProfile.run('profile_newtype()')
```

### Benchmarking

Create benchmarks using pytest-benchmark:

```python
def test_newtype_performance(benchmark):
    def wrapped_operation():
        # Your operation here
        pass

    benchmark(wrapped_operation)
```

## Troubleshooting

### Common Issues

1. Import errors:
   - Check PYTHONPATH
   - Verify virtual environment activation

2. Build failures:
   - Update Poetry and dependencies
   - Clear Poetry cache

3. Test failures:
   - Check Python version compatibility
   - Verify test dependencies

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See CONTRIBUTING.md for detailed guidelines.
