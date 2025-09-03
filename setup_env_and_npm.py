#!/usr/bin/env python3
"""
setup_env_and_npm.py
- Create .env from .env.example.grouped or .env.example if missing.
- Run `npm install` when package.json is present.
- Print next steps to create/activate a Python venv and install requirements.
"""
from __future__ import annotations
import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent

def info(msg: str) -> None:
    print(f"[INFO] {msg}")

def warn(msg: str) -> None:
    print(f"[WARN] {msg}")

def err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)

def copy_env():
    env = ROOT / ".env"
    if env.exists():
        info(".env already exists — leaving it as-is.")
        return

    candidates = [ROOT / ".env.example.grouped", ROOT / ".env.example"]
    src = next((p for p in candidates if p.exists()), None)
    if not src:
        warn("No .env.example.grouped or .env.example found. Creating a minimal .env with a placeholder secret.")
        env.write_text("FLASK_SECRET_KEY='change-me'\n", encoding="utf-8")
        return

    content = src.read_text(encoding="utf-8", errors="ignore")
    # Ensure trailing newline for POSIX tools
    if not content.endswith("\n"):
        content += "\n"
    env.write_text(content, encoding="utf-8")
    info(f"Created .env from {src.name}")

def have_npm() -> bool:
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def run_npm_install():
    pkg = ROOT / "package.json"
    if not pkg.exists():
        info("No package.json found — skipping npm install.")
        return

    if not have_npm():
        warn("npm is not installed or not on PATH. Install Node.js first: https://nodejs.org/")
        warn("macOS:   brew install node    |   Ubuntu/Debian: sudo apt-get install -y nodejs npm")
        warn("Windows: https://nodejs.org/en/download/  (includes npm)")
        return

    info("Running `npm install` ...")
    try:
        subprocess.run(["npm", "install"], check=True, cwd=str(ROOT))
        info("npm install completed.")
    except subprocess.CalledProcessError as e:
        err(f"`npm install` failed with exit code {e.returncode}. See output above.")
    except Exception as e:
        err(f"`npm install` failed: {e}")

def print_next_steps():
    print("\n=== NEXT STEPS: Python virtual environment & dependencies ===")
    print("\n# macOS / Linux (bash/zsh):")
    print("python3 -m venv .venv")
    print("source .venv/bin/activate")
    print("pip install --upgrade pip")
    print("pip install -r requirements.txt")

    print("\n# Windows PowerShell:")
    print("py -3 -m venv .venv")
    print(".\\.venv\\Scripts\\Activate.ps1")
    print("pip install --upgrade pip")
    print("pip install -r requirements.txt")

    print("\n# Windows CMD:")
    print("py -3 -m venv .venv")
    print(".\\.venv\\Scripts\\activate.bat")
    print("pip install --upgrade pip")
    print("pip install -r requirements.txt")

    # NPM scripts (if present)
    if (ROOT / "package.json").exists():
        print("\n=== NPM (CSS build) ===")
        print("npm run build:css         # build default theme")
        print("npm run build:css:all     # build default + light + dark")
        print("npm run watch:css         # watch and rebuild on changes")

    # Optional: hint to run app (customize as needed)
    if (ROOT / "app.py").exists():
        print("\n=== Run Flask app (example) ===")
        print("export FLASK_APP=app.py        # Windows PowerShell: $Env:FLASK_APP='app.py'")
        print("flask run --reload")

def main():
    info(f"Project root: {ROOT}")
    copy_env()
    run_npm_install()
    print_next_steps()
    info("All done.")

if __name__ == '__main__':
    main()
