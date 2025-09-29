#!/usr/bin/env python3
"""
UI helpers and ASCII/ASMI art for CYBER-MATRIX Elite CLI
"""

from datetime import datetime
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from .styles import THEME


console = Console(highlight=False)


def ascii_logo() -> Text:
    art_lines = [
        "██████╗ ██╗   ██╗██████╗ ███████╗██████╗     ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗",
        "██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗    ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║██║ ██╔╝",
        "██████╔╝██║   ██║██████╔╝█████╗  ██║  ██║    ██╔████╔██║███████║   ██║   ██████╔╝██║█████╔╝ ",
        "██╔═══╝ ██║   ██║██╔══██╗██╔══╝  ██║  ██║    ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║██╔═██╗ ",
        "██║     ╚██████╔╝██║  ██║███████╗██████╔╝    ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██║  ██╗",
        "╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝",
    ]
    logo = Text()
    for line in art_lines:
        logo.append(line, style=f"bold {THEME.primary}")
        logo.append("\n")
    logo.append("CYBER-MATRIX v8.0 • Elite CLI • Holographic Ops Terminal\n", style=f"bold {THEME.accent}")
    logo.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", style=THEME.secondary)
    return logo


def frame_panel(renderable, title: str = "CYBER-MATRIX", subtitle: Optional[str] = None) -> Panel:
    return Panel(
        renderable,
        title=f"[bold {THEME.primary}]{title}[/]",
        subtitle=f"[bold {THEME.muted}]{subtitle}[/]" if subtitle else None,
        border_style=THEME.secondary,
        box=box.HEAVY,
    )


def status_progress(description: str) -> Progress:
    return Progress(
        SpinnerColumn(style=THEME.accent),
        TextColumn(f"[bold {THEME.accent}]{description}[/]"),
        BarColumn(bar_width=None, style=THEME.secondary, complete_style=THEME.accent),
        TimeElapsedColumn(),
        transient=True,
    )


def menu(items: list[tuple[str, str]]) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style=f"bold {THEME.accent}")
    table.add_column(style=f"bold {THEME.primary}")
    for key, label in items:
        table.add_row(key, label)
    return frame_panel(table, title="Elite Operations", subtitle=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def key_value_table(title: str, pairs: list[tuple[str, str]]) -> Panel:
    t = Table.grid(padding=(0, 2))
    t.add_column(style=f"bold {THEME.accent}")
    t.add_column(style=f"{THEME.primary}")
    for k, v in pairs:
        t.add_row(k, v)
    return frame_panel(t, title=title)


def result_table(title: str, columns: list[str], rows: list[list[str]]) -> Panel:
    t = Table(box=box.SIMPLE_HEAVY, border_style=THEME.secondary, show_header=True, header_style=f"bold {THEME.accent}")
    for c in columns:
        t.add_column(c)
    for row in rows:
        t.add_row(*[str(cell) for cell in row])
    return frame_panel(t, title=title)

