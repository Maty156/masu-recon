#!/usr/bin/env python3
"""MASU Recon - Subdomain Finder"""

import subprocess
import threading
from utils import section, bullet, warn, info, save_json, C

# Common subdomains wordlist
WORDLIST = [
    "www", "mail", "ftp", "smtp", "pop", "imap", "webmail",
    "admin", "panel", "dashboard", "portal", "login", "secure",
    "api", "api2", "v1", "v2", "dev", "staging", "test", "beta",
    "app", "apps", "mobile", "m", "wap",
    "blog", "shop", "store", "news", "forum", "community",
    "cdn", "static", "assets", "media", "images", "img",
    "vpn", "remote", "ssh", "rdp", "git", "gitlab", "github",
    "jenkins", "ci", "build", "deploy",
    "db", "database", "mysql", "postgres", "mongo", "redis",
    "ns1", "ns2", "dns", "dns1", "dns2",
    "mx", "mx1", "mx2", "smtp1", "smtp2",
    "support", "help", "docs", "wiki", "kb",
    "status", "monitor", "metrics", "grafana",
    "cloud", "server", "host", "node", "web", "web1", "web2",
    "old", "new", "backup", "bak",
    "internal", "intranet", "local",
    "auth", "oauth", "sso", "id", "accounts",
    "pay", "payment", "checkout", "billing",
    "files", "upload", "download", "s3",
]

found = []
lock  = threading.Lock()

def check_subdomain(subdomain, domain):
    target = f"{subdomain}.{domain}"
    try:
        out = subprocess.check_output(
            ["dig", "+short", "A", target],
            stderr=subprocess.DEVNULL,
            timeout=5
        ).decode(errors="ignore").strip()
        if out:
            ips = [l.strip() for l in out.splitlines() if l.strip()]
            with lock:
                found.append({"subdomain": target, "ips": ips})
                print(f"  {C.GREEN}✓{C.RESET} {C.BOLD}{target:<45}{C.RESET} {C.DIM}{', '.join(ips)}{C.RESET}")
    except Exception:
        pass

def run(target, report_dir=None):
    section("Subdomain Finder")

    # Strip protocol if present
    domain = target.replace("https://", "").replace("http://", "").split("/")[0]

    info(f"Scanning {len(WORDLIST)} subdomains on {domain}...")
    print(f"  {C.DIM}(this may take 30-60 seconds){C.RESET}\n")

    threads = []
    for word in WORDLIST:
        t = threading.Thread(target=check_subdomain, args=(word, domain), daemon=True)
        threads.append(t)
        t.start()
        # Limit concurrency to 30 threads at a time
        if len([t for t in threads if t.is_alive()]) >= 30:
            for t in threads:
                t.join(timeout=0.1)

    for t in threads:
        t.join()

    print("")
    if found:
        from utils import success
        success(f"Found {len(found)} subdomain(s)")
    else:
        warn("No subdomains found")

    save_json(report_dir, "subdomains", {"found": found, "total": len(found)})
