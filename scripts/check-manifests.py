#!/usr/bin/env python3
"""Fail if the per-client manifests drift from each other.

Every host reads its own manifest file, so the same facts are written several
times. This keeps name, version, description, MCP URL and legal URLs identical
across all of them, and is what CI runs.
"""
import json, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
def load(p): return json.loads((root / p).read_text())

manifests = {p: load(p) for p in [
    ".claude-plugin/plugin.json",
    ".grok-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".codex-plugin/plugin.json",
]}
mcp_files = {p: load(p) for p in ["mcp.json", ".mcp.json"]}
markets = {p: load(p) for p in [".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"]}

errors = []
ref = manifests[".claude-plugin/plugin.json"]
for path, m in manifests.items():
    for key in ("name", "version", "description", "license"):
        if m.get(key) != ref.get(key):
            errors.append(f"{path}: {key}={m.get(key)!r} != {ref.get(key)!r}")
    if m.get("author", {}).get("name") != "StackOne":
        errors.append(f"{path}: author.name must be StackOne")

urls = set()
for path, m in mcp_files.items():
    servers = m.get("mcpServers", {})
    if list(servers) != ["stackone"]:
        errors.append(f"{path}: expected exactly one server named 'stackone', got {list(servers)}")
    for s in servers.values():
        urls.add(s.get("url"))
        if s.get("type") != "http":
            errors.append(f"{path}: server type must be 'http'")
if urls != {"https://mcp.stackone.com/mcp"}:
    errors.append(f"MCP URLs differ or are wrong: {urls}")

if manifests[".cursor-plugin/plugin.json"].get("mcpServers") != "./mcp.json":
    errors.append(".cursor-plugin/plugin.json must point mcpServers at ./mcp.json")
if manifests[".codex-plugin/plugin.json"].get("mcpServers") != "./.mcp.json":
    errors.append(".codex-plugin/plugin.json must point mcpServers at ./.mcp.json")

interface = manifests[".codex-plugin/plugin.json"].get("interface", {})
for key, limit in (("displayName", 30), ("shortDescription", 30), ("developerName", 80), ("longDescription", 4000)):
    value = interface.get(key, "")
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        errors.append(f".codex-plugin/plugin.json: interface.{key} must contain 1–{limit} characters")

for path, mk in markets.items():
    entry = mk["plugins"][0]
    if entry.get("name") != ref["name"]:
        errors.append(f"{path}: plugin name {entry.get('name')!r} != {ref['name']!r}")
    if "version" in entry and entry["version"] != ref["version"]:
        errors.append(f"{path}: version {entry['version']} != {ref['version']}")

for a in ("assets/logo.png", "assets/logo.svg"):
    if not (root / a).exists():
        errors.append(f"missing {a}")

if errors:
    print("\n".join(errors)); sys.exit(1)
print(f"ok: {ref['name']} v{ref['version']} consistent across {len(manifests)} manifests, {len(mcp_files)} mcp files, {len(markets)} marketplaces")
