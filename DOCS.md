# `unveil`

**Usage**:

```console
$ unveil [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-l, --log-path PATH`: Specify custom path for logs. Default is ~/.unveil
* `-v, --verbose`: Enables verbose output for all commands
* `-o, --output PATH`: Output contents to a text file
* `-b, --banner`: Prints ASCII art if specified to avoid cluttering terminal
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `check`: Checks to see if one or multiple IP...
* `validate`: Takes an IP address as input and checks if...
* `ip`: Fetch your Public IP address from various...
* `blacklists, providers`: Get all providers the scraper modules...

## `unveil check`

Checks to see if one or multiple IP addresses are blacklisted and allows for a custom text file with blacklists/providers to check through

**Usage**:

```console
$ unveil check [OPTIONS] TEXT
```

**Arguments**:

* `TEXT`: If command is ran without supplying argument it will check your own public IP to see if it&#x27;s blacklisted

**Options**:

* `-t, --timeout FLOAT`: Timeout duration  [default: 5]
* `-l, --lifetime FLOAT`: Lifetime duration  [default: 5]
* `-b, -p, --blacklists, --providers TEXT`: Path to custom blacklists file
* `--help`: Show this message and exit.

## `unveil validate`

Takes an IP address as input and checks if it&#x27;s a valid IPv4 address

**Usage**:

```console
$ unveil validate [OPTIONS] IP
```

**Arguments**:

* `IP`: [required]

**Options**:

* `-r, --raw`: Only prints out if the IP is valid
* `--help`: Show this message and exit.

## `unveil ip`

Fetch your Public IP address from various sources

**Usage**:

```console
$ unveil ip [OPTIONS]
```

**Options**:

* `-r, --raw`: Returns your Public IP and nothing more
* `-j, --json`: Returns the JSON pretty printed
* `--help`: Show this message and exit.

## `unveil blacklists, providers`

Get all providers the scraper modules fetches from the web

**Usage**:

```console
$ unveil blacklists, providers [OPTIONS]
```

**Options**:

* `-l, --limit INTEGER`: Limit how many providers to get from all scraper modules  [default: 0]
* `--help`: Show this message and exit.
