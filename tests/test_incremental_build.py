import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IncrementalBuild(unittest.TestCase):
    def test_unchanged_sources_do_not_reextract_pages_or_reindex(self):
        manifest = json.loads((ROOT / "knowledge/manifest.json").read_text(encoding="utf-8"))
        paths = [ROOT / manifest["sources"][source]["pages"][0]["path"] for source in ("slide", "outline")]
        paths.append(ROOT / "knowledge/index/study.sqlite3")
        before = [p.stat().st_mtime_ns for p in paths]
        proc = subprocess.run([sys.executable, str(ROOT / "tools/study.py"), "build"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(before, [p.stat().st_mtime_ns for p in paths])
