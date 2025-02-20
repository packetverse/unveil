import typer

from typing import Annotated
from rich.console import Console

from unveil.logger import Logger
from unveil.utils import _validate_ip

app = typer.Typer()


@app.command()
def validate(ctx: typer.Context, ip: Annotated[str, typer.Argument()]) -> None:
    """Takes an IP address as input and checks if it's a valid IPv4 address"""
    console: Console = ctx.obj["CONSOLE"]
    log: Logger = ctx.obj["LOG"]

    log.info(f"Validating: {ip}")

    if _validate_ip(ip):
        log.info(f"{ip} is valid")
        console.print(f"[bold green][+] {ip} is valid[/]")
        raise typer.Exit()
    else:
        log.info(f"{ip} is NOT VALID!")
        console.print(f"[bold red][-] {ip} is invalid[/]")
        raise typer.Exit(code=1)
