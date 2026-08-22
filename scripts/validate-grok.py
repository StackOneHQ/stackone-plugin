#!/usr/bin/env python3
"""Validate the plugin the way xai-org/plugin-marketplace does.

CI checks out github.com/xai-org/plugin-marketplace at a pinned commit and
passes its path as argv[1]. We import xAI's own `plugin_catalog` (used by their
index generator and daily SHA-bump bot) to extract this plugin, and their
`validate-catalog` rules to check the catalog entry we will submit in the PR
(marketplace/xai-catalog-entry.json), with the sha filled from the current commit.
"""
import importlib.util, json, os, pathlib, subprocess, sys

repo = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) < 2:
    print("usage: validate-grok.py <path-to-xai-org/plugin-marketplace-checkout>"); sys.exit(2)
xai = pathlib.Path(sys.argv[1]).resolve()

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, xai / rel)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

catalog = load("plugin_catalog", "scripts/plugin_catalog.py")
validator = load("validate_catalog", "scripts/validate-catalog.py")

errors = []
extracted = catalog.extract_plugin(repo)
version = extracted.get("version")
if not version:
    errors.append("xAI extractor found no plugin version (needs .grok-plugin/plugin.json or .claude-plugin/plugin.json)")
servers = extracted.get("components", {}).get("mcpServers", [])
if [s["name"] for s in servers] != ["stackone"]:
    errors.append(f"xAI extractor expected one MCP server 'stackone', got {servers}")
elif servers[0].get("description") != "http":
    errors.append(f"xAI extractor sees transport {servers[0].get('description')!r}, expected 'http'")
for k in ("hooks", "lspServers", "commands", "agents"):
    if extracted.get("components", {}).get(k):
        errors.append(f"plugin unexpectedly ships {k}: {extracted['components'][k]} (this plugin is MCP-only)")

entry = json.loads((repo / "marketplace/xai-catalog-entry.json").read_text())
sha = os.environ.get("GITHUB_SHA") or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
entry["source"]["sha"] = sha
errors += validator.validate_entry(entry, 0)
for key in ("name", "description", "homepage", "keywords", "domains", "category"):
    if not entry.get(key):
        errors.append(f"xai catalog entry missing {key}")
manifest = json.loads((repo / ".grok-plugin/plugin.json").read_text())
if entry["name"] != manifest["name"]:
    errors.append(f"catalog entry name {entry['name']!r} != .grok-plugin/plugin.json name {manifest['name']!r}")

if errors:
    print("\n".join(errors)); sys.exit(1)
print(f"ok: xAI extractor sees {manifest['name']} v{version} with MCP server 'stackone' (http); catalog entry valid with sha {sha[:8]}")
