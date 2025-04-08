import typer
from rich.console import Console
from pathlib import Path
import json
import os
from typing import Optional

app = typer.Typer(
    name="config",
    help="Manage mosscli configuration",
    add_completion=False,
)

console = Console()

CONFIG_DIR = Path.home() / ".mosscli"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "proxy": {
        "enabled": False,
        "list": []
    },
    "ai": {
        "provider": "groq",
        "api_key": ""
    },
    "output": {
        "format": "csv",
        "directory": "./output"
    }
}

def ensure_config_exists():
    """Ensure config directory and file exist with default values."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

def load_config():
    """Load current configuration."""
    ensure_config_exists()
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

@app.command()
def show():
    """Show current configuration."""
    config = load_config()
    console.print("[bold green]Current Configuration:[/bold green]")
    console.print(json.dumps(config, indent=4))

@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key to set (e.g., 'proxy.enabled')"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set a configuration value."""
    config = load_config()
    
    # Handle nested keys
    keys = key.split(".")
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Convert value to appropriate type
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    elif value.isdigit():
        value = int(value)
    elif value.replace(".", "", 1).isdigit():
        value = float(value)
    
    current[keys[-1]] = value
    save_config(config)
    console.print(f"[bold green]Set {key} to {value}[/bold green]")

@app.command()
def reset():
    """Reset configuration to defaults."""
    save_config(DEFAULT_CONFIG)
    console.print("[bold green]Configuration reset to defaults[/bold green]")

@app.command()
def get(
    key: str = typer.Argument(..., help="Configuration key to get (e.g., 'proxy.enabled')"),
):
    """Get a configuration value."""
    config = load_config()
    
    # Handle nested keys
    keys = key.split(".")
    current = config
    for k in keys:
        if k not in current:
            console.print(f"[bold red]Key {key} not found[/bold red]")
            return
        current = current[k]
    
    console.print(f"[bold green]{key}: {current}[/bold green]")

if __name__ == "__main__":
    app() 