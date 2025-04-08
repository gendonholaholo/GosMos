# TikTok Scraper Tests

This directory contains the test suite for the TikTok Scraper project. The tests are organized into separate modules for each component of the system.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py
├── test_proxy_rotator.py
├── test_data_processor.py
├── test_scraper.py
└── README.md
```

## Running Tests

### Prerequisites

- Python 3.8+
- pytest
- pytest-cov (for coverage reports)

### Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

2. Install the project in development mode:
```bash
pip install -e .
```

### Running All Tests

To run all tests:
```bash
pytest tests/
```

### Running Specific Tests

To run tests for a specific module:
```bash
pytest tests/test_proxy_rotator.py
pytest tests/test_data_processor.py
pytest tests/test_scraper.py
```

### Running with Coverage

To run tests with coverage report:
```bash
pytest --cov=core tests/
```

## Test Categories

### ProxyRotator Tests
- Initialization and configuration
- Proxy rotation functionality
- Proxy validation
- Error handling

### DataProcessor Tests
- Data processing for products, creators, and videos
- File saving (CSV and JSON)
- DataFrame merging
- Error handling

### Scraper Tests
- Request handling
- Retry mechanism
- Data extraction
- Error handling
- Batch processing

## Writing New Tests

When adding new tests:

1. Use the existing fixtures from `conftest.py`
2. Follow the naming convention: `test_<functionality>`
3. Include docstrings explaining the test purpose
4. Use appropriate assertions
5. Mock external dependencies
6. Test both success and error cases

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies
3. **Coverage**: Aim for high test coverage
4. **Readability**: Write clear and descriptive test names
5. **Maintenance**: Keep tests up to date with code changes

## Troubleshooting

If tests fail:

1. Check the test output for specific error messages
2. Verify that all dependencies are installed
3. Ensure the test environment is properly configured
4. Check if the test data is still valid
5. Verify that the mocked responses match the expected format 