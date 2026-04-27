#!/usr/bin/env python3
"""MASU Recon - Report Aggregator"""

import json
import os
import sys
from datetime import datetime

def run(target, report_dir, timestamp):
    modules = ["whois", "dns", "subdomains", "headers", "nmap", "traceroute"]
    report  = {
        "tool":      "MASU Recon v1.0",
        "target":    target,
        "timestamp": timestamp,
        "generated": datetime.now().isoformat(),
        "modules":   {}
    }

    for mod in modules:
        path = os.path.join(report_dir, f"{mod}.json")
        if os.path.exists(path):
            with open(path) as f:
                report["modules"][mod] = json.load(f)

    # Write final combined report.json
    out_path = os.path.join(report_dir, "report.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: reporter.py <target> <report_dir> <timestamp>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3])
