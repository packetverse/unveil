from .utils import _validate_ip, _get_ip, _reverse_ip
from .services import ident

from rich.console import Console
from rich.panel import Panel
from rich.style import Style

# from rich.progress import track
from typing import Annotated, Optional
from inspect import cleandoc
from json import dumps
from dns.resolver import NXDOMAIN, Timeout, NoNameservers, NoAnswer
from socket import gaierror, gethostbyname

import typer
import dns.resolver

app = typer.Typer(no_args_is_help=True)
console = Console()

# add some utilty to scrape lists from sites like
# https://www.dnsbl.info/dnsbl-list.php
# https://www.dnsbl.com/
BLACKLISTS = [
    "zen.spamhaus.org",
    "b.barracudacentral.org",
    "bl.spamcop.net",
    "dnsbl.sorbs.net",
    "dnsbl-1.uceprotect.net",
    "dnsbl-2.uceprotect.net",
    "dnsbl-3.uceprotect.net",
    "cbl.abuseat.org",
    "dnsbl.dronebl.org",
    "psbl.surriel.com",
    "all.s5h.net",
    "combined.abuse.ch",
    "drone.abuse.ch",
    "ips.backscatterer.org",
    "noptr.spamrats.com",
    "relays.nether.net",
    "spam.dnsbl.anonmails.de",
    "spamrbl.imp.ch",
    "ubl.unsubscore.com",
    "z.mailspike.net",
    "blacklist.woody.ch",
    "db.wpbl.info",
    "duinv.aupads.org",
    "ix.dnsbl.manitu.net",
    "pbl.spamhaus.org",
    "orvedb.aupads.org",
    "rbl.0spam.org",
    "singular.ttk.pte.hu",
    "spam.spamrats.com",
    "spamsources.fabel.dk",
    "virus.rbl.jp",
    "bl.0spam.org",
    "bogons.cymru.com",
    "dyna.spamrats.com",
    "korea.services.net",
    "proxy.bl.gweep.ca",
    "relays.bl.gweep.ca",
    "spam.abuse.ch",
    "spambot.bls.digibase.ca",
    "ubl.lashback.com",
    "wormrbl.imp.ch",
]


# This shouldn't actually print current ip another function should be made for that but
# it should definitely be remade and it should query a lot of blacklist websites and
# return results about how many and which sites it's blacklisted on
@app.command()
def check(
    ip: Annotated[Optional[str], typer.Argument(default_factory=_get_ip)],
    verbose: Annotated[Optional[bool], typer.Option(help="Shows more info")] = False,
) -> None:
    # results = {}
    reversed_ip = _reverse_ip(ip)
    good = 0
    bad = 0

    # for provider in track(BLACKLISTS, description="Querying IP information..."):
    for provider in BLACKLISTS:
        query = f"{reversed_ip}.{provider}"
        try:
            # dnspython method
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            answer = resolver.query(query, "A")
            answer_txt = resolver.query(query, "TXT")

            # socket method
            # gethostbyname(query)

            console.print(
                f"[bold green][+] {ip} listed in {provider} ({answer[0]}) ({answer_txt[0]})[/]"
            )
            bad += 1
            # console.print(f"[bold red][-] {ip} is listed [/bold red]")
        # except gaierror:
        #     console.print(f"[bold red][-] {ip} not listed in {provider}[/]")
        #     good += 1
        except NXDOMAIN:
            good += 1
            console.print(f"[bold red][-] {ip} not listed in {provider}[/]")
        except Timeout:
            console.print(
                f"[bold yellow][.] Timeout querying {provider}"
            ) if verbose else None
        except NoNameservers:
            console.print(
                f"[bold yellow][.] No nameservers for {provider}"
            ) if verbose else False
        except NoAnswer:
            console.print(
                f"[bold yellow][.] No answer from {provider}"
            ) if verbose else False
        except Exception:
            # error should not be added to list and logging should be implemented instead
            pass

    total = good + bad
    print(f"{ip}: {bad}/{total}")


@app.command()
def validate(ip: str) -> None:
    if _validate_ip(ip):
        console.print(f"[green][+] {ip} is valid")
    else:
        console.print(f"[red][-] {ip} is invalid")


@app.command()
def ip(
    raw: Annotated[
        Optional[bool], typer.Option(help="Returns your Public IP and nothing more")
    ] = False,
    json: Annotated[
        Optional[bool], typer.Option(help="Returns the JSON pretty printed")
    ] = False,
    verbose: Annotated[Optional[bool], typer.Option(help="Displays more info")] = False,
) -> None:
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
