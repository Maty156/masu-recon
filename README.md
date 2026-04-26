# MASU Recon Tool

```
███╗   ███╗ █████╗ ███████╗██╗   ██╗
████╗ ████║██╔══██╗██╔════╝██║   ██║
██╔████╔██║███████║███████╗██║   ██║
██║╚██╔╝██║██╔══██║╚════██║██║   ██║
██║ ╚═╝ ██║██║  ██║███████║╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝
```

**MASU Recon v1.0** — A clean, modular reconnaissance tool for ethical hacking and CTFs.  
Built with Bash + Python. Outputs to terminal with full color, saves reports as TXT + JSON.

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

```bash
git clone https://github.com/Maty156/masu-recon.git
cd masu-recon
chmod +x masu-recon.sh

# Install dependencies (Arch)
sudo pacman -S nmap whois bind-tools curl traceroute python

# Install Python dependencies
pip install requests dnspython
```

---

## Usage

```bash
# Run all modules
./masu-recon.sh example.com --all

# Run all + save report
./masu-recon.sh example.com --all -o

# Run specific modules
./masu-recon.sh example.com --whois --dns --headers

# Scan an IP
./masu-recon.sh 192.168.1.1 --nmap --traceroute

# Save output to reports/
./masu-recon.sh example.com --nmap --subdomains -o
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

| Tool | Install |
|------|---------|
| `nmap` | `sudo pacman -S nmap` |
| `whois` | `sudo pacman -S whois` |
| `dig` | `sudo pacman -S bind-tools` |
| `traceroute` | `sudo pacman -S traceroute` |
| `python3` | `sudo pacman -S python` |
| `dnspython` | `pip install dnspython` |

---

## Legal

This tool is for **educational purposes and authorized testing only**.  
Never run recon against targets you don't have permission to test.

---

**by Matyas Abraham (Maty156)**  
Part of the MASU toolkit — [github.com/Maty156](https://github.com/Maty156)
