# -*- coding: utf-8 -*-
"""Discover the local PHP binary and enable pdo_mysql without editing php.ini."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


def php_bin() -> str:
    for name in ("php", "php.exe"):
        found = shutil.which(name)
        if found:
            return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "kpn-tools" / "php" / "php.exe"
    if local.is_file():
        return str(local)
    return ""


def php_command(php: str) -> list[str]:
    """Return a PHP argv prefix. Loads pdo_mysql from the binary's ext dir when needed."""
    probe = subprocess.run(
        [php, "-m"],
        capture_output=True,
        text=True,
        timeout=20,
    )
    loaded = (probe.stdout or "") + "\n" + (probe.stderr or "")
    if re.search(r"(?m)^pdo_mysql$", loaded):
        return [php]
    ext = Path(php).resolve().parent / "ext"
    for name in ("php_pdo_mysql.dll", "pdo_mysql.so"):
        if (ext / name).is_file():
            return [php, "-d", f"extension_dir={ext}", "-d", f"extension={name}"]
    return [php]
