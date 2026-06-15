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
import subprocess
import json
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def _run_modules(mods: List[str], target: str, report_dir: Optional[str], save: bool, concurrent: bool = False):
    if not mods:
        console.print("[red]No modules to run.[/red]")
        return

    total = len(mods)
    console.print(f"[bold]Target:[/bold] {target}  •  [bold]Modules:[/bold] {', '.join(mods)}")

    # Ensure report dir exists if saving
    if save and report_dir:
        os.makedirs(report_dir, exist_ok=True)

    def run_module_subproc(module_name: str) -> dict:
        cmd = ["python3", "modules/runner.py", module_name, target]
        if save and report_dir:
            cmd.append(report_dir)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            stdout = proc.stdout
            stderr = proc.stderr
            return {"module": module_name, "returncode": proc.returncode, "stdout": stdout, "stderr": stderr}
        except Exception as e:
            return {"module": module_name, "returncode": -1, "stdout": "", "stderr": str(e)}

    results = []

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Running modules...", total=total)

        if concurrent and total > 1:
            with ThreadPoolExecutor(max_workers=min(8, total)) as ex:
                futures = {ex.submit(run_module_subproc, m): m for m in mods}
                for fut in as_completed(futures):
                    m = futures[fut]
                    progress.update(task, description=f"{m}")
                    console.rule(f"[green]Module: {m}[/green]")
                    res = fut.result()
                    # print captured stdout/stderr
                    if res.get("stdout"):
                        console.print(res["stdout"])
                    if res.get("stderr"):
                        console.print(f"[red]{res['stderr']}[/red]")
                    results.append(res)
                    progress.advance(task)
        else:
            for m in mods:
                progress.update(task, description=f"{m}")
                console.rule(f"[green]Module: {m}[/green]")
                res = run_module_subproc(m)
                if res.get("stdout"):
                    console.print(res["stdout"])
                if res.get("stderr"):
                    console.print(f"[red]{res['stderr']}[/red]")
                results.append(res)
                progress.advance(task)

    console.print("\n[bold green]All done.[/bold green]")

    # Aggregate per-module JSON reports into a single report.json if saving
    if save and report_dir:
        aggregated = {}
        for path in glob.glob(os.path.join(report_dir, "*.json")):
            name = os.path.splitext(os.path.basename(path))[0]
            try:
                with open(path, "r") as fh:
                    aggregated[name] = json.load(fh)
            except Exception:
                # skip invalid json
                aggregated[name] = {"_file": path}

        # add runner metadata
        aggregated["_meta"] = {"target": target, "modules": mods}
        out_path = os.path.join(report_dir, "report.json")
        try:
            with open(out_path, "w") as fh:
                json.dump(aggregated, fh, indent=2)
            console.print(f"[bold]Aggregated report saved:[/bold] {out_path}")
        except Exception as e:
            console.print(f"[red]Failed to write aggregated report:[/red] {e}")


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
