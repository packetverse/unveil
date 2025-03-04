import time
import typer
import asyncio

from typing import Annotated, Optional
from pydantic import ValidationError
from json import dumps
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

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
        data = asyncio.run(fetcher.fetch_all_sources())
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
        raw_ip = next(iter(data.values())).ip if data else "No IP found"
        console.print(raw_ip)
        raise typer.Exit()

    elif json:
        log.info("json flag supplied")

        json_data = {api: vars(info) for api, info in data.items()}
        console.print(JSON(dumps(json_data, ensure_ascii=True, indent=4)))
        raise typer.Exit()

    log.info("no flags supplied")
    log.info("pretty printing to console...")
    for source, ip_info in data.items():
        details = "\n".join(
            f"[blue][.][/] {field}: {value}"
            for field, value in vars(ip_info).items()
            if value
        )
        console.print(Panel(details, title=f"[bold blue]{source}[/]"))

    duration = time.time() - start_time
    log.info(f"Completed in {duration:.2f} seconds.")
    console.print(
        Panel(
            f"[bold yellow][.][/] Fetched data from {len(data)} sources in {duration:.2f} seconds.",
            title="Results",
            title_align="left",
        )
    )
    raise typer.Exit()
