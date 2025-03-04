import time

from re import match
from requests import get

from unveil.ip import IPv4


# Make functions for checking validating IPv6 aswell and identifying
# only works for IPv4
def _validate_ip(ip: str) -> bool:
    return True if match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$", ip) else False


def _get_ip() -> str:
    return get("https://ident.me").text


def _reverse_ip(ip: str) -> str:
    return ".".join(reversed(ip.split(".")))


async def _fetch_api(api_url: str) -> IPv4:
    response = get(api_url)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        data = response.json()
    else:
        data = {"ip": response.text.strip()}

    return IPv4(**data)
