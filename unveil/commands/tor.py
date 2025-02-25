# This module hasn't been tested and I don't believe it's working
# Reason: it just gets your public ip and queries torproject api to see if the IP is connected to Tor
# Just a speculation not sure if this works as I said hasn't been tested

import typer

# from typing import Annotated, Optional
from requests import get
from rich.console import Console

# from unveil.utils import _get_ip
from unveil.logger import Logger

app = typer.Typer()


@app.command()
def tor(
    ctx: typer.Context,
    # ip: Annotated[Optional[str], typer.Argument(default_factory=_get_ip)],
):
    """Checks if you are connected to tor"""
    log: Logger = ctx.obj["LOG"]
    console: Console = ctx.obj["CONSOLE"]

    try:
        response = get("https://check.torproject.org/api/ip", timeout=5)
        response.raise_for_status()

        data = response.json()
    except Exception as e:
        log.error(e)
        raise typer.Exit(code=1)

    if data["IsTor"]:
        console.print("[bold green]✅ You are connected through Tor![/]")
        raise typer.Exit()
    else:
        console.print("[bold red]❌ You are NOT connected through Tor.[/]")
        raise typer.Exit(code=1)
