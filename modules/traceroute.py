#!/usr/bin/env python3
"""MASU Recon - Traceroute"""

import subprocess
import re
from utils import section, warn, error, info, save_json, C

def run(target, report_dir=None):
    section("Traceroute")

    info(f"Tracing route to {target}...")
    print(f"  {C.DIM}(max 30 hops){C.RESET}\n")

    try:
        out = subprocess.check_output(
            ["traceroute", "-m", "30", "-w", "2", target],
            stderr=subprocess.STDOUT,
            timeout=60
        ).decode(errors="ignore")
    except subprocess.TimeoutExpired:
        warn("Traceroute timed out")
        return
    except FileNotFoundError:
        error("traceroute not found — install with: sudo pacman -S traceroute")
        return
    except subprocess.CalledProcessError as e:
        out = e.output.decode(errors="ignore")
    except Exception as e:
        error(f"Traceroute failed: {e}")
        return

    hops = []
    hop_pattern = re.compile(r"^\s*(\d+)\s+(.+)$")

    print(f"  {'HOP':<5} {'HOST / IP':<45} {'RTT'}")
    print(f"  {C.DIM}{'─'*70}{C.RESET}")

    for line in out.splitlines()[1:]:  # skip header line
        m = hop_pattern.match(line)
        if not m:
            continue

        hop_num = m.group(1)
        rest    = m.group(2).strip()

        if "* * *" in rest or rest == "* * *":
            print(f"  {C.DIM}{hop_num:<5} {'* * *  (no response)':<45}{C.RESET}")
            hops.append({"hop": int(hop_num), "host": "*", "rtt": "*"})
            continue

        # Extract hostname/IP and RTT
        ip_match  = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)", rest)
        rtt_match = re.findall(r"[\d.]+ ms", rest)
        host_match = re.match(r"([^\s(]+)", rest)

        ip   = ip_match.group(1)   if ip_match   else ""
        host = host_match.group(1) if host_match else rest[:40]
        rtt  = rtt_match[0]        if rtt_match  else ""

        display_host = f"{host} ({ip})" if ip and host != ip else host

        # Color by RTT
        rtt_val = float(rtt_match[0].split()[0]) if rtt_match else 0
        if rtt_val < 50:
            rtt_color = C.GREEN
        elif rtt_val < 150:
            rtt_color = C.YELLOW
        else:
            rtt_color = C.RED

        print(f"  {C.CYAN}{hop_num:<5}{C.RESET} {display_host:<45} {rtt_color}{rtt}{C.RESET}")
        hops.append({"hop": int(hop_num), "host": display_host, "rtt": rtt})

    total_hops = len([h for h in hops if h["host"] != "*"])
    print(f"\n  {C.DIM}Total hops: {len(hops)}  |  Responding: {total_hops}{C.RESET}")

    save_json(report_dir, "traceroute", {"hops": hops, "total": len(hops)})
