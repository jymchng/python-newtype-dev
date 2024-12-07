# Contributing Guide

Thank you for considering contributing to python-newtype! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/python-newtype-dev.git
   cd python-newtype-dev
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   make install-dev-deps
   ```

## Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```

2. Make your changes and ensure:
   - Code follows the project style
   - Tests pass
   - Documentation is updated
   - C extensions compile correctly

3. Run tests:
   ```bash
   make test
   ```

4. Build documentation:
   ```bash
   mkdocs serve  # View at http://127.0.0.1:8000
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

6. Push and create a pull request:
   ```bash
   git push origin feature-name
   ```

## Code Style

- Follow PEP 8
- Use type hints where appropriate
- Document functions and classes with docstrings
- Keep functions focused and concise
- Write clear commit messages

## Testing

- Write tests for new features
- Ensure all tests pass
- Include both positive and negative test cases
- Test edge cases
- Use pytest fixtures appropriately

### Running Tests

```bash
# Run all tests
make test

# Run with debug output
make test-debug

# Run specific test file
make test-file FILE=tests/test_newtype.py

# Run with memory leak detection
make test-leak
```

## Documentation

- Update documentation for new features
- Include examples in docstrings
- Update API reference if needed
- Check documentation builds correctly

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## C Extensions

When modifying C extensions:

1. Follow C best practices
2. Update header files appropriately
3. Test compilation on multiple platforms
4. Document any platform-specific code
5. Use debug printing when needed

### Building Extensions

```bash
# Clean and rebuild
make clean build

# Build with debug printing
make build-debug
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Create detailed pull request description

## Release Process

1. Update version number
2. Update CHANGELOG.md
3. Create release notes
4. Tag release
5. Build and upload to PyPI

## Getting Help

- Open an issue for bugs
- Discuss major changes in issues first
- Join discussions in existing issues
- Ask questions in discussions

## Code of Conduct

- Be respectful and inclusive
- Follow the project's code of conduct
- Help others learn and grow
- Give credit where due
