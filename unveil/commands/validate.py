import typer

from ipaddress import AddressValueError, IPv4Address, IPv6Address, ip_address
from typing import Annotated, Optional
from rich.console import Console

from unveil.logger import Logger

app = typer.Typer()


# currently only takes IPv4 address
@app.command()
def validate(
    ctx: typer.Context,
    ip: Annotated[str, typer.Argument()],
    raw: Annotated[
        Optional[bool],
        typer.Option("--raw", "-r", help="Only prints out if the IP is valid"),
    ] = False,
) -> None:
    """Takes an IP address as input and checks if it's a valid IPv4 address"""
    console: Console = ctx.obj["CONSOLE"]
    log: Logger = ctx.obj["LOG"]

    log.info(f"Validating: {ip}")

    try:
        ip_obj = IPv4Address(ip)
    except AddressValueError:
        console.print(f"[bold red][-] {ip} is not valid!")
        raise typer.Exit(code=1)
    except Exception as e:
        print(e)
        raise typer.Exit(code=1)

    if raw:
        print(ip)
        raise typer.Exit()

    console.print(f"[bold green][+] {ip} is a valid IPv{ip_obj.version} address")

    if ctx.obj["VERBOSE"]:
        console.print(f"[bold green][+] IP version: IPv{ip_obj.version}")
        console.print(f"[bold green][+] Private: {ip_obj.is_private}")
        console.print(f"[bold green][+] Loopback: {ip_obj.is_loopback}")
        console.print(f"[bold green][+] Global: {ip_obj.is_global}")
        console.print(f"[bold green][+] Multicast: {ip_obj.is_multicast}")
        console.print(f"[bold green][+] Reserved: {ip_obj.is_reserved}")
        console.print(f"[bold green][+] Link-local: {ip_obj.is_link_local}")
        raise typer.Exit()

    # print(ip_addr.is_private)

    # ip_obj = _validate_ip(ip)

    # if ip_obj:
    #     if raw:
    #         console.print(f"[bold green][+] {ip} is valid")
    #     else:
    #         ip_type = "IPv4" if isinstance(ip_obj, IPv4Address) else "IPv6"
    #         info = ip_info(ip_obj)

    #         console.print(f"[bold green][+] {ip_obj} is a valid {ip_type} address")

    #         if ip_type == "IPv4":
    #             first_octet = int(str(ip_obj).split(".")[0])
    #             if 0 <= first_octet <= 127:
    #                 ip_class = "Class A"
    #             elif 128 <= first_octet <= 191:
    #                 ip_class = "Class B"
    #             elif 192 <= first_octet <= 223:
    #                 ip_class = "Class C"
    #             elif 224 <= first_octet <= 239:
    #                 ip_class = "Class D (Multicast)"
    #             elif 240 <= first_octet <= 255:
    #                 ip_class = "Class E (Reserved)"
    #             else:
    #                 ip_class = "Unknown Class"

    #             console.print(f"[.] Class: {ip_class}")

    #     raise typer.Exit()
    # else:
    #     log.info(f"{ip} is not valid!")
    #     console.print(f"[bold red][-] {ip} is invalid")
    #     raise typer.Exit(code=1)

    # validate_and_analyze_ip(ip)

    # if _validate_ip(ip):
    #     log.info(f"{ip} is valid")
    #     console.print(f"[bold green][+] {ip} is valid[/]")
    #     raise typer.Exit()
    # else:
    #     log.info(f"{ip} is NOT VALID!")
    #     console.print(f"[bold red][-] {ip} is invalid[/]")
    #     raise typer.Exit(code=1)
