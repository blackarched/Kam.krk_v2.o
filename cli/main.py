#!/usr/bin/env python3
"""
CYBER-MATRIX Elite CLI - high-tech terminal for penetration suite
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from rich.prompt import Prompt
from rich.traceback import install as rich_traceback_install

from .styles import THEME
from .ui import ascii_logo, menu, key_value_table, result_table, console
from . import commands as cmd


rich_traceback_install(show_locals=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmx",
        description="CYBER-MATRIX Elite CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("info", help="Show local system and network info")

    sp = sub.add_parser("discover", help="Discover devices in CIDR range")
    sp.add_argument("ip_range", nargs="?", default="192.168.1.0/24")

    sp = sub.add_parser("ports", help="Scan ports on target host")
    sp.add_argument("target_ip")
    sp.add_argument("--ports", default="22,80,443", dest="port_range")

    sp = sub.add_parser("simulate", help="Simulate a security test")
    sp.add_argument("target_ip")
    sp.add_argument("--type", default="general", dest="test_type")

    sp = sub.add_parser("history", help="Show recent scan history")
    sp.add_argument("--limit", type=int, default=20)

    sp = sub.add_parser("show", help="Show a previous result by ID")
    sp.add_argument("id", type=int)

    sub.add_parser("tui", help="Interactive Elite console")

    return parser


def run_info() -> int:
    info = cmd.cmd_info()
    pairs = [("Hostname", info.get("hostname", "Unknown")), ("Local IP", info.get("local_ip", "Unknown"))]
    console.print(key_value_table("Local System", pairs))
    return 0


def run_discover(ip_range: str) -> int:
    with console.status(f"[bold {THEME.accent}]Discovering devices in {ip_range}..."):
        devices = cmd.cmd_discover(ip_range)
    rows = [[d.get("ip", ""), d.get("mac", ""), d.get("hostname", ""), d.get("status", "")] for d in devices]
    console.print(result_table("Discovered Devices", ["IP", "MAC", "Hostname", "Status"], rows or [["-", "-", "-", "-"]]))
    console.print(f"[bold {THEME.muted}]Total: {len(devices)}[/]")
    return 0


def run_ports(target_ip: str, port_range: str) -> int:
    with console.status(f"[bold {THEME.accent}]Scanning {target_ip} ports {port_range}..."):
        ports = cmd.cmd_scan_ports(target_ip, port_range)
    rows = [[p.get("port", ""), p.get("service", ""), p.get("state", "")] for p in ports]
    console.print(result_table("Open Ports", ["Port", "Service", "State"], rows or [["-", "-", "-"]]))
    console.print(f"[bold {THEME.muted}]Total open: {len(ports)}[/]")
    return 0


def run_simulate(target_ip: str, test_type: str) -> int:
    with console.status(f"[bold {THEME.accent}]Simulating {test_type} test on {target_ip}..."):
        result = cmd.cmd_simulate(target_ip, test_type)
    pairs = [("Target", result.get("target", "")), ("Status", result.get("status", "")), ("Severity", result.get("severity", ""))]
    console.print(key_value_table("Simulation Result", pairs))
    findings = result.get("findings", [])
    if findings:
        console.print(result_table("Findings", ["Item"], [[f] for f in findings]))
    return 0


def run_history(limit: int) -> int:
    rows = cmd.cmd_history(limit)
    table_rows = [[r["id"], r["timestamp"], r["scan_type"], r["target"], r["status"]] for r in rows]
    console.print(result_table("Scan History", ["ID", "Timestamp", "Type", "Target", "Status"], table_rows or [["-", "-", "-", "-", "-"]]))
    return 0


def run_show(result_id: int) -> int:
    data = cmd.cmd_show_result(result_id)
    if not data:
        console.print(f"[bold {THEME.error}]No result found for ID {result_id}[/]")
        return 1
    console.print(key_value_table("Result", [("ID", str(data["id"])), ("Type", data["scan_type"]), ("Target", data["target"]), ("Status", data["status"]) ]))
    results = data.get("results", {})
    if "devices" in results:
        rows = [[d.get("ip",""), d.get("mac",""), d.get("hostname",""), d.get("status","" )] for d in results["devices"]]
        console.print(result_table("Devices", ["IP", "MAC", "Hostname", "Status"], rows))
    elif "open_ports" in results:
        rows = [[p.get("port",""), p.get("service",""), p.get("state","" )] for p in results["open_ports"]]
        console.print(result_table("Open Ports", ["Port", "Service", "State"], rows))
    else:
        console.print(results)
    return 0


def run_tui() -> int:
    console.clear()
    console.print(ascii_logo())
    items = [
        ("1", "Local info"),
        ("2", "Discover devices"),
        ("3", "Scan ports"),
        ("4", "Simulate security test"),
        ("5", "History"),
        ("6", "Show result by ID"),
        ("q", "Quit"),
    ]
    while True:
        console.print(menu(items))
        choice = Prompt.ask(f"[bold {THEME.accent}]Select" , choices=[i[0] for i in items], default="1")
        if choice == "1":
            run_info()
        elif choice == "2":
            cidr = Prompt.ask("CIDR", default="192.168.1.0/24")
            run_discover(cidr)
        elif choice == "3":
            ip = Prompt.ask("Target IP")
            ports = Prompt.ask("Ports", default="22,80,443")
            run_ports(ip, ports)
        elif choice == "4":
            ip = Prompt.ask("Target IP")
            type_ = Prompt.ask("Test type", default="general")
            run_simulate(ip, type_)
        elif choice == "5":
            run_history(20)
        elif choice == "6":
            id_ = int(Prompt.ask("Result ID"))
            run_show(id_)
        elif choice == "q":
            break
        console.print()
    return 0


def main(argv: List[str] | None = None) -> int:
    console.print(ascii_logo())
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "info":
        return run_info()
    elif args.command == "discover":
        return run_discover(args.ip_range)
    elif args.command == "ports":
        return run_ports(args.target_ip, args.port_range)
    elif args.command == "simulate":
        return run_simulate(args.target_ip, args.test_type)
    elif args.command == "history":
        return run_history(args.limit)
    elif args.command == "show":
        return run_show(args.id)
    elif args.command == "tui":
        return run_tui()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())

