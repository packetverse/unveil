import typer

from typing import Annotated, Optional
from pathlib import Path
from itertools import islice
from rich.panel import Panel
from rich.console import Console

from unveil.logger import Logger
from unveil.scraper import DNSBLInfo, Scraper, WhatIsMyIPAddress

app = typer.Typer()


# add logic to output the providers to a file
@app.command(
    "blacklists, providers",
)
def blacklists(
    ctx: typer.Context,
    limit: Annotated[
        Optional[int],
        typer.Option(
            "--limit",
            "-l",
            help="Limit how many providers to get from all scraper modules",
        ),
    ] = 0,
) -> None:
    """Get all providers the scraper modules fetches from the web"""
    console: Console = ctx.obj["CONSOLE"]
    log: Logger = ctx.obj["LOG"]
    scrapers = [DNSBLInfo, WhatIsMyIPAddress]

    log.info(f"Fetching blacklists from: {[scraper.__name__ for scraper in scrapers]}")
    blacklists = Scraper(scrapers).fetch()

    if ctx.obj["OUTPUT"]:
        log.info("output flag specified")

        output_path = Path(ctx.obj["OUTPUT"])
        log.info(f"output path: {output_path}")

        mode = "a" if output_path.exists() else "w"
        log.info(f"will output to file with mode: {mode}")

        with open(output_path, mode) as f:
            log.info(f"reading now from file: {output_path}")
            if limit > 0:
                log.info(f"writing to file with limit: {limit}")
                for blacklist in islice(blacklists, limit):
                    f.write(f"{blacklist}\n")
                log.info(f"wrote blacklists to file with limit: {limit}")
                raise typer.Exit()
            else:
                log.info("writing all blacklists to file without limit")
                for blacklist in blacklists:
                    f.write(f"{blacklist}\n")
                log.info("wrote all blacklists to file without limit")
                raise typer.Exit()
    else:
        if limit > 0:
            log.info(f"printing to console with limit: {limit}")
            console.print(
                Panel(
                    "\n".join(islice(blacklists, limit)),
                    title="[bold blue]Providers[/]",
                )
            )
            log.info("printed to console")
            raise typer.Exit()
        else:
            log.info("printing to console without limit")
            console.print(Panel("\n".join(blacklists), title="[bold blue]Providers[/]"))
            log.info("wrote to console")
            raise typer.Exit()
