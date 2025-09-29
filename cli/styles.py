#!/usr/bin/env python3
"""
CLI Visual Styles for CYBER-MATRIX Elite CLI
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    primary: str = "#c000ff"
    secondary: str = "#ff00de"
    accent: str = "#00ff41"
    muted: str = "#7a7a7a"
    warning: str = "#ffb000"
    error: str = "#ff3b3b"
    success: str = "#00ff8a"
    info: str = "#00bfff"


THEME = Theme()

