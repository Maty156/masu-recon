#!/usr/bin/env python3
"""MASU Recon - DNS Enumeration"""

import subprocess
from utils import section, result, bullet, warn, error, save_json, C

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "PTR"]

def dig(target, rtype):
    try:
        out = subprocess.check_output(
            ["dig", "+short", rtype, target],
            stderr=subprocess.DEVNULL,
            timeout=10
        ).decode(errors="ignore").strip()
        return [l.strip() for l in out.splitlines() if l.strip()] if out else []
    except Exception:
        return []

def run(target, report_dir=None):
    section("DNS Enumeration")

    data = {}

    for rtype in RECORD_TYPES:
        records = dig(target, rtype)
        if records:
            print(f"\n  {C.BOLD}{C.CYAN}{rtype} Records:{C.RESET}")
            for r in records:
                bullet(r)
            data[rtype] = records
        else:
            print(f"  {C.DIM}{rtype:<6} — no records{C.RESET}")

    # Zone transfer attempt (educational — usually blocked)
    print(f"\n  {C.BOLD}{C.CYAN}Zone Transfer (AXFR):{C.RESET}")
    ns_records = data.get("NS", [])
    if ns_records:
        ns = ns_records[0].rstrip(".")
        try:
            axfr = subprocess.check_output(
                ["dig", "AXFR", target, f"@{ns}"],
                stderr=subprocess.DEVNULL,
                timeout=10
            ).decode(errors="ignore").strip()
            if "Transfer failed" in axfr or not axfr:
                bullet("Zone transfer blocked (expected)", C.C.DIM if hasattr(C, 'C') else C.YELLOW)
            else:
                bullet("Zone transfer succeeded!", C.C.RED if hasattr(C, 'C') else C.GREEN)
                data["AXFR"] = axfr[:500]
        except Exception:
            bullet("Zone transfer blocked (expected)", C.YELLOW)
    else:
        warn("No NS records found for zone transfer attempt")

    if not data:
        warn("No DNS records found")

    save_json(report_dir, "dns", data)
