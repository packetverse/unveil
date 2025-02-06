from unveil.utils import _validate_ip, _get_ip, _reverse_ip
from unveil.scraper import Scraper, DNSBLInfo, WhatIsMyIPAddress
from unveil.alias import AliasGroup
from unveil.ip import IPFetcher
from unveil.logger import Logger
from unveil import config

from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.progress import Progress

from typing import Annotated, Optional
from inspect import cleandoc
from json import dumps
from dns.resolver import NXDOMAIN, Timeout, NoNameservers, NoAnswer
from pathlib import Path
from itertools import islice
from pydantic import ValidationError

import typer
import dns.resolver
import time

app = typer.Typer(
    cls=AliasGroup,
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)

console = Console()

BANNER = """
[bold red]███████████████████████████████████████████████████████████████████[/]
[bold red]█▌[/]                                                               [bold red]▐█[/]
[bold red]█▌[/]                                                               [bold red]▐█[/]
[bold red]█▌[/]  ███    █▄  ███▄▄▄▄    ▄█    █▄     ▄████████  ▄█   ▄█        [bold red]▐█[/]
[bold red]█▌[/]  ███    ███ ███▀▀▀██▄ ███    ███   ███    ███ ███  ███        [bold red]▐█[/]
[bold red]█▌[/]  ███    ███ ███   ███ ███    ███   ███    █▀  ███▌ ███        [bold red]▐█[/]
[bold red]█▌[/]  ███    ███ ███   ███ ███    ███  ▄███▄▄▄     ███▌ ███        [bold red]▐█[/]
[bold red]█▌[/]  ███    ███ ███   ███ ███    ███ ▀▀███▀▀▀     ███▌ ███        [bold red]▐█[/]
[bold red]█▌[/]  ███    ███ ███   ███ ███    ███   ███    █▄  ███  ███        [bold red]▐█[/]
[bold red]█▌[/]  ███    ███ ███   ███ ███    ███   ███    ███ ███  ███▌    ▄  [bold red]▐█[/]
[bold red]█▌[/]  ████████▀   ▀█   █▀   ▀██████▀    ██████████ █▀   █████▄▄██  [bold red]▐█[/]
[bold red]█▌[/]                                                    ▀          [bold red]▐█[/]
[bold red]█▌[/]                                                               [bold red]▐█[/]
[bold red]█▌[/]                                                               [bold red]▐█[/]
[bold red]███████████████████████████████████████████████████████████████████[/]
"""


def vprint(console: Console, message: str) -> None:
    if config.verbose:
        console.print(message)


# find a better way to log and verbosity doesnt mean display logs really, means just display more detailed info
# this definitely needs some working on so it can be implemented for each function
@app.callback()
def main(
    ctx: typer.Context,
    log_path: Annotated[
        Optional[str],
        typer.Option(
            "--log-path",
            "-l",
            help="Specify custom path for logs. Default is ~/.unveil",
            show_default=False,
            metavar="PATH",
        ),
    ] = None,
    verbose: Annotated[
        Optional[bool],
        typer.Option(
            "--verbose",
            "-v",
            help="Enables verbose output for all commands",
        ),
    ] = False,
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output contents to a text file",
            show_default=False,
            metavar="PATH",
        ),
    ] = None,
    banner: Annotated[
        Optional[bool],
        typer.Option(
            "--banner",
            "-b",
            help="Prints ASCII art if specified to avoid cluttering terminal",
        ),
    ] = False,
):
    global log
    log = Logger(log_path)

    log.info(f"Command invoked: {ctx.invoked_subcommand}")
    flags = "Flags specified:"

    if verbose:
        config.verbose = True
        flags += "\n--verbose"

    if output:
        config.output = output
        flags += f"\n--output={output}"

    if banner:
        console.print(BANNER)
        flags += "\n--banner"

    log.info(flags)


