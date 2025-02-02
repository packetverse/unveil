from .utils import _validate_ip, _get_ip, _reverse_ip
from .scraper import Scraper, DNSBLInfo, WhatIsMyIPAddress
from .alias import AliasGroup
from .ip import IPv4, IPFetcher

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

app = typer.Typer(
    cls=AliasGroup,
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)
state = {"verbose": False, "output": None}
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

# TODO: Add custom providers option for `check` command
# TODO: Add output option for all commands
# TODO: Add custom proxies to use when querying since sometimes you can't do it with your own home network
# TODO: Add command to check if providers are online or not, verifying if they are dead or not before checking blacklist status
# TODO: Add typer callback to support verbose option across the entire CLI, verbose shouldn't be implemented in the commands it-self and it should read a global state

# TODO: This should be made a typer option with default factory set to a Scraper instance, for easier custom blacklists support
# BLACKLISTS = Scraper([DNSBLInfo, WhatIsMyIPAddress]).fetch()


# TODO: Add support for multiple output formats
@app.callback()
def main(
    verbose: Annotated[
        Optional[bool],
        typer.Option("--verbose", "-v", help="Enables verbose output for all commands"),
    ] = False,
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Output contents to a text file"),
    ] = None,
):
    console.print(BANNER)
    if verbose:
        state["verbose"] = True

    if output:
        state["output"] = output


# This command always assumes an IP is IPv4 we should add some logic to check and verify if IPv4 or IPv6
# and then use according blacklists that support IPv6 and so on
@app.command()
def check(
    ip: Annotated[Optional[str], typer.Argument(default_factory=_get_ip)],
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
    reversed_ip = _reverse_ip(ip)
    good = 0
    bad = 0

    if blacklists is not None:
        print(f"Custom blacklists file provided: {blacklists}")
        with open(blacklists, "r") as f:
            blacklists = [line.strip() for line in f.readlines()]
    else:
        blacklists = Scraper([DNSBLInfo, WhatIsMyIPAddress]).fetch()

    # for provider in track(BLACKLISTS, description="Querying IP information..."):
    with Progress(console=console, transient=True) as progress:
        task = progress.add_task("Querying providers...", total=len(blacklists))
        for provider in blacklists:
            query = f"{reversed_ip}.{provider}"
            try:
                # dnspython method
                resolver = dns.resolver.Resolver()
                resolver.timeout = timeout
                resolver.lifetime = lifetime
                answer = resolver.query(query, "A")
                answer_txt = resolver.query(query, "TXT")

                # socket method
                # gethostbyname(query)

                if state["verbose"]:
                    console.print(
                        f"[bold green][+] {ip} listed in {provider} ({answer[0]}) ({answer_txt[0]})"
                    )
                else:
                    console.print(f"[bold green][+] {ip} listed in {provider}")
                bad += 1
            # except gaierror:
            #     console.print(f"[bold red][-] {ip} not listed in {provider}[/]")
            #     good += 1
            except NXDOMAIN:
                good += 1
                console.print(f"[bold red][-] {ip} not listed in {provider}[/]")
            except Timeout:
                if state["verbose"]:
                    good += 1
                    console.print(f"[bold yellow][.] Timeout querying {provider}")
            except NoNameservers:
                if state["verbose"]:
                    good += 1
                    console.print(f"[bold yellow][.] No nameservers for {provider}")
            except NoAnswer:
                if state["verbose"]:
                    good += 1
                    console.print(f"[bold yellow][.] No answer from {provider}")
            except Exception:
                pass

            progress.advance(task)

    total = good + bad
    yellow = Style(color="yellow", bold=True)
    formatted_text = cleandoc(f"""
    [{yellow}][.][/] {ip}: {bad}/{total}
    """)
    console.print(Panel(formatted_text, title=f"[{yellow}]Results[/]"))


@app.command(
    help="Takes an IP address as input and checks if it's a valid IPv4 address"
)
def validate(ip: Annotated[str, typer.Argument()]) -> None:
    if _validate_ip(ip):
        console.print(f"[bold green][+] {ip} is valid[/]")
    else:
        console.print(f"[bold red][-] {ip} is invalid[/]")


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
    fetcher = IPFetcher()

    try:
        data = fetcher.fetch_from_all_apis()
    except ValidationError as e:
        console.print(f"[bold red]Validation Error:[/] {e}")
        return
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        return

    if raw:
        raw_ip = list(data.values())[0].ip if data else "No IP found"
        console.print(raw_ip)
        return
    elif json:
        formatted_data = dumps(data, indent=4)
        console.print(Panel(formatted_data, title="[bold green]JSON[/]"))
        return

    for api_name, ip_info in data.items():
        q = Style(color="blue", bold=True)
        formatted_data = cleandoc(f"""
        [{q}][?][/] IP address: {ip_info.ip}
        [{q}][?][/] ASO: {ip_info.aso}
        [{q}][?][/] ASN: {ip_info.asn}
        [{q}][?][/] Continent: {ip_info.continent}
        [{q}][?][/] Country Code: {ip_info.cc}
        [{q}][?][/] Country: {ip_info.country}
        [{q}][?][/] City: {ip_info.city}
        [{q}][?][/] Postal/ZIP code: {ip_info.postal}

        [{q}][?][/] Geolocation:
        [{q}][?][/] Latitude: {ip_info.latitude}
        [{q}][?][/] Longitude: {ip_info.longitude}
        [{q}][?][/] Timezone: {ip_info.tz}
        """)

        console.print(Panel.fit(formatted_data, title=f"[bold blue]{api_name}[/]"))


# add logic to output the providers to a file
@app.command(
    "blacklists, providers",
    help="Get all provider-s the scraper modules fetches from the web",
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

    if state["output"]:
        output_path = Path(state["output"])
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
