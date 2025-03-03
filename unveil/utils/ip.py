from re import match
from requests import get


# Make functions for checking validating IPv6 aswell and identifying
# only works for IPv4
def _validate_ip(ip: str) -> bool:
    return True if match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$", ip) else False


def _get_ip() -> str:
    return get("https://ident.me").text


def _reverse_ip(ip: str) -> str:
    return ".".join(reversed(ip.split(".")))
