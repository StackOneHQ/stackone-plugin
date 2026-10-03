#!/usr/bin/env python3
"""Build a reproducible public plugin ZIP without changing the multi-host manifests."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from branding_assets import branding_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extension", action="store_true",
        help="Use the native extension endpoint; requires the API release and feat_mcp_apps.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    subprocess.run([sys.executable, str(root / "scripts/check-manifests.py")], check=True)

    files = {
        name: (root / name).read_bytes()
        for name in (".codex-plugin/plugin.json", ".mcp.json", "assets/logo.svg", "LICENSE")
    }
    if args.extension:
        mcp = json.loads(files[".mcp.json"])
        mcp["mcpServers"]["stackone"]["url"] = "https://mcp.stackone.com/mcp?extension=on&tool-mode=search_execute"
        mcp["mcpServers"]["stackone"]["note"] += " Native app entrypoint: stackone_open."
        files[".mcp.json"] = (json.dumps(mcp, indent=2) + "\n").encode()
        manifest = json.loads(files[".codex-plugin/plugin.json"])
        manifest["interface"]["shortDescription"] = "Manage your connections"
        manifest["interface"]["longDescription"] = (
            "Manage StackOne connector profiles and linked accounts in ChatGPT. "
            "Search accounts, review connection status, rename or enable profiles when permitted, "
            "and link or reconnect accounts through the same StackOne Hub used by OAuth, embedded in ChatGPT. "
            "Provider sign-in may require a popup. "
            "Full credential configuration opens the existing StackOne dashboard. "
            "Management requires explicit consent and follows your current StackOne permissions."
        )
        manifest["interface"]["defaultPrompt"] = [
            "Open StackOne to review my linked accounts.",
            "Open my StackOne connector profiles.",
            "Open StackOne so I can link an account.",
        ]
        files[".codex-plugin/plugin.json"] = (json.dumps(manifest, indent=2) + "\n").encode()

    # Resolve assets from the final manifest, including extension-mode edits.
    interface = json.loads(files[".codex-plugin/plugin.json"])["interface"]
    files.update(branding_files(interface, lambda name: (root / name).read_bytes()))

    suffix = "-extension" if args.extension else ""
    destination = root / "dist" / f"stackone-chatgpt{suffix}.zip"
    destination.parent.mkdir(exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            entry = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    with ZipFile(destination) as archive:
        branding_files(interface, archive.read)
        if archive.testzip() is not None:
            raise ValueError("Plugin archive failed its integrity check")
    print(destination)


if __name__ == "__main__":
    main()
