from typing import Annotated, Optional

import typer

from rich.console import Console

from unveil import config
from unveil.alias import AliasGroup

from unveil.logger import Logger

from unveil.commands.blacklists import app as blacklists_app
from unveil.commands.check import app as check_app
from unveil.commands.ip import app as ip_app
from unveil.commands.tor import app as tor_app
from unveil.commands.validate import app as validate_app

app = typer.Typer(
    cls=AliasGroup,
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)

app.add_typer(blacklists_app)
app.add_typer(check_app)
app.add_typer(ip_app)
app.add_typer(tor_app)
app.add_typer(validate_app)

console = Console()


# find a better way to log and verbosity doesnt mean display logs really, means just display more detailed info
# this definitely needs some working on so it can be implemented for each function
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_path: Annotated[
        Optional[str],
        typer.Option(
            "--log-path",
            "-l",
            help="Specify custom path for logs. Default is ~/.unveil",
            show_default=False,
            metavar="PATH",
        ),
    ] = None,
    verbose: Annotated[
        Optional[bool],
        typer.Option(
            "--verbose",
            "-v",
            help="Enables verbose output for all commands",
        ),
    ] = False,
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output contents to a text file",
            show_default=False,
            metavar="PATH",
        ),
    ] = None,
    banner: Annotated[
        Optional[bool],
        typer.Option(
            "--banner",
            "-b",
            help="Prints ASCII art if specified to avoid cluttering terminal",
        ),
    ] = False,
):
    ctx.ensure_object(dict)
    log = Logger(log_path)
    log.info(f"Command invoked: {ctx.invoked_subcommand}")

    if banner:
        console.print(config.banner)

    log.info("Flags specified (raw):")
    log.info(ctx.params)

    log.info("Flags specified:")
    for param, value in ctx.params.items():
        if isinstance(value, bool):
            if value:
                log.info(f"--{param}")
        elif value is not None:
            log.info(f"--{param}={value}")

    ctx.obj["BANNER"] = banner
    ctx.obj["CONSOLE"] = console
    ctx.obj["LOG_PATH"] = log_path
    ctx.obj["LOG"] = log
    ctx.obj["OUTPUT"] = output
    ctx.obj["VERBOSE"] = verbose
