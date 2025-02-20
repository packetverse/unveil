import time
import typer

from inspect import cleandoc
from typing import Annotated, Optional
from pydantic import ValidationError
from json import dumps
from rich.console import Console
from rich.style import Style
from rich.panel import Panel

from unveil.logger import Logger
from unveil.ip import IPFetcher

app = typer.Typer()


# add different sources to fetch public ip from such as the scraper module
# make different panels and title of each panel would be where it fetched it's information
@app.command()
def ip(
    ctx: typer.Context,
    raw: Annotated[
        Optional[bool],
        typer.Option("--raw", "-r", help="Returns your Public IP and nothing more"),
    ] = False,
    json: Annotated[
        Optional[bool],
        typer.Option("--json", "-j", help="Returns the JSON pretty printed"),
    ] = False,
) -> None:
    """Fetch your Public IP address from various sources"""
    console: Console = ctx.obj["CONSOLE"]
    log: Logger = ctx.obj["LOG"]

    start_time = time.time()
    log.info(f"Starting time: {start_time:.2f}")

    fetcher = IPFetcher()
    try:
        log.info("trying to fetch data from all apis")
        data = fetcher.fetch_from_all_apis()
    except ValidationError as e:
        log.error(e)
        console.print(f"[bold red]Validation Error:[/] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        log.error(e)
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(code=1)

    log.info("fetched data from all apis")

    if raw:
        log.info("raw flag supplied")
        log.info("getting first api fetched and returning just IP")
        raw_ip = list(data.values())[0].ip if data else "No IP found"
        log.info("printing to console")
        console.print(raw_ip)
        log.info("done")
        raise typer.Exit()
    elif json:
        log.info("json flag supplied")
        formatted_data = dumps(data, indent=4)
        log.info("printing to console")
        console.print(Panel(formatted_data, title="[bold green]JSON[/]"))
        log.info("done")
        raise typer.Exit()

    log.info("no flags supplied")
    log.info("pretty printing to console...")
    for api_name, ip_info in data.items():
        q = Style(color="blue", bold=True)
        strings = ""

        for field, value in vars(ip_info).items():
            if value:
                # field_name = config.field_aliases.get(field, field)
                strings += f"[{q}][?][/] {field}: {value}\n"

        formatted_data = cleandoc(strings)

        console.print(Panel(formatted_data, title=f"[bold blue]{api_name}[/]"))
        log.info("printed to console")

    end_time = time.time()
    log.info(f"End time: {end_time:.2f}")

    total_time = end_time - start_time
    num_apis = len(data)
    log.info(f"Fetched data from {num_apis} APIs in {total_time:.2f}")
    log.info("printing info to console")
    console.print(
        Panel(
            f"[bold yellow][.][/] Fetched data from {num_apis} APIs in {total_time:.2f} seconds.",
            title="Results",
            title_align="left",
        )
    )
    log.info("done")
    raise typer.Exit()
