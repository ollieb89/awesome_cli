# Architecture Documentation

## Project Structure

The project follows a `src`-layout to ensure tests run against the installed package and to avoid import ambiguities.

```
src/
  awesome_cli/
    __init__.py
    __main__.py          # Entry point for `python -m awesome_cli`
    cli.py               # Typer CLI application definition
    config.py            # Configuration loading (Env vars, files)
    core/                # Core domain logic
      services.py        # Business logic functions
      models.py          # Dataclasses and types
      io.py              # I/O helpers
    utils/               # Utility modules
      logging.py         # Logging configuration
      paths.py           # Path helpers
```

## Key Decisions

- **Typer**: Used for the CLI interface due to its type-hint-based command definition and ease of use.
- **Rich**: Integrated for beautiful terminal output.
- **Dataclasses**: Used for configuration (`Settings`) and domain models to keep dependencies minimal.
- **Src Layout**: Chosen for better packaging practices.
- **Hatchling**: Used as the build backend for modern standards compliance.
