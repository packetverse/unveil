import typer

from typing import Annotated, Optional
from rich.console import Console

from unveil.alias import AliasGroup
from unveil.commands.blacklists import app as blacklists_app
from unveil.commands.check import app as check_app
from unveil.commands.ip import app as ip_app
from unveil.commands.mac import app as mac_app
from unveil.commands.tor import app as tor_app
from unveil.commands.validate import app as validate_app
from unveil.logger import Logger
from unveil import __version__

app = typer.Typer(
    cls=AliasGroup,
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "-h"]},
)

app.add_typer(check_app)
app.add_typer(validate_app)
app.add_typer(ip_app)
app.add_typer(mac_app, name="mac", no_args_is_help=True)
app.add_typer(tor_app)
app.add_typer(blacklists_app)


def version_callback(value: bool) -> None:
    if value:
        print(__version__)
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def callback(
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
    quiet: Annotated[
        Optional[bool],
        typer.Option(
            "--quiet",
            "-q",
            envvar="UNVEIL_QUIET",
            help="Ensures nothing is printed to the console",
        ),
    ] = False,
    color: Annotated[
        Optional[bool],
        typer.Option(
            "--color/--no-color",
            envvar="UNVEIL_COLOR",
            help="Control the use of color in output",
            show_default=False,
        ),
    ] = True,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            help="Displays the current version",
        ),
    ] = False,
):
    if quiet:
        console = Console(quiet=True)
    elif color:
        console = Console()
    elif not color:
        console = Console(no_color=True)

    ctx.ensure_object(dict)
    log = Logger(log_path, verbose)
    log.info(f"Command invoked: {ctx.invoked_subcommand}")

    log.info("Flags specified (raw):")
    log.info(ctx.params)

    log.info("Flags specified:")
    for param, value in ctx.params.items():
        if isinstance(value, bool):
            if value:
                log.info(f"--{param}")
        elif value is not None:
            log.info(f"--{param}={value}")

    ctx.obj["CONSOLE"] = console
    ctx.obj["LOG_PATH"] = log_path
    ctx.obj["LOG"] = log
    ctx.obj["VERBOSE"] = verbose
