from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.style import Style

# from unveil.logger import Logger
from unveil.utils.io import _download_file
from unveil.utils.mac import (
    _classify_mac,
    _format_block_size,
    _get_block_size,
    _get_country_code,
    _get_mac_range,
    _get_macs,
    _is_private_vendor,
    _load_csv,
    _normalize_mac,
)

app = typer.Typer()


@app.command()
def list(ctx: typer.Context) -> None:
    """Returns a list of all MAC addresses found on the system"""
    console: Console = ctx.obj["CONSOLE"]
    addresses = _get_macs()

    for address in addresses:
        console.print(address)


@app.command()
def mac(
    ctx: typer.Context,
    address: Annotated[
        str,
        typer.Argument(default_factory=_get_macs()[0]),
    ],
    path: Annotated[
        Optional[str],
        typer.Option("--path", "-p", help="Provide custom path to csv file"),
    ] = None,
):
    # log: Logger = ctx.obj["LOG"]
    console: Console = ctx.obj["CONSOLE"]

    if path is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }
        path = _download_file(
            "https://standards-oui.ieee.org/oui/oui.csv", "oui.csv", headers=headers
        )

    data = _load_csv(path)
    mac = _normalize_mac(address)
    result = data.get(mac, None)

    if not result:
        raise typer.Exit(code=1)

    oui = result["Assignment"]
    registry = result.get("Registry", "Unknown")
    org_name = result.get("Organization Name", "Unknown")
    org_addr = result.get("Organization Address", "Unknown")
    block_size = _get_block_size(registry)
    start_block, end_block, block_range = _get_mac_range(oui, block_size)
    classification, is_random = _classify_mac(address)

    # pretty printing
    b = Style(color="blue", bold=True)
    console.print(f"[{b}][+] OUI: {oui}")
    console.print(f"[{b}][+] Organization: {org_name}")
    console.print(f"[{b}][+] Organization Address: {org_addr}")
    console.print(f"[{b}][+] Country Code: {_get_country_code(org_addr)}")
    console.print(f"[{b}][+] Private?: {'Yes' if _is_private_vendor(result) else 'No'}")
    console.print(f"[{b}][+] Block size: {_format_block_size(block_size)}")
    console.print(f"[{b}][+] Block assignment type?: {registry}")
    console.print(f"[{b}][+] Block start: {start_block}")
    console.print(f"[{b}][+] Block end: {end_block}")
    console.print(f"[{b}][+] Block range: {block_range}")
    console.print(f"[{b}][+] MAC type: {classification}")
    console.print(f"[{b}][+] Random?: {is_random}")

    # if result:
    #     console.print("Vendor details:")
    #     console.print(f"OUI: {result['Assignment']}")
    #     raise typer.Exit()
    # else:
    #     typer.echo("something went wrong")
    #     raise typer.Exit(code=1)
