#!/usr/bin/env python3
"""Regression checks for the read-only auditor; fixtures stay in its checkout."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from audit_skill import audit


class AuditTests(unittest.TestCase):
    def setUp(self):
        checkout = Path(__file__).resolve().parents[2]
        self.temp = tempfile.TemporaryDirectory(prefix=".prompting-tests-", dir=checkout)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "sample"
        self.root.mkdir()
        self.write("SKILL.md", "---\nname: sample\ndescription: Buat ringkasan rapat.\n---\n# Instruksi\nRingkas catatan.\n")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def codes(self, **kwargs):
        return {x["code"] for x in audit(self.root, **kwargs)["issues"]}

    def test_valid_portable(self):
        self.assertTrue(audit(self.root, portable=True)["ok"])

    def test_managed_directory_keeps_identity(self):
        target = self.root.with_name("skill-123")
        self.root.rename(target)
        self.root = target
        self.assertTrue(audit(self.root)["ok"])
        self.assertIn("folder", self.codes(portable=True))

    def test_empty_required_values(self):
        self.write("SKILL.md", '---\nname: ""\ndescription: "  "\n---\nIsi\n')
        self.assertTrue({"name", "description"} <= self.codes())

    def test_duplicate_yaml_keys(self):
        self.write("SKILL.md", "---\nname: sample\nname: hidden\ndescription: Draf.\n---\nIsi\n")
        self.assertIn("yaml", self.codes())

    def test_frontmatter_non_mapping(self):
        self.write("SKILL.md", "---\n- name\n- sample\n---\nIsi\n")
        self.assertIn("yaml", self.codes())

    def test_unclosed_frontmatter(self):
        self.write("SKILL.md", "---\nname: sample\ndescription: Draf.\n")
        self.assertIn("frontmatter", self.codes())

    def test_empty_body(self):
        self.write("SKILL.md", "---\nname: sample\ndescription: Draf.\n---\n")
        self.assertIn("body", self.codes())

    def test_multiline_yaml_and_crlf(self):
        (self.root / "SKILL.md").write_bytes(b"---\r\nname: sample\r\ndescription: >\r\n  Make notes.\r\n  Use for meetings.\r\n---\r\nMake notes.\r\n")
        self.assertTrue(audit(self.root)["ok"])

    def test_missing_then_existing_reference(self):
        self.write("references/guide.md", "[Bahan](data.md)\n")
        self.assertIn("missing_link", self.codes())
        self.write("references/data.md", "Data.\n")
        self.assertTrue(audit(self.root)["ok"])

    def test_reference_style_link(self):
        self.write("references/guide.md", "Baca [bahan][a].\n[a]: missing.md\n")
        self.assertIn("missing_link", self.codes())

    def test_encoded_path_escape(self):
        self.write("references/guide.md", "[Bahan](%2e%2e/%2e%2e/private.md)\n")
        self.assertIn("outside", self.codes())

    def test_fenced_examples_are_not_live_links(self):
        self.write("references/guide.md", "````markdown\n[Contoh](missing.md)\n```\n[Masih contoh](missing2.md)\n````\n")
        self.assertTrue(audit(self.root)["ok"])

    def test_unicode_space_path_and_external_url(self):
        self.write("references/data rapat.md", "Data.\n")
        self.write("references/guide.md", "[Lokal](<data rapat.md>)\n[Web](https://example.invalid/missing)\n")
        self.assertTrue(audit(self.root)["ok"])

    def test_symlink_is_flagged(self):
        target = Path(self.temp.name) / "outside.md"
        target.write_text("Private fixture.", encoding="utf-8")
        (self.root / "linked.md").symlink_to(target)
        self.assertIn("symlink", self.codes())

    def test_ui_assets_are_root_relative(self):
        self.write("assets/icon.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write("agents/openai.yaml", 'interface:\n  display_name: "Sample"\n  short_description: "Buat ringkasan rapat yang jelas"\n  default_prompt: "Gunakan $sample untuk rapat ini."\n  icon_small: "./assets/icon.svg"\n')
        self.assertEqual(audit(self.root)["issues"], [])

    def test_invalid_ui_mapping(self):
        self.write("agents/openai.yaml", "interface: []\n")
        self.assertIn("ui_yaml", self.codes())

    def test_placeholder_is_warning(self):
        self.write("references/guide.md", "TODO lengkapi aturan.\n")
        result = audit(self.root)
        self.assertTrue(result["ok"])
        self.assertIn("placeholder", self.codes())

    def test_non_utf8_is_not_silently_skipped(self):
        (self.root / "SKILL.md").write_bytes(b"\xff\xfe")
        self.assertIn("read", self.codes())

    def test_skill_scripts_are_not_executed(self):
        sentinel = self.root / "executed"
        self.write("scripts/payload.py", "from pathlib import Path\nPath(" + repr(str(sentinel)) + ").touch()\n")
        self.assertTrue(audit(self.root)["ok"])
        self.assertFalse(sentinel.exists())

    def test_cli_json_and_failure_exit(self):
        tool = str(Path(__file__).with_name("audit_skill.py"))
        run = subprocess.run([sys.executable, tool, str(self.root), "--json"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(json.loads(run.stdout)["ok"])
        self.write("references/bad.md", "[Bahan](missing.md)\n")
        run = subprocess.run([sys.executable, tool, str(self.root), "--json"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(run.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
