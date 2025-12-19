# Awesome CLI

A production-ready Python CLI application scaffold.

## Description

Awesome CLI is a robust command-line interface tool built with Python, utilizing modern best practices and libraries like Typer and Rich.

## Installation

You can install the package in editable mode for development:

```bash
pip install -e .
```

## Usage

After installation, the `awesome-cli` command will be available.

### Basic Commands

Get help:
```bash
awesome-cli --help
```

Initialize the application:
```bash
awesome-cli init
```

Run a job:
```bash
awesome-cli run --name my_job
```

### Running via `python -m`

You can also run the CLI using the module name:

```bash
python -m awesome_cli run --name my_job --verbose
```

## Development

### Running Tests

Run the test suite with `pytest`:

```bash
pytest
```

### Linting and Formatting

We use `ruff` for linting and formatting.

```bash
ruff check .
ruff format .
```

### Type Checking

We use `mypy` for static type checking.

```bash
mypy src
```
