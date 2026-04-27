#!/usr/bin/env python3
"""
MASU Recon - Shared utilities
"""

import json
import os
from datetime import datetime

# ─── ANSI Colors ───────────────────────────────────────────
class C:
    RED     = '\033[0;31m'
    GREEN   = '\033[0;32m'
    BLUE    = '\033[0;34m'
    CYAN    = '\033[0;36m'
    YELLOW  = '\033[1;33m'
    MAGENTA = '\033[0;35m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RESET   = '\033[0m'

def section(title):
    print(f"\n{C.BOLD}{C.BLUE}━━━ {title} ━━━{C.RESET}")

def info(msg):
    print(f"{C.CYAN}[INFO]{C.RESET} {msg}")

def success(msg):
    print(f"{C.GREEN}[✓]{C.RESET} {msg}")

def warn(msg):
    print(f"{C.YELLOW}[!]{C.RESET} {msg}")

def error(msg):
    print(f"{C.RED}[✗]{C.RESET} {msg}")

def result(key, val):
    print(f"  {C.DIM}{key:<20}{C.RESET} {C.BOLD}{val}{C.RESET}")

def bullet(val, color=C.GREEN):
    print(f"  {color}•{C.RESET} {val}")

# ─── Save module result to JSON file ───────────────────────
def save_json(report_dir, module_name, data):
    if not report_dir:
        return
    os.makedirs(report_dir, exist_ok=True)
    path = os.path.join(report_dir, f"{module_name}.json")
    with open(path, "w") as f:
        json.dump({
            "module":    module_name,
            "timestamp": datetime.now().isoformat(),
            "data":      data
        }, f, indent=2)
