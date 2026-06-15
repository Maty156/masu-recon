#!/usr/bin/env python3
"""MASU Recon - Improved CLI using Click + Rich"""
import sys
import os
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))

try:
    from runner import MODULES
except Exception:
    MODULES = {}

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

console = Console()


def available_modules() -> List[str]:
    return sorted(MODULES.keys())


@click.group()
def cli():
    """MASU Recon enhanced CLI"""
    pass


@cli.command("list")
def list_modules():
    """List available recon modules"""
    mods = available_modules()
    table = Table(title="Available Modules")
    table.add_column("Name", style="cyan", no_wrap=True)
    for m in mods:
        table.add_row(m)
    console.print(table)


def _run_modules(mods: List[str], target: str, report_dir: str|None, save: bool):
    if not mods:
        console.print("[red]No modules to run.[/red]")
        return

    total = len(mods)
    console.print(f"[bold]Target:[/bold] {target}  •  [bold]Modules:[/bold] {', '.join(mods)}")

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Running modules...", total=total)

        for m in mods:
            progress.update(task, description=f"{m}")
            console.rule(f"[green]Module: {m}[/green]")
            try:
                # Call the module function. Each module prints its own output.
                MODULES[m](target, report_dir if save else None)
            except Exception as e:
                console.print(f"[red]Module {m} failed:[/red] {e}")
            progress.advance(task)

    console.print("\n[bold green]All done.[/bold green]")


@cli.command("scan")
@click.argument("target")
@click.option("--modules", "modules_opt", default="", help="Comma-separated list of modules to run (or 'all')")
@click.option("--report-dir", default="", help="Directory to save module reports")
@click.option("--save/--no-save", default=False, help="Save reports to disk (enables --report-dir)")
def scan(target, modules_opt, report_dir, save):
    """Run recon modules against TARGET"""
    if modules_opt.strip().lower() in ("all", ""):
        mods = available_modules()
    else:
        mods = [m.strip() for m in modules_opt.split(",") if m.strip()]
        invalid = [m for m in mods if m not in MODULES]
        if invalid:
            console.print(f"[red]Unknown modules:[/red] {', '.join(invalid)}")
            return

    if save and not report_dir:
        # default to reports/<target>-cli
        report_dir = os.path.join(os.getcwd(), "reports", f"{target}-cli")
        os.makedirs(report_dir, exist_ok=True)

    _run_modules(mods, target, report_dir if report_dir else None, save)


@cli.command("interactive")
@click.argument("target")
@click.option("--report-dir", default="", help="Directory to save module reports")
@click.option("--save/--no-save", default=False, help="Save reports to disk (enables --report-dir)")
def interactive(target: str, report_dir: str, save: bool):
    """Interactive module selection UI for TARGET"""
    mods = available_modules()
    if not mods:
        console.print("[red]No available modules.[/red]")
        return

    table = Table(title=f"Modules (target: {target})")
    table.add_column("#", style="magenta", no_wrap=True)
    table.add_column("Module", style="cyan")
    for i, m in enumerate(mods, start=1):
        table.add_row(str(i), m)
    console.print(table)

    prompt = "Enter module numbers separated by comma, or 'all' (e.g. 1,3,4): "
    choice = console.input(f"[bold yellow]{prompt}[/bold yellow]")
    if not choice:
        console.print("[red]No selection made.[/red]")
        return

    if choice.strip().lower() == "all":
        sel = mods
    else:
        parts = [p.strip() for p in choice.split(",") if p.strip()]
        idxs = []
        invalid = []
        for p in parts:
            if not p.isdigit():
                invalid.append(p)
                continue
            n = int(p)
            if n < 1 or n > len(mods):
                invalid.append(p)
            else:
                idxs.append(n - 1)
        if invalid:
            console.print(f"[red]Invalid selection:[/red] {', '.join(invalid)}")
            return
        # preserve order and dedupe
        sel = []
        for i in idxs:
            if mods[i] not in sel:
                sel.append(mods[i])

    if save and not report_dir:
        report_dir = os.path.join(os.getcwd(), "reports", f"{target}-cli")
        os.makedirs(report_dir, exist_ok=True)

    _run_modules(sel, target, report_dir if report_dir else None, save)


if __name__ == "__main__":
    cli()
