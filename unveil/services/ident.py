from ..ip import IPv4, IPv6
from requests import get


# gets your ip from request
def ident() -> dict:
    return get("https://ident.me/json").json()
