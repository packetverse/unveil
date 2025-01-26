# 🧰 unveil - pentesting tool

## 👀 Features

- View your IPs: Detects and displays your Public IP address from multiple sources
- Search IP information: Query information about any IP address
- IP information: Presents detailed information for all IP addresses, including country, region, asn, geolocation etc

## Installation

To install from source:

```bash
git clone https://github.com/packetverse/unveil
cd unveil
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Then you can just run the CLI from the terminal as long as you're in the virtual environment

```bash
unveil
```

Will automatically show the help dialog if run without any options/arguments
