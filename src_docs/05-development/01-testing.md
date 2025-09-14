# Testing

This project uses `pytest` for testing. To run the tests, use the following command:

```bash
hatch run test
```

This will run all the unit and integration tests.

## Test Structure

The tests are organized into two main directories:

-   `tests/unit`: Unit tests for individual components.
-   `tests/integration`: Integration tests for the complete pipeline and CLI.

## Running Specific Tests

You can run specific tests by passing arguments to `pytest`:

```bash
hatch run test -- tests/unit/test_config.py
```

## Coverage

To generate a test coverage report, run:

```bash
hatch run test-cov
```
