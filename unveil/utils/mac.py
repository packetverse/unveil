from re import findall
from csv import DictReader
from pycountry import countries
from psutil import net_if_addrs, AF_LINK
from socket import socket, AF_INET, SOCK_DGRAM

ISO_COUNTRIES = {country.alpha_2 for country in countries}
BLOCK_SIZES = {"MA-L": 2**24, "MA-M": 2**20, "MA-S": 2**12}


def _normalize_mac(mac: str) -> str:
    mac = mac.upper().replace("-", ":").replace(".", "").replace(" ", "")
    if len(mac) == 12:
        mac = ":".join(mac[i : i + 2] for i in range(0, 12, 2))
    return mac[:8].replace(":", "")


def _is_private_vendor(row: int) -> bool:
    return (
        row["Organization Name"].strip().upper() == "PRIVATE"
        and row["Organization Address"].strip() == ""
    )


def _get_block_size(registry: str) -> int | str:
    return BLOCK_SIZES.get(registry.strip().upper(), "Unknown")


def _get_country_code(address: str) -> list | str:
    if not address:
        return "Unknown"

    words = findall(r"\b[A-Z]{2}\b", address)
    country_codes = [word for word in words if word in ISO_COUNTRIES]
    return country_codes[-1] if country_codes else "Unknown"


def _oui_to_int(oui: str) -> int:
    return int(oui, 16)


def _int_to_mac(mac_int: int, length: int = 6) -> str:
    mac_hex = f"{mac_int:012X}"
    return ":".join(mac_hex[i : i + 2] for i in range(0, length * 2, 2))


def _get_mac_range(oui: str, block_size: int) -> tuple[str]:
    oui_int = int(oui.upper().ljust(12, "0"), 16)
    start_block = f"{oui_int:012X}"
    end_block = (
        f"{(oui_int + block_size - 1):012X}"
        if isinstance(block_size, int)
        else "Unknown"
    )

    return (
        start_block,
        end_block,
        f"{':'.join(start_block[i : i + 2] for i in range(0, 12, 2))} - {':'.join(end_block[i : i + 2] for i in range(0, 12, 2)) if end_block != 'Unknown' else 'Unknown'}",
    )


# not working properly, needs better logic
def _classify_mac(mac: str) -> tuple[str, bool]:
    mac_clean = mac.replace(":", "").replace("-", "").upper()
    first_byte = int(mac_clean[:2], 16)
    is_local = first_byte & 0b00000010 != 0
    is_multicast = first_byte & 0b00000001 != 0

    if is_multicast:
        classification = "Multicast"
    else:
        classification = "Unicast"

    if is_local:
        classification += " (Locally Administered)"
    else:
        classification += " (Globally Unique)"

    is_random = not is_local
    return classification, is_random


def _load_csv(path: str) -> dict:
    oui_dict = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = DictReader(f)
        for row in reader:
            oui_dict[row["Assignment"].upper()] = row
    return oui_dict


def _format_block_size(size: int) -> str:
    if not isinstance(size, int):
        return "Unknown"

    if size >= 10**6:
        return f"{size} ({size / 10**6:.2f}M)"
    elif size >= 10**3:
        return f"{size} ({size / 10**3:.2f}K)"
    else:
        return f"{size} addresses"


def _get_macs() -> list[str]:
    """
    Returns a list of MAC addresses for all NICs on the system.
    The NIC actually handling outbound traffic is placed first.
    If no NICs are found, returns an empty list.
    """
    mac_addresses = []
    nic_mac_map = {}

    for iface, addresses in net_if_addrs().items():
        for addr in addresses:
            if addr.family == AF_LINK:  # mac addr
                nic_mac_map[iface] = addr.address

    # determine which nic is handling outbound traffic
    active_nic = None
    try:
        # get the nic handling the default route
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.connect(
                ("8.8.8.8", 80)
            )  # connect to Google dns (doesn't actually send data)
            local_ip = s.getsockname()[0]  # get local IP of the active NIC

        # match local IP to its NIC
        for iface, addresses in net_if_addrs().items():
            for addr in addresses:
                if addr.family == AF_INET and addr.address == local_ip:
                    active_nic = iface
                    break
            if active_nic:
                break
    except Exception:
        pass  # fallback: if this fails, no active NIC prioritization

    # prioritize active NIC's MAC
    if active_nic and active_nic in nic_mac_map:
        mac_addresses.append(nic_mac_map.pop(active_nic))  # Move active MAC to front

    # add remaining MACs
    mac_addresses.extend(nic_mac_map.values())

    return mac_addresses  # return all values but first one is probably most accurate
