#!/usr/bin/env bash
# ███╗   ███╗ █████╗ ███████╗██╗   ██╗
# ████╗ ████║██╔══██╗██╔════╝██║   ██║
# ██╔████╔██║███████║███████╗██║   ██║
# ██║╚██╔╝██║██╔══██║╚════██║██║   ██║
# ██║ ╚═╝ ██║██║  ██║███████║╚██████╔╝
# ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝
#
# MASU Recon Tool v1.0
# by Matyas Abraham (Maty156)
# https://github.com/Maty156/masu-recon

set -e

# ─── Colors ────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ─── Helpers ───────────────────────────────────────────────
info()    { echo -e "${CYAN}[INFO]${RESET} $1"; }
success() { echo -e "${GREEN}[✓]${RESET} $1"; }
warn()    { echo -e "${YELLOW}[!]${RESET} $1"; }
error()   { echo -e "${RED}[✗]${RESET} $1"; }
section() { echo -e "\n${BOLD}${BLUE}━━━ $1 ━━━${RESET}"; }

# ─── Spinner ───────────────────────────────────────────────
spinner() {
    local pid=$1 msg=$2
    local frames=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    while kill -0 "$pid" 2>/dev/null; do
        for frame in "${frames[@]}"; do
            printf "\r  ${CYAN}%s${RESET} %s" "$frame" "$msg"
            sleep 0.1
        done
    done
    printf "\r%-60s\r" " "
}

# ─── Banner ────────────────────────────────────────────────
banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
███╗   ███╗ █████╗ ███████╗██╗   ██╗
████╗ ████║██╔══██╗██╔════╝██║   ██║
██╔████╔██║███████║███████╗██║   ██║
██║╚██╔╝██║██╔══██║╚════██║██║   ██║
██║ ╚═╝ ██║██║  ██║███████║╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝
EOF
    echo -e "${RESET}${BOLD}  MASU Recon Tool v1.0${RESET}  ${DIM}by Matyas Abraham${RESET}"
    echo -e "  ${DIM}https://github.com/Maty156/masu-recon${RESET}\n"
}

# ─── Usage ─────────────────────────────────────────────────
usage() {
    banner
    echo -e "  ${BOLD}Usage:${RESET}"
    echo -e "    ${CYAN}./masu-recon.sh${RESET} ${YELLOW}<target>${RESET} ${DIM}[options]${RESET}\n"
    echo -e "  ${BOLD}Modules:${RESET}"
    echo -e "    ${GREEN}--all${RESET}         Run all modules"
    echo -e "    ${GREEN}--whois${RESET}       WHOIS lookup"
    echo -e "    ${GREEN}--dns${RESET}         DNS enumeration"
    echo -e "    ${GREEN}--subdomains${RESET}  Subdomain finder"
    echo -e "    ${GREEN}--headers${RESET}     HTTP headers grab"
    echo -e "    ${GREEN}--nmap${RESET}        Nmap port scan"
    echo -e "    ${GREEN}--traceroute${RESET}  Traceroute\n"
    echo -e "  ${BOLD}Options:${RESET}"
    echo -e "    ${GREEN}-o, --output${RESET}  Save report to file (txt + json)"
    echo -e "    ${GREEN}-h, --help${RESET}    Show this help\n"
    echo -e "  ${BOLD}Examples:${RESET}"
    echo -e "    ${DIM}./masu-recon.sh example.com --all -o${RESET}"
    echo -e "    ${DIM}./masu-recon.sh example.com --whois --dns${RESET}"
    echo -e "    ${DIM}./masu-recon.sh 192.168.1.1 --nmap --traceroute${RESET}\n"
    exit 0
}

