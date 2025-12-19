"""
CLI entry point using Typer.
"""
import logging
from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated

from awesome_cli import __version__, config, core
from awesome_cli.utils import setup_logging

app = typer.Typer(
    name="awesome-cli",
    help="A production-ready Python CLI application scaffold.",
    add_completion=False,
)
console = Console()
logger = logging.getLogger(__name__)

def version_callback(value: bool) -> None:
    """Callback to display the application version."""
    if value:
        console.print(f"Awesome CLI Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Annotated[
        Optional[bool], 
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit."
        )
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable verbose output.")
    ] = False,
    config_file: Annotated[
        Optional[str],
        typer.Option("--config", "-c", help="Path to config file.")
    ] = None,
) -> None:
    """
    Awesome CLI Main Entry Point.
    """
    # Load settings and setup logging
    settings = config.load_settings(config_file)
    if verbose:
        settings.log_level = "DEBUG"

    setup_logging(settings)

    if verbose:
        logger.debug(f"Settings loaded: {settings}")
        console.print(f"[dim]Loaded settings for env: {settings.env}[/dim]")

@app.command()
def init(
    path: Annotated[str, typer.Option(help="Path to initialize.")] = ".",
) -> None:
    """
    Initialize the application configuration and state.
    """
    console.print(f"[bold green]Initializing Awesome CLI at {path}...[/bold green]")
    try:
        result = core.initialize_app_state()
        console.print(f"Status: {result['status']}")
        logger.info(f"Initialization complete: {result}")
    except Exception as e:
        console.print(f"[bold red]Initialization failed:[/bold red] {e}")
        logger.exception("Initialization failed")
        raise typer.Exit(code=1) from e

@app.command()
def run(
    name: Annotated[str, typer.Option(help="Name of the job to run.")] = "default_job",
) -> None:
    """
    Run the main application logic.
    """
    console.print(f"Starting job: [bold cyan]{name}[/bold cyan]")
    
    try:
        result = core.run_job(name)
        console.print(f"[green]Success:[/green] {result.message}")
        logger.info(f"Job result: {result}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception(f"Job {name} failed")
        raise typer.Exit(code=1) from e

if __name__ == "__main__":
    app()
