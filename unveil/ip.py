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

from typing import Dict, Optional

from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from requests import get


@dataclass
class IPv4:
    ip: str
    aso: Optional[str] = None
    asn: Optional[int] = None
    continent: Optional[str] = None
    cc: Optional[str] = Field(None, serialization_alias="country_code")
    country: Optional[str] = None
    city: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = Field(None, serialization_alias="tz")
    loc: Optional[str] = None
    region: Optional[str] = None

    @model_validator(mode="after")
    def parse_location(self):
        try:
            loc = self.loc
            if "," in loc:
                lat, lon = loc.split(",")
                self.latitude = lat
                self.longitude = lon
                del self.loc
            return self
        except Exception:
            # should be logged implement later
            # print(f"Error: {e}")
            pass


class IPFetcher:
    def __init__(self):
        self.apis = {
            "Ident": "https://ident.me/json",
            "Ipify": "https://api.ipify.org/?format=json",
            "icanhazip": "https://icanhazip.com",
            "IPinfo": "https://ipinfo.io/json",
            "Country": "https://api.country.is",
            "GeoJS": "https://get.geojs.io/v1/ip/geo.json",
            "ipapi": "https://ipapi.co/json",
            # "ip-api": "http://ip-api.com/json", # looks like they require api key now
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

    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        data = response.json()
    else:
        data = {"ip": response.text.strip()}

    # key_mapping = {"country_code": "cc", "timezone": "tz"}

    # normalized_data = {}
    # for key, value in data.items():
    #     mapped_key = key_mapping.get(key, key)
    #     normalized_data[mapped_key] = value

    # ip_info = IPv4(**normalized_data)
    # print(ip_info)
    return IPv4(**data)
