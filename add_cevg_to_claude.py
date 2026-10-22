"""Add the CEVG server to Claude Desktop's config file, safely.

Run it with Claude Desktop fully closed:

    python add_cevg_to_claude.py

It asks for the Sarvam key (typing is hidden), keeps everything else in the
file as it is, saves a backup first, and refuses to touch a file it cannot
read as JSON.
"""

import getpass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

config = Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"


def masked(text: str) -> str:
    import re
    return re.sub(r"sk_[A-Za-z0-9_]+", "sk_HIDDEN", text)


def main() -> int:
    running = subprocess.run(["tasklist", "/FI", "IMAGENAME eq claude.exe"], capture_output=True, text=True).stdout
    if "claude.exe" in running.lower():
        print("Claude Desktop is still running. It would overwrite the change when it closes.")
        print("Close it with:  Get-Process claude* | Stop-Process -Force")
        print("then run this script again.")
        return 1

    shell = Path(input("Path of the cevg `shell` folder\n"
                       r"(for example C:\Users\chara\Downloads\cevg-milestone-7b\cevg\shell): ").strip().strip('"'))
    if not (shell / "cevg_shell" / "server.py").is_file():
        print(f"There is no cevg_shell\\server.py inside {shell}; check the path.")
        return 1

    data = {}
    if config.is_file():
        text = config.read_text(encoding="utf-8-sig")
        try:
            data = json.loads(text) if text.strip() else {}
        except json.JSONDecodeError as e:
            print(f"The config file is not valid JSON: {e}")
            print("Its first 30 lines, with any key hidden (safe to share):\n")
            print(masked("\n".join(text.splitlines()[:30])))
            print("\nNothing was changed. Send this output to get the exact fix.")
            return 1
        backup = config.with_suffix(".backup.json")
        shutil.copy2(config, backup)
        print(f"Backup saved as {backup}")

    key = getpass.getpass("Sarvam API key (hidden as you type or paste; Enter for none, silent videos only): ").strip()
    env = {"PYTHONPATH": str(shell)}
    if key:
        env["SARVAM_API_KEY"] = key

    servers = data.setdefault("mcpServers", {})
    servers["cevg"] = {"command": sys.executable, "args": ["-m", "cevg_shell", "serve"], "env": env}

    # No byte-order mark: Claude Desktop cannot read a file that starts with one.
    config.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Done. Servers now in the file: {', '.join(servers)}")
    print("Start Claude Desktop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