# ─── Dependency Check ──────────────────────────────────────
check_deps() {
    section "Checking dependencies"
    local missing=()
    local deps=(nmap whois dig curl traceroute python3)

    for dep in "${deps[@]}"; do
        if command -v "$dep" &>/dev/null; then
            success "$dep found"
        else
            warn "$dep not found"
            missing+=("$dep")
        fi
    done

    # Python modules
    if command -v python3 &>/dev/null; then
        python3 -c "import requests, dns.resolver, json, subprocess" 2>/dev/null \
            && success "Python modules OK" \
            || warn "Some Python modules missing — run: pip install requests dnspython"
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        warn "Missing: ${missing[*]}"
        warn "Install with: sudo pacman -S ${missing[*]}"
    fi
    echo ""
}

# ─── Parse Args ────────────────────────────────────────────
TARGET=""
RUN_WHOIS=false
RUN_DNS=false
RUN_SUBDOMAINS=false
RUN_HEADERS=false
RUN_NMAP=false
RUN_TRACEROUTE=false
SAVE_OUTPUT=false

[[ $# -eq 0 ]] && usage

TARGET="$1"
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all)         RUN_WHOIS=true; RUN_DNS=true; RUN_SUBDOMAINS=true
                       RUN_HEADERS=true; RUN_NMAP=true; RUN_TRACEROUTE=true ;;
        --whois)       RUN_WHOIS=true ;;
        --dns)         RUN_DNS=true ;;
        --subdomains)  RUN_SUBDOMAINS=true ;;
        --headers)     RUN_HEADERS=true ;;
        --nmap)        RUN_NMAP=true ;;
        --traceroute)  RUN_TRACEROUTE=true ;;
        -o|--output)   SAVE_OUTPUT=true ;;
        -h|--help)     usage ;;
        *) warn "Unknown option: $1" ;;
    esac
    shift
done

# ─── Output setup ──────────────────────────────────────────
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
REPORT_DIR="./reports/${TARGET}-${TIMESTAMP}"
REPORT_TXT="${REPORT_DIR}/report.txt"
REPORT_JSON="${REPORT_DIR}/report.json"

if $SAVE_OUTPUT; then
    mkdir -p "$REPORT_DIR"
    info "Reports will be saved to: ${REPORT_DIR}"
fi

# Tee output to file if saving
tee_output() {
    if $SAVE_OUTPUT; then
        tee -a "$REPORT_TXT"
    else
        cat
    fi
}

# ─── Main ──────────────────────────────────────────────────
banner
echo -e "  ${BOLD}Target:${RESET} ${YELLOW}${TARGET}${RESET}"
echo -e "  ${BOLD}Time:${RESET}   ${DIM}$(date)${RESET}"
echo -e "  ${BOLD}Output:${RESET} ${DIM}$(if $SAVE_OUTPUT; then echo "$REPORT_DIR"; else echo "terminal only"; fi)${RESET}\n"

check_deps

# Write report header
if $SAVE_OUTPUT; then
    {
        echo "MASU Recon Report"
        echo "Target:    $TARGET"
        echo "Date:      $(date)"
        echo "═══════════════════════════════════════"
    } > "$REPORT_TXT"
fi

# ─── Run Python Modules ────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_RUNNER="$SCRIPT_DIR/modules/runner.py"

run_module() {
    local module=$1
    python3 "$PY_RUNNER" "$module" "$TARGET" \
        "$( $SAVE_OUTPUT && echo "$REPORT_DIR" || echo "" )" 2>/dev/null | tee_output
}

$RUN_WHOIS      && run_module "whois"
$RUN_DNS        && run_module "dns"
$RUN_SUBDOMAINS && run_module "subdomains"
$RUN_HEADERS    && run_module "headers"
$RUN_NMAP       && run_module "nmap"
$RUN_TRACEROUTE && run_module "traceroute"

# ─── Save JSON summary ─────────────────────────────────────
if $SAVE_OUTPUT; then
    python3 "$SCRIPT_DIR/modules/reporter.py" "$TARGET" "$REPORT_DIR" "$TIMESTAMP"
    echo ""
    success "Report saved: ${REPORT_TXT}"
    success "JSON saved:   ${REPORT_JSON}"
fi

echo -e "\n${GREEN}${BOLD}━━━ Recon Complete ━━━${RESET}\n"
