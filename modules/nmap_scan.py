#!/usr/bin/env python3
"""MASU Recon - Nmap Port Scan"""

import subprocess
import re
from utils import section, result, bullet, warn, error, success, info, save_json, C

# Port risk classification
HIGH_RISK   = {21, 23, 445, 1433, 3306, 3389, 5432, 5900, 6379, 27017}
MEDIUM_RISK = {20, 22, 25, 110, 143, 161, 512, 513, 514, 1080, 8080, 8443}

def classify_port(port):
    if port in HIGH_RISK:
        return C.RED, "HIGH"
    if port in MEDIUM_RISK:
        return C.YELLOW, "MEDIUM"
    return C.GREEN, "LOW"

def run(target, report_dir=None):
    section("Nmap Port Scan")

    info("Running fast scan (top 1000 ports + service detection)...")
    print(f"  {C.DIM}This may take 1-3 minutes...{C.RESET}\n")

    try:
        out = subprocess.check_output(
            ["nmap", "-sV", "--open", "-T4", "--top-ports", "1000", target],
            stderr=subprocess.DEVNULL,
            timeout=180
        ).decode(errors="ignore")
    except subprocess.TimeoutExpired:
        warn("Nmap timed out after 3 minutes")
        return
    except FileNotFoundError:
        error("nmap not found — install with: sudo pacman -S nmap")
        return
    except Exception as e:
        error(f"Nmap failed: {e}")
        return

    # Parse open ports
    port_pattern = re.compile(
        r"(\d+)/(\w+)\s+(\w+)\s+(\S+)\s*(.*)"
    )

    ports = []
    open_count = 0

    print(f"  {'PORT':<10} {'PROTO':<8} {'STATE':<10} {'SERVICE':<15} {'VERSION':<25} {'RISK'}")
    print(f"  {C.DIM}{'─'*85}{C.RESET}")

    for line in out.splitlines():
        m = port_pattern.match(line.strip())
        if m:
            port, proto, state, service, version = m.groups()
            if state == "open":
                port_num  = int(port)
                color, risk = classify_port(port_num)
                print(f"  {color}{port:<10}{C.RESET} {proto:<8} {C.GREEN}{state:<10}{C.RESET} {service:<15} {C.DIM}{version[:25]:<25}{C.RESET} {color}[{risk}]{C.RESET}")
                ports.append({
                    "port": port_num, "proto": proto,
                    "state": state, "service": service,
                    "version": version.strip(), "risk": risk
                })
                open_count += 1

    print(f"\n  {C.DIM}{'─'*85}{C.RESET}")

    # OS detection hint from nmap output
    os_match = re.search(r"OS details?:\s*(.+)", out)
    if os_match:
        result("OS Guess", os_match.group(1).strip())

    # Summary
    high   = sum(1 for p in ports if p["risk"] == "HIGH")
    medium = sum(1 for p in ports if p["risk"] == "MEDIUM")

    print(f"\n  {C.BOLD}Open Ports:{C.RESET} {open_count}  |  "
          f"{C.RED}High Risk: {high}{C.RESET}  |  "
          f"{C.YELLOW}Medium Risk: {medium}{C.RESET}")

    if open_count == 0:
        warn("No open ports found (target may be firewalled)")

    save_json(report_dir, "nmap", {"ports": ports, "open_count": open_count})
