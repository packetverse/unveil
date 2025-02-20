import typer
import dns.resolver

from inspect import cleandoc
from typing import Optional, Annotated
from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers, Timeout
from rich.progress import Progress
from rich.console import Console
from rich.panel import Panel
from rich.style import Style

from unveil.logger import Logger
from unveil.scraper import DNSBLInfo, Scraper, WhatIsMyIPAddress
from unveil.utils import _get_ip, _reverse_ip

app = typer.Typer()


# This command always assumes an IP is IPv4 we should add some logic to check and verify if IPv4 or IPv6
# and then use according blacklists that support IPv6 and so on
@app.command()
def check(
    ctx: typer.Context,
    ip: Annotated[
        Optional[str],
        typer.Argument(
            metavar="TEXT",
            show_default=False,
            default_factory=_get_ip,
            help="If command is ran without supplying argument it will check your own public IP to see if it's blacklisted",
        ),
    ],
    timeout: Annotated[
        Optional[float], typer.Option("--timeout", "-t", help="Timeout duration")
    ] = 5,
    lifetime: Annotated[
        Optional[float], typer.Option("--lifetime", "-l", help="Lifetime duration")
    ] = 5,
    blacklists: Annotated[
        Optional[str],
        typer.Option(
            "--blacklists",
            "--providers",
            "-b",
            "-p",
            help="Path to custom blacklists file",
        ),
    ] = None,
) -> None:
    """
    Checks to see if one or multiple IP addresses are blacklisted and allows for a custom text file with blacklists/providers to check through
    """

    log: Logger = ctx.obj["LOG"]
    console: Console = ctx.obj["CONSOLE"]

    log.info(f"Reversing IP: {ip}")
    reversed_ip = _reverse_ip(ip)
    log.info(f"IP reversed: {reversed_ip}")

    good = 0
    bad = 0

    if blacklists is not None:
        log.info(f"Custom blacklists file provided: {blacklists}")
        with open(blacklists, "r") as f:
            blacklists = [line.strip() for line in f.readlines()]
    else:
        scrapers = [DNSBLInfo, WhatIsMyIPAddress]
        blacklists = Scraper(scrapers).fetch()
        log.info("No blacklists file provided, scraping from default ones")
        log.info(
            f"Fetching blacklists from: {[scraper.__name__ for scraper in scrapers]}"
        )

    log.info("Starting checking progress now")
    log.info(
        f"Values:\nip: {ip}\ntimeout: {timeout}\nlifetime: {lifetime}\nblacklists: {blacklists}"
    )

    with Progress(console=console, transient=True) as progress:
        task = progress.add_task("Querying providers...", total=len(blacklists))
        log.info("Querying started...")
        iteration = 0

        for provider in blacklists:
            # will log that it starts at 1 which is ok instead of 0
            iteration += 1
            log.info(f"iteration: {iteration}")

            query = f"{reversed_ip}.{provider}"
            log.info(f"query: {query}")

            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = timeout
                resolver.lifetime = lifetime
                answer = resolver.query(query, "A")
                answer_txt = resolver.query(query, "TXT")

                if ctx.obj["VERBOSE"]:
                    console.print(
                        f"[bold green][+] {ip} listed in {provider} ({answer[0]}) ({answer_txt[0]})"
                    )
                else:
                    console.print(f"[bold green][+] {ip} listed in {provider}")
                bad += 1
            except NXDOMAIN:
                good += 1
                console.print(f"[bold red][-] {ip} not listed in {provider}")
            except Timeout:
                if ctx.obj["VERBOSE"]:
                    good += 1
                    log.info(f"timeout querying: {query}")
                    console.print(f"[bold yellow][.] Timeout querying {provider}")
            except NoNameservers:
                if ctx.obj["VERBOSE"]:
                    good += 1
                    log.info(f"no nameservers for {query}")
                    console.print(f"[bold yellow][.] No nameservers for {provider}")
            except NoAnswer:
                if ctx.obj["VERBOSE"]:
                    good += 1
                    log.info(f"no answer from: {query}")
                    console.print(f"[bold yellow][.] No answer from {provider}")
            except Exception as e:
                log.error(e)
                pass

            progress.advance(task)

    log.info("Finished querying all providers")
    log.info(f"Hits: {bad}")

    total = good + bad
    log.info(f"Results: {bad}/{total}")

    yellow = Style(color="yellow", bold=True)
    formatted_text = cleandoc(f"""
    [{yellow}][.][/] {ip}: {bad}/{total}
    """)

    log.info("Printing results to console")
    console.print(Panel(formatted_text, title=f"[{yellow}]Results[/]"))
    log.info("Command finished")

    raise typer.Exit()
