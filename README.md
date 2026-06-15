# MASU Recon Tool

```
███╗   ███╗ █████╗ ███████╗██╗   ██╗
████╗ ████║██╔══██╗██╔════╝██║   ██║
██╔████╔██║███████║███████╗██║   ██║
██║╚██╔╝██║██╔══██║╚════██║██║   ██║
██║ ╚═╝ ██║██║  ██║███████║╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝
```

**MASU Recon v1.0** — A small, modular reconnaissance tool for ethical hacking and CTFs.
Built with Bash + Python. Includes a new enhanced Python CLI (`masu_cli.py`) with a nicer terminal UI (Click + Rich), interactive selection, concurrent execution and aggregated JSON reporting.

---

## Features

| Module | Description |
|--------|-------------|
| `--whois` | WHOIS lookup — registrar, dates, nameservers |
| `--dns` | DNS enumeration — A, AAAA, MX, NS, TXT, CNAME, SOA + zone transfer attempt |
| `--subdomains` | Subdomain bruteforce using built-in wordlist (threaded) |
| `--headers` | HTTP headers grab + security headers audit with score |
| `--nmap` | Nmap port scan with service detection + risk classification |
| `--traceroute` | Traceroute with RTT color coding |

---

## Installation

Clone and make the shell launcher executable:

```bash
git clone https://github.com/Maty156/masu-recon.git
cd masu-recon
chmod +x masu-recon.sh
```

System packages (example for Arch/Manjaro):

```bash
sudo pacman -S nmap whois bind-tools curl traceroute python
```

Python dependencies for the enhanced CLI (`masu_cli.py`):

```bash
python3 -m pip install -r requirements.txt
```

---

## Usage

Shell launcher (original):

```bash
./masu-recon.sh example.com --all
./masu-recon.sh example.com --nmap --subdomains -o
```

New Python CLI (recommended) — list modules, run scans, or use interactive mode:

```bash
# List available modules
python3 masu_cli.py list

# Run modules (comma separated or 'all') and save reports
python3 masu_cli.py scan example.com --modules nmap,dns --save --report-dir reports/example.com-quick

# Interactive selection
python3 masu_cli.py interactive example.com --save --report-dir reports/example.com-quick

# Use concurrent execution (speed up multiple modules)
python3 masu_cli.py scan example.com --modules all --save --report-dir reports/example.com-quick --concurrent
```

---

## Output

Terminal output is fully colored. With `-o` flag, reports are saved to:

```
reports/
└── example.com-20260425-120000/
    ├── report.txt       ← full terminal output
    ├── report.json      ← combined JSON summary
    ├── whois.json
    ├── dns.json
    ├── subdomains.json
    ├── headers.json
    ├── nmap.json
    └── traceroute.json
```

---

## Dependencies

Core system tools and Python packages (examples):

```bash
# system
sudo pacman -S nmap whois bind-tools curl traceroute python

# python (for original modules)
python3 -m pip install requests dnspython

# python (for enhanced CLI)
python3 -m pip install -r requirements.txt
```

---

## Legal

This tool is for **educational purposes and authorized testing only**.  
Never run recon against targets you don't have permission to test.

---

**by Matyas Abraham (Maty156)**  
Part of the MASU toolkit — [github.com/Maty156](https://github.com/Maty156)
