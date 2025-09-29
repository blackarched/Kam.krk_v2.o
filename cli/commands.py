#!/usr/bin/env python3
"""
Command implementations for Elite CLI, wrapping secure_network_tools and app DB.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List


DB_FILE = "cyber_matrix.db"


def _db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema() -> None:
    try:
        with _db_connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    scan_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    results TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.commit()
    except Exception:
        pass


def record_scan(scan_type: str, target: str, results: Dict[str, Any], status: str = "completed") -> None:
    try:
        _ensure_schema()
        with _db_connect() as conn:
            conn.execute(
                "INSERT INTO scan_results (scan_type, target, results, status) VALUES (?, ?, ?, ?)",
                (scan_type, target, json.dumps(results), status),
            )
            conn.commit()
    except Exception:
        pass


def safe_import_secure_tools():
    from secure_network_tools import secure_tools
    return secure_tools


def cmd_info() -> Dict[str, Any]:
    tools = safe_import_secure_tools()
    info = tools.get_local_network_info()
    return info


def cmd_discover(ip_range: str) -> List[Dict[str, Any]]:
    tools = safe_import_secure_tools()
    devices = tools.discover_network_devices(ip_range)
    record_scan("network_discovery", ip_range, {"devices": devices})
    return devices


def cmd_scan_ports(target_ip: str, port_range: str) -> List[Dict[str, Any]]:
    tools = safe_import_secure_tools()
    ports = tools.scan_ports_secure(target_ip, port_range)
    record_scan("port_scan", target_ip, {"open_ports": ports})
    return ports


def cmd_simulate(target_ip: str, test_type: str) -> Dict[str, Any]:
    tools = safe_import_secure_tools()
    result = tools.simulate_security_test(target_ip, test_type)
    record_scan("simulate", target_ip, result)
    return result


def cmd_history(limit: int = 20):
    try:
        _ensure_schema()
        with _db_connect() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, scan_type, target, status FROM scan_results ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return list(rows)
    except Exception:
        return []


def cmd_show_result(result_id: int):
    try:
        _ensure_schema()
        with _db_connect() as conn:
            row = conn.execute(
                "SELECT id, timestamp, scan_type, target, results, status FROM scan_results WHERE id = ?",
                (result_id,),
            ).fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "scan_type": row["scan_type"],
                "target": row["target"],
                "status": row["status"],
                "results": json.loads(row["results"]) if row["results"] else {},
            }
    except Exception:
        return None

