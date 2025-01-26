# Services that should be added that require no authentication
# https://icanhazip.com/ - no auth - average 30ms response - no rate limit (check article: https://blog.apnic.net/2021/06/17/how-a-small-free-ip-tool-survived/)
# https://www.ipify.org/ - no auth - average 100ms response - no rate limit
# https://ipinfo.io/ - no auth - average 150ms response - 50k requests/month
# https://www.myip.com/api-docs/ - no auth - average 150ms response - no rate limit
# https://country.is/ - no auth - average 75ms response - 10 requests per second rate limit
# https://www.geojs.io/ - no auth - average 150ms response - no rate limit
# https://www.geoplugin.com/ - no auth - average 100ms response - no rate limit (no info about it so assuming there is none)
# https://ip-api.com/ - no auth - average 150ms response - 45 requests per minute
# https://ipapi.co/ - no auth - average 200ms response - 30k requests per month / up-to 100 a day

from re import match

# This class will mostly be used for general IP adresses and formatting and so on


class IPv4:
    def __init__(
        self,
        ip,
        country,
        cc,
    ):
        self.ip = ip
        self.country = country
        self.cc = cc

    def _validate_ip(self, ip: str) -> bool:
        return (
            True if match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$", ip) else False
        )

    def _format_json(self) -> None: ...


class IPv6: ...
