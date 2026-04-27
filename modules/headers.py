#!/usr/bin/env python3
"""MASU Recon - HTTP Headers Grab"""

import urllib.request
import urllib.error
import ssl
from utils import section, result, bullet, warn, error, success, save_json, C

# Security headers to specifically check for
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "X-XSS-Protection",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
]

def fetch_headers(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MASU-Recon/1.0"})
        res = urllib.request.urlopen(req, timeout=10, context=ctx)
        return dict(res.headers), res.status, res.url
    except urllib.error.HTTPError as e:
        return dict(e.headers), e.code, url
    except Exception as e:
        return None, None, str(e)

def run(target, report_dir=None):
    section("HTTP Headers")

    # Try HTTPS first, fallback to HTTP
    domain = target.replace("https://", "").replace("http://", "").split("/")[0]
    urls   = [f"https://{domain}", f"http://{domain}"]

    headers, status, final_url = None, None, None
    for url in urls:
        headers, status, final_url = fetch_headers(url)
        if headers:
            break

    if not headers:
        warn(f"Could not reach {domain}")
        return

    data = {"url": final_url, "status": status, "headers": {}, "security": {}}

    # ─── General headers ───────────────────────────────────
    print(f"\n  {C.BOLD}{C.CYAN}General:{C.RESET}")
    interesting = [
        "Server", "X-Powered-By", "Content-Type", "Location",
        "Set-Cookie", "Via", "X-Cache", "CF-Ray", "X-Varnish"
    ]
    result("Status Code", f"{status}")
    result("Final URL",   final_url)
    for h in interesting:
        val = headers.get(h) or headers.get(h.lower())
        if val:
            result(h, val[:80])
            data["headers"][h] = val

    # ─── Security headers audit ────────────────────────────
    print(f"\n  {C.BOLD}{C.CYAN}Security Headers Audit:{C.RESET}")
    present = 0
    for h in SECURITY_HEADERS:
        val = headers.get(h) or headers.get(h.lower())
        if val:
            print(f"  {C.GREEN}✓{C.RESET} {h:<40} {C.DIM}{val[:50]}{C.RESET}")
            data["security"][h] = {"present": True, "value": val}
            present += 1
        else:
            print(f"  {C.RED}✗{C.RESET} {C.DIM}{h}{C.RESET}")
            data["security"][h] = {"present": False}

    # ─── Score ─────────────────────────────────────────────
    score = int((present / len(SECURITY_HEADERS)) * 100)
    color = C.GREEN if score >= 70 else C.YELLOW if score >= 40 else C.RED
    print(f"\n  {C.BOLD}Security Score:{C.RESET} {color}{score}%{C.RESET} ({present}/{len(SECURITY_HEADERS)} headers present)")
    data["security_score"] = score

    save_json(report_dir, "headers", data)
