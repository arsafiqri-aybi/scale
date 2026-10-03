#!/usr/bin/env python3
"""Read-only supplemental checks; not a host validator or a security proof."""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    print("PyYAML diperlukan; pemeriksaan belum dijalankan.", file=sys.stderr)
    raise SystemExit(2)


class UniqueSafeLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys instead of silently taking the last."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in result
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    None, None, "Kunci YAML harus skalar.", key_node.start_mark
                ) from exc
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    None, None, "Kunci YAML ganda.", key_node.start_mark
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def prose_only(text):
    """Remove fenced code examples from Markdown checks."""
    output, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.fullmatch(r"\s{0,3}" + re.escape(fence[0]) +
                            "{" + str(len(fence)) + r",}\s*", line):
                fence = None
            continue
        if match:
            fence = match.group(1)
        else:
            output.append(line)
    return "\n".join(output)


def audit(root, portable=False):
    root = Path(root).absolute()
    issues = []
    stats = {"files": 0, "markdown_files": 0, "local_links": 0}

    def issue(level, code, file, message):
        issues.append({"level": level, "code": code,
                       "file": str(file), "message": message})

    if root.is_symlink() or not root.is_dir():
        issue("error", "root", ".", "Target harus direktori nyata, bukan symlink.")
        return {"ok": False, "stats": stats, "issues": issues}
    root = root.resolve()
    texts = {}

    def local_target(source, target):
        if target.startswith("#"):
            return
        try:
            url = urlsplit(target)
        except ValueError:
            issue("error", "link", source, "Tujuan tautan tidak sah.")
            return
        if url.scheme or url.netloc:
            return
        if not url.path:
            return
        stats["local_links"] += 1
        path = unquote(url.path)
        candidate = root / Path(source).parent / path
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            issue("error", "link", source, "Tujuan lokal tidak dapat diresolve.")
            return
        if Path(path).is_absolute() or not resolved.is_relative_to(root):
            issue("error", "outside", source, "Referensi lokal keluar dari folder Skill.")
        elif not candidate.exists():
            issue("error", "missing_link", source, "Referensi lokal tidak ditemukan: " + path)

    for base, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        for name in list(dirs):
            path = Path(base) / name
            if path.is_symlink():
                issue("error", "symlink", path.relative_to(root),
                      "Symlink tidak dibaca; tinjau atau gunakan berkas nyata.")
                dirs.remove(name)
        for name in sorted(files):
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            stats["files"] += 1
            if path.is_symlink():
                issue("error", "symlink", rel, "Symlink tidak dibaca.")
                continue
            if path.suffix.lower() not in {".md", ".yaml", ".yml"}:
                continue
            try:
                if path.stat().st_size > 1_000_000:
                    issue("error", "size", rel, "Teks melebihi batas baca pemeriksa (1 MB).")
                    continue
                texts[rel] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                issue("error", "read", rel, "Teks UTF-8 tidak dapat dibaca.")

    skill = texts.get("SKILL.md")
    meta = {}
    if skill is None:
        issue("error", "skill_missing", "SKILL.md", "SKILL.md tidak tersedia untuk diperiksa.")
    else:
        match = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", skill, re.S)
        if not match:
            issue("error", "frontmatter", "SKILL.md", "Frontmatter YAML tidak lengkap.")
        else:
            try:
                value = yaml.load(match.group(1), Loader=UniqueSafeLoader)
                if not isinstance(value, dict):
                    raise ValueError("Frontmatter harus mapping.")
                meta = value
            except (yaml.YAMLError, ValueError, TypeError, RecursionError):
                issue("error", "yaml", "SKILL.md", "YAML tidak sah atau memiliki kunci ganda.")
            body = skill[match.end():].strip()
            if not body:
                issue("error", "body", "SKILL.md", "Instruksi utama kosong.")
            if len(body.splitlines()) > 500:
                issue("warning", "length", "SKILL.md", "Pertimbangkan pemuatan referensi selektif.")
        name = meta.get("name")
        if not isinstance(name, str) or not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            issue("error", "name", "SKILL.md", "Nama harus 1–64 karakter huruf kecil, angka, dan tanda hubung.")
        elif portable and root.name != name:
            issue("error", "folder", "SKILL.md", "Nama folder paket portabel harus sama dengan name.")
        desc = meta.get("description")
        if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
            issue("error", "description", "SKILL.md", "Description harus teks tidak kosong, maksimal 1024 karakter.")
        if isinstance(desc, str) and ("<" in desc or ">" in desc):
            issue("warning", "description_markup", "SKILL.md", "Periksa dukungan host untuk tanda kurung sudut.")
        if set(meta) - {"name", "description"}:
            issue("warning", "fields", "SKILL.md", "Periksa field tambahan dengan validator host.")

    for rel, content in texts.items():
        if not rel.lower().endswith(".md"):
            continue
        stats["markdown_files"] += 1
        prose = prose_only(content)
        if re.search(r"\b(?:TODO|FIXME|TBD)\b|\[INSERT[^\]]*\]", prose):
            issue("warning", "placeholder", rel, "Tinjau penanda yang tampak belum selesai.")
        pattern = r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+[\"'][^\n]*?[\"'])?\s*\)"
        for link in re.finditer(pattern, prose):
            local_target(rel, link.group(1) or link.group(2))
        for link in re.finditer(r"^\s{0,3}\[[^\]\n]+\]:\s*(?:<([^>\n]+)>|(\S+))", prose, re.M):
            local_target(rel, link.group(1) or link.group(2))

    ui = texts.get("agents/openai.yaml")
    if ui is not None:
        try:
            config = yaml.load(ui, Loader=UniqueSafeLoader)
            if not isinstance(config, dict):
                raise ValueError("Metadata harus mapping.")
            interface = config.get("interface")
            if not isinstance(interface, dict):
                raise ValueError("Interface harus mapping.")
            for field in ("display_name", "short_description", "default_prompt"):
                if not isinstance(interface.get(field), str) or not interface[field].strip():
                    issue("warning", "ui_field", "agents/openai.yaml", "Tinjau field: " + field)
            short = interface.get("short_description")
            if isinstance(short, str) and not 25 <= len(short) <= 64:
                issue("warning", "ui_length", "agents/openai.yaml", "Deskripsi tampilan di luar rentang 25–64 karakter.")
            prompt, name = interface.get("default_prompt"), meta.get("name")
            if isinstance(prompt, str) and isinstance(name, str) and not re.search(
                    r"\$" + re.escape(name) + r"(?![a-z0-9-])", prompt):
                issue("warning", "ui_prompt", "agents/openai.yaml", "Prompt awal belum memanggil nama Skill yang tepat.")
            for field in ("icon_small", "icon_large"):
                if field in interface:
                    if not isinstance(interface[field], str) or not interface[field].strip():
                        issue("error", "icon", "agents/openai.yaml", "Path ikon harus teks tidak kosong.")
                    else:
                        local_target("SKILL.md", interface[field])
        except (yaml.YAMLError, ValueError, TypeError, RecursionError):
            issue("error", "ui_yaml", "agents/openai.yaml", "Metadata tampilan tidak sah atau memiliki kunci ganda.")

    return {"ok": not any(x["level"] == "error" for x in issues),
            "stats": stats, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory")
    parser.add_argument("--portable", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        report = audit(args.skill_directory, args.portable)
    except (OSError, RuntimeError) as exc:
        print("Pemeriksaan tidak selesai: " + str(exc), file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Pemeriksaan statis: " + ("LULUS" if report["ok"] else "GAGAL"))
        for item in report["issues"]:
            print(f'{item["level"]}: {item["file"]}: {item["message"]}')
        print("Tidak menguji perilaku, keamanan menyeluruh, atau pemasangan.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
