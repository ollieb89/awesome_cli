"""
CLI entry point using Typer.
"""
import typer
from typing import Optional
from typing_extensions import Annotated
from awesome_cli import __version__
from awesome_cli import core, config
from rich.console import Console

app = typer.Typer(
    name="awesome-cli",
    help="A production-ready Python CLI application scaffold.",
    add_completion=False,
)
console = Console()

def version_callback(value: bool):
    """Callback to display the application version."""
    if value:
        console.print(f"Awesome CLI Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Annotated[
        Optional[bool], 
        typer.Option("--version", "-v", callback=version_callback, is_eager=True, help="Show the version and exit.")
    ] = None,
):
    """
    Awesome CLI Main Entry Point.
    """
    pass

@app.command()
def init(
    path: Annotated[str, typer.Option(help="Path to initialize.")] = ".",
):
    """
    Initialize the application configuration and state.
    """
    console.print(f"[bold green]Initializing Awesome CLI at {path}...[/bold green]")
    result = core.initialize_app_state()
    console.print(f"Status: {result['status']}")

@app.command()
def run(
    name: Annotated[str, typer.Option(help="Name of the job to run.")] = "default_job",
    config_file: Annotated[Optional[str], typer.Option("--config", "-c", help="Path to config file.")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", help="Enable verbose output.")] = False,
):
    """
    Run the main application logic.
    """
    # Load configuration
    settings = config.load_settings(config_file)
    
    if verbose:
        console.print(f"[dim]Loaded settings for env: {settings.env}[/dim]")
    
    console.print(f"Starting job: [bold cyan]{name}[/bold cyan]")
    
    # Call core logic
    try:
        result = core.run_job(name, verbose=verbose)
        console.print(f"[green]Success:[/green] {result}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
