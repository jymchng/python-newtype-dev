# Building Python NewType

This guide covers how to build and package Python NewType for development and distribution.

## Prerequisites

Before building Python NewType, ensure you have the following installed:

- Python 3.7 or later
- Poetry (for dependency management)
- pytest (for testing)
- build (for building packages)

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-newtype.git
cd python-newtype
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
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
pip install dist/newtype-*.whl
```

### Using Build

Alternatively, you can use Python's build module:

```bash
python -m build
```

## Running Tests

1. Run all tests:
```bash
pytest
```

2. Run tests with coverage:
```bash
pytest --cov=newtype
```

3. Run specific test files:
```bash
pytest tests/test_basic_examples.py
```

## Code Quality

### Type Checking

We use mypy for static type checking:

```bash
mypy newtype
```

### Code Style

We follow PEP 8 guidelines. Use flake8 for style checking:

```bash
flake8 newtype tests
```

### Formatting

We use black for code formatting:

```bash
black newtype tests
```

## Documentation

### Building Documentation

We use MkDocs for documentation:

1. Install MkDocs:
```bash
pip install mkdocs mkdocs-material
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

1. Update version in `pyproject.toml`:
```toml
[tool.poetry]
name = "newtype"
version = "1.0.0"
```

2. Create and push a tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

3. Build distribution packages:
```bash
poetry build
```

4. Upload to PyPI:
```bash
poetry publish
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

## Continuous Integration

We use GitHub Actions for CI/CD:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, "3.10"]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    - name: Run tests
      run: poetry run pytest
    - name: Check types
      run: poetry run mypy newtype
```

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
