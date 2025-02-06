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

from requests import get
from pydantic.dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class IPv4:
    ip: str
    aso: Optional[str] = None
    asn: Optional[int] = None
    continent: Optional[str] = None
    cc: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tz: Optional[str] = None


class IPFetcher:
    def __init__(self):
        self.apis = {
            "Ident": "https://ident.me/json",
            "Ipify": "https://api.ipify.org/?format=json",
        }

    def fetch_from_all_apis(self) -> Dict[str, IPv4]:
        ip_data = {}

        for name, api_url in self.apis.items():
            try:
                ip_info = fetch_ipv4_info(api_url)
                ip_data[name] = ip_info
            except Exception as e:
                print(f"Error fetching data from {api_url}: {e}")

        return ip_data


# add some logic to fetch from all services
def fetch_ipv4_info(api_url: str) -> IPv4:
    response = get(api_url)
    response.raise_for_status()
    data = response.json()

    ip_info = IPv4(**data)
    return ip_info
