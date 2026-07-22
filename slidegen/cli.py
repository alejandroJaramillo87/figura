"""Slidegen CLI. Thin typer app; commands land in Phases 2-4."""

import sys

import typer

from slidegen.doctor import run_doctor

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def main(ctx: typer.Context) -> None:
    """Slidegen: HTML/CSS slides rendered to looping GIFs."""
    if ctx.invoked_subcommand != "doctor" and not run_doctor(quiet=True):
        raise typer.Exit(code=1)


@app.command()
def doctor() -> None:
    """Check that ffmpeg and Playwright Chromium are available."""
    if not run_doctor():
        raise typer.Exit(code=1)


if __name__ == "__main__":
    sys.exit(app())
