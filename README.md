# Awesome CLI

A production-ready Python CLI application scaffold.

## Installation

To install the application in editable mode (useful for development), run:

```bash
pip install -e .
```

To install dev dependencies (tests, linting):

```bash
pip install -e ".[dev]"
```

## Usage

You can run the CLI directly using the `awesome-cli` command (after installation) or via `python -m awesome_cli`.

### General Help

```bash
awesome-cli --help
```

### Initialize Configuration

Initialize the application state (e.g., creates default config).

```bash
awesome-cli init
```

### Run a Job

Run the main application logic.

```bash
awesome-cli run --verbose --name "MyJob"
```

## Development

### Running Tests

We use `pytest` for testing.

```bash
pytest
```

### Type Checking

We use `mypy` for static type checking.

```bash
mypy src
```

### Linting

We use `ruff` for linting.

```bash
ruff check src tests
```
