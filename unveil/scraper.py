from requests import get
from lxml import html
from typing import List


# TODO: Module should be remade so that it could also be used to fetch most blacklisted IPs with a resource like:
# https://github.com/stamparm/ipsum


# Helper functions
def _deduplicate_blacklist(blacklists: List[str]) -> List[str]:
    return list(set(blacklists))

class DNSBLInfo:
    def _fetch(self) -> List:
        try:
            response = get("https://www.dnsbl.info/dnsbl-list.php")
            tree = html.fromstring(response.text)

            return [
                list.replace("http://", "").replace("https://", "")
                for list in tree.xpath("//table//a/text()")
            ]
        except Exception:
            # add error handling/logging
            return []


class WhatIsMyIPAddress:
    def _fetch(self):
        try:
            with open("./tests/wh.html", "r") as f:
                html_string = f.read()

            tree = html.fromstring(html_string)

            return [
                list.text_content().strip()
                for list in tree.xpath(
                    "//div[@class='blacklist-results']//p[not(contains(., 'IP Blacklist Offline:'))]"
                )
                if list.text_content().strip()
            ]
        except Exception:
            # add error handling/logging here as well in future
            return []


class BlacklistMaster:
    # https://www.blacklistmaster.com/blacklists
    ...


class Scraper:
    def __init__(self, scrapers: List) -> None:
        self.scrapers = scrapers

    def fetch(self) -> List[str]:
        blacklists = []

        for scraper in self.scrapers:
            instance = scraper()
            blacklists.extend(instance._fetch())

        return _deduplicate_blacklist(blacklists)
