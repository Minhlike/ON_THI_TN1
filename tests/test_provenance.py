import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from study import audit_data


class Provenance(unittest.TestCase):
    def test_full_audit(self):
        manifest = json.loads((ROOT / "knowledge/manifest.json").read_text(encoding="utf-8"))
        result = audit_data(manifest)
        self.assertTrue(result["ok"], result["errors"][:10])