# This command always assumes an IP is IPv4 we should add some logic to check and verify if IPv4 or IPv6
# and then use according blacklists that support IPv6 and so on
@app.command()
def check(
    ip: Annotated[
        Optional[str],
        typer.Argument(
            metavar="TEXT",
            show_default=False,
            default_factory=_get_ip,
            help="If command is ran without this argument it will check your own Public IP to see if it's blacklisted",
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
    reversed_ip = _reverse_ip(ip)
    good = 0
    bad = 0

    if blacklists is not None:
        log.info(f"Custom blacklists file provided: {blacklists}")
        with open(blacklists, "r") as f:
            blacklists = [line.strip() for line in f.readlines()]
    else:
        blacklists = Scraper([DNSBLInfo, WhatIsMyIPAddress]).fetch()

    log.info("Starting checking progress now")
    log.info(
        f"Values:\nip: {ip}\ntimeout: {timeout}\nlifetime: {lifetime}\nblacklists: {blacklists}"
    )
    with Progress(console=console, transient=True) as progress:
        task = progress.add_task("Querying providers...", total=len(blacklists))
        log.info("Querying started...")
        for provider in blacklists:
            query = f"{reversed_ip}.{provider}"
            try:
                resolver = dns.resolver.Resolver()
                resolver.timeout = timeout
                resolver.lifetime = lifetime
                answer = resolver.query(query, "A")
                answer_txt = resolver.query(query, "TXT")

                log.info(f"querying {query}")

                if config.verbose:
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
                if config.verbose:
                    good += 1
                    log.info(f"timeout querying: {query}")
                    console.print(f"[bold yellow][.] Timeout querying {provider}")
            except NoNameservers:
                if config.verbose:
                    good += 1
                    log.info(f"no nameservers for {query}")
                    console.print(f"[bold yellow][.] No nameservers for {provider}")
            except NoAnswer:
                if config.verbose:
                    good += 1
                    log.info(f"no answer from: {query}")
                    console.print(f"[bold yellow][.] No answer from {provider}")
            except Exception as e:
                log.error(e)
                pass

            progress.advance(task)

    log.info("Progress done")
    total = good + bad
    yellow = Style(color="yellow", bold=True)
    formatted_text = cleandoc(f"""
    [{yellow}][.][/] {ip}: {bad}/{total}
    """)
    console.print(Panel(formatted_text, title=f"[{yellow}]Results[/]"))
    raise typer.Exit()


@app.command(
    help="Takes an IP address as input and checks if it's a valid IPv4 address"
)
def validate(ip: Annotated[str, typer.Argument()]) -> None:
    if _validate_ip(ip):
        console.print(f"[bold green][+] {ip} is valid[/]")
        raise typer.Exit()
    else:
        console.print(f"[bold red][-] {ip} is invalid[/]")
        raise typer.Exit(code=1)


# add different sources to fetch public ip from such as the scraper module
# make different panels and title of each panel would be where it fetched it's information
@app.command(help="Fetch your Public IP")
def ip(
    raw: Annotated[
        Optional[bool],
        typer.Option("--raw", "-r", help="Returns your Public IP and nothing more"),
    ] = False,
    json: Annotated[
        Optional[bool],
        typer.Option("--json", "-j", help="Returns the JSON pretty printed"),
    ] = False,
) -> None:
    start_time = time.time()
    fetcher = IPFetcher()

    try:
        data = fetcher.fetch_from_all_apis()
    except ValidationError as e:
        console.print(f"[bold red]Validation Error:[/] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(code=1)

    if raw:
        raw_ip = list(data.values())[0].ip if data else "No IP found"
        console.print(raw_ip)
        raise typer.Exit()
    elif json:
        formatted_data = dumps(data, indent=4)
        console.print(Panel(formatted_data, title="[bold green]JSON[/]"))
        raise typer.Exit()

    for api_name, ip_info in data.items():
        q = Style(color="blue", bold=True)
        strings = ""

        for field, value in vars(ip_info).items():
            if value:
                field_name = config.field_aliases.get(field, field)
                strings += f"[{q}][?][/] {field_name}: {value}\n"

        formatted_data = cleandoc(strings)
        console.print(Panel(formatted_data, title=f"[bold blue]{api_name}[/]"))

    end_time = time.time()
    total_time = end_time - start_time
    num_apis = len(data)

    console.print(
        Panel(
            f"[bold yellow][.][/] Fetched data from {num_apis} APIs in {total_time:.2f} seconds.",
            title="Results",
            title_align="left",
        )
    )


# add logic to output the providers to a file
@app.command(
    "blacklists, providers",
    help="Get all providers the scraper modules fetches from the web",
)
def blacklists(
    limit: Annotated[
        Optional[int],
        typer.Option(
            "--limit",
            "-l",
            help="Limit how many providers to get from all scraper modules",
        ),
    ] = 0,
) -> None:
    blacklists = Scraper([DNSBLInfo, WhatIsMyIPAddress]).fetch()

    if config.output:
        output_path = Path(config.output)
        mode = "a" if output_path.exists() else "w"

        with open(output_path, mode) as f:
            if limit > 0:
                for blacklist in islice(blacklists, limit):
                    f.write(f"{blacklist}\n")
            else:
                for blacklist in blacklists:
                    f.write(f"{blacklist}\n")
    else:
        if limit > 0:
            console.print(
                Panel(
                    "\n".join(islice(blacklists, limit)),
                    title="[bold blue]Providers[/]",
                )
            )
        else:
            console.print(Panel("\n".join(blacklists), title="[bold blue]Providers[/]"))
