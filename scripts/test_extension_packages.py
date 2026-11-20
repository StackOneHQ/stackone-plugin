"""Exercise the actual distributable archives and preserve the existing action package."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://mcp.stackone.com/mcp?extension=on&management-only=on"


def build(*args):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build-chatgpt-plugin.py"), *args],
        check=True, capture_output=True, text=True,
    )
    return Path(result.stdout.strip().splitlines()[-1])


class ExtensionPackagesTest(unittest.TestCase):
    def test_chatgpt_package_contains_setup_skill_and_bounded_endpoint(self):
        path = build("--extension")
        with ZipFile(path) as archive:
            manifest = json.loads(archive.read(".codex-plugin/plugin.json"))
            onboarding = manifest["extensions"]["com.openai"]["onboardingSkill"]
            self.assertIn(onboarding.removeprefix("./"), archive.namelist())
            self.assertEqual(manifest["skills"], "./skills/")
            self.assertEqual(json.loads(archive.read(".mcp.json"))["mcpServers"]["stackone"]["url"], ENDPOINT)
            self.assertNotIn(".claude-plugin/plugin.json", archive.namelist())
            self.assertIsNone(archive.testzip())
        first = hashlib.sha256(path.read_bytes()).digest()
        self.assertEqual(first, hashlib.sha256(build("--extension").read_bytes()).digest())

    def test_claude_variant_uses_same_skill_and_endpoint_with_its_own_manifest(self):
        path = build("--extension", "--host", "claude")
        with ZipFile(path) as archive:
            manifest = json.loads(archive.read(".claude-plugin/plugin.json"))
            self.assertEqual(manifest["skills"], "./skills/")
            self.assertIn("skills/setup/SKILL.md", archive.namelist())
            self.assertNotIn(".codex-plugin/plugin.json", archive.namelist())
            self.assertEqual(json.loads(archive.read(".mcp.json"))["mcpServers"]["stackone"]["url"], ENDPOINT)
            self.assertIsNone(archive.testzip())

    def test_default_action_package_and_source_installs_are_unchanged(self):
        with ZipFile(build()) as archive:
            self.assertEqual(json.loads(archive.read(".mcp.json"))["mcpServers"]["stackone"]["url"], "https://mcp.stackone.com/mcp")
            self.assertNotIn("skills/setup/SKILL.md", archive.namelist())
        self.assertEqual(json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]["stackone"]["url"], "https://mcp.stackone.com/mcp")


if __name__ == "__main__":
    unittest.main()
