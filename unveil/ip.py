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

import asyncio

from requests import get
from typing import Optional
from aiohttp import ClientSession, ClientTimeout
from unveil.models.ip import IPv4
from pydantic import ValidationError


class IPFetcher:
    API_ENDPOINTS = {
        "Ident": "https://ident.me/json",
        "Ipify": "https://api.ipify.org/?format=json",
        "icanhazip": "https://icanhazip.com",
        "IPinfo": "https://ipinfo.io/json",
        "Country": "https://api.country.is",
        "GeoJS": "https://get.geojs.io/v1/ip/geo.json",
        "ipapi": "https://ipapi.co/json",
        # "ip-api": "http://ip-api.com/json", # looks like they require api key now
    }

    async def fetch_ip_data(
        self, session: ClientSession, name: str, url: str
    ) -> Optional[IPv4]:
        try:
            async with session.get(url, timeout=ClientTimeout(total=5)) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    data = await response.json()
                else:
                    data = {"ip": (await response.text()).strip()}

                return IPv4(**data)
        except ValidationError:
            # log.error(f"Validation error for {name}: {e}")
            return None
        except Exception:
            # log.error(f"Failed to fetch from {name}: {e}")
            return None

    async def fetch_all_sources(self) -> dict[str, IPv4]:
        async with ClientSession() as session:
            tasks = [
                self.fetch_ip_data(session, name, url)
                for name, url in self.API_ENDPOINTS.items()
            ]
            results = await asyncio.gather(*tasks)

        return {
            name: ip_info
            for name, ip_info in zip(self.API_ENDPOINTS.keys(), results)
            if ip_info
        }

        # ip_data = {}

        # for name, api_url in self.apis.items():
        #     try:
        #         ip_info = fetch_ipv4_info(api_url)
        #         ip_data[name] = ip_info
        #     except Exception as e:
        #         print(f"Error fetching data from {api_url}: {e}")

        # return ip_data


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
