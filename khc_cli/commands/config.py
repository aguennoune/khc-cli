"""Commands to manage khc-cli configuration."""
import typer
import yaml
from pathlib import Path
from khc_cli.config import CONFIG_PATH, DEFAULT_CONFIG

app = typer.Typer(help="Manage khc-cli configuration")

@app.command("init")
def init_config(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite the file if it already exists")
):
    """Initialize the configuration file ~/.khc_cli_rc"""
    if CONFIG_PATH.exists() and not force:
        typer.echo(f"File {CONFIG_PATH} already exists. Use --force to overwrite.")
        raise typer.Exit(1)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
    typer.echo(f"Configuration file created: {CONFIG_PATH}")
