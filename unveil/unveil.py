from .utils import _validate_ip, _get_ip, _reverse_ip
from .services import ident
from .scraper import Scraper, DNSBLInfo, WhatIsMyIPAddress
from .alias import AliasGroup

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

import typer
import dns.resolver

app = typer.Typer(
    cls=AliasGroup,
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)
state = {"verbose": False}
console = Console()

# TODO: Add custom providers option for `check` command
# TODO: Add output option for all commands
# TODO: Add custom proxies to use when querying since sometimes you can't do it with your own home network
# TODO: Add command to check if providers are online or not, verifying if they are dead or not before checking blacklist status
# TODO: Add typer callback to support verbose option across the entire CLI, verbose shouldn't be implemented in the commands it-self and it should read a global state

# TODO: This should be made a typer option with default factory set to a Scraper instance, for easier custom blacklists support
# BLACKLISTS = Scraper([DNSBLInfo, WhatIsMyIPAddress]).fetch()


@app.callback()
def main(verbose: bool = False):
    if verbose:
        state["verbose"] = True


# This command always assumes an IP is IPv4 we should add some logic to check and verify if IPv4 or IPv6
# and then use according blacklists that support IPv6 and so on
@app.command()
def check(
    ip: Annotated[Optional[str], typer.Argument(default_factory=_get_ip)],
    # verbose: Annotated[
    #     Optional[bool], typer.Option("--verbose", "-v", help="Shows more info")
    # ] = False,
    timeout: Annotated[
        Optional[float], typer.Option("--timeout", "-t", help="Timeout duration")
    ] = 5,
    lifetime: Annotated[
        Optional[float], typer.Option("--lifetime", "-l", help="Lifetime duration")
    ] = 5,
    blacklists: Annotated[
        Optional[str],
        typer.Option(
            help="Path to custom blacklists file",
        ),
    ] = None,
) -> None:
    reversed_ip = _reverse_ip(ip)
    good = 0
    bad = 0

    if blacklists is not None:
        # add logic to extract blacklists and so on from file
        print("Custom blacklists file provided")
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
@app.command(help="Fetch your Public IP")
def ip(
    raw: Annotated[
        Optional[bool], typer.Option(help="Returns your Public IP and nothing more")
    ] = False,
    json: Annotated[
        Optional[bool], typer.Option(help="Returns the JSON pretty printed")
    ] = False,
    verbose: Annotated[Optional[bool], typer.Option(help="Displays more info")] = False,
) -> None:
    if verbose:
        data = ident.ident()

    if raw:
        console.print(_get_ip())
    elif json:
        formatted_data = dumps(data, indent=4)
        console.print(Panel(formatted_data, title="[bold green]JSON[/]"))
    else:
        q = Style(color="blue", bold=True)
        formatted_data = cleandoc(f"""
        [{q}][?][/] IP address: {data["ip"]}
        [{q}][?][/] ASO: {data["aso"]}
        [{q}][?][/] ASN: {data["asn"]}
        [{q}][?][/] Continent: {data["continent"]}
        [{q}][?][/] Country Code: {data["cc"]}
        [{q}][?][/] Country: {data["country"]}
        [{q}][?][/] City: {data["city"]}
        [{q}][?][/] Postal/ZIP code: {data["postal"]}

        [{q}][?][/] Geolocation:
        [{q}][?][/] Latitude: {data["latitude"]}
        [{q}][?][/] Longitude: {data["longitude"]}
        [{q}][?][/] Timezone: {data["tz"]}
        """)

        console.print(Panel(formatted_data, title="[bold blue]IP information[/]"))


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
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Outputs all scraped blacklists to a file"),
    ] = None,
) -> None:
    blacklists = Scraper([DNSBLInfo, WhatIsMyIPAddress]).fetch()

    if output:
        output_path = Path(output)
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
