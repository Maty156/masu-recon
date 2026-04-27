#!/usr/bin/env python3
"""
MASU Recon - Module Runner
Dispatches to individual recon modules and handles output
"""

import sys
import os

# Add modules dir to path
sys.path.insert(0, os.path.dirname(__file__))

from whois_lookup import run as whois_run
from dns_enum    import run as dns_run
from subdomains  import run as subdomains_run
from headers     import run as headers_run
from nmap_scan   import run as nmap_run
from traceroute  import run as traceroute_run

MODULES = {
    "whois":      whois_run,
    "dns":        dns_run,
    "subdomains": subdomains_run,
    "headers":    headers_run,
    "nmap":       nmap_run,
    "traceroute": traceroute_run,
}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: runner.py <module> <target> [report_dir]")
        sys.exit(1)

    module     = sys.argv[1]
    target     = sys.argv[2]
    report_dir = sys.argv[3] if len(sys.argv) > 3 else ""

    if module not in MODULES:
        print(f"Unknown module: {module}")
        sys.exit(1)

    MODULES[module](target, report_dir if report_dir else None)
