#!/usr/bin/env python3
"""MASU Recon - WHOIS Lookup"""

import subprocess
import re
from utils import section, result, warn, error, save_json

def run(target, report_dir=None):
    section("WHOIS Lookup")

    try:
        out = subprocess.check_output(
            ["whois", target],
            stderr=subprocess.DEVNULL,
            timeout=15
        ).decode(errors="ignore")
    except subprocess.TimeoutExpired:
        warn("WHOIS timed out")
        return
    except Exception as e:
        error(f"WHOIS failed: {e}")
        return

    # Fields to extract
    fields = {
        "Domain Name":      r"Domain Name:\s*(.+)",
        "Registrar":        r"Registrar:\s*(.+)",
        "Created":          r"Creation Date:\s*(.+)",
        "Expires":          r"Expir\w+ Date:\s*(.+)",
        "Updated":          r"Updated Date:\s*(.+)",
        "Name Servers":     r"Name Server:\s*(.+)",
        "Registrant Org":   r"Registrant Organization:\s*(.+)",
        "Registrant Email": r"Registrant Email:\s*(.+)",
        "Status":           r"Domain Status:\s*(.+)",
        "DNSSEC":           r"DNSSEC:\s*(.+)",
    }

    extracted = {}
    seen = set()

    for label, pattern in fields.items():
        matches = re.findall(pattern, out, re.IGNORECASE)
        if matches:
            # For name servers, show all unique
            if label == "Name Servers":
                unique = list(dict.fromkeys(m.strip().lower() for m in matches))
                extracted[label] = unique
                result(label, ", ".join(unique[:4]))
            else:
                val = matches[0].strip()
                if val not in seen:
                    extracted[label] = val
                    seen.add(val)
                    result(label, val[:80])

    if not extracted:
        warn("No WHOIS data parsed — raw output below:")
        print(out[:500])

    save_json(report_dir, "whois", extracted)
