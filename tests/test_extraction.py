import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from study import parse_page, page_path


class ExtractionIntegrity(unittest.TestCase):
    def test_each_source_page_has_record_and_matching_hash(self):
        manifest = json.loads((ROOT / "knowledge/manifest.json").read_text(encoding="utf-8"))
        for source_id in ("slide", "outline"):
            source = manifest["sources"][source_id]
            self.assertEqual(source["page_count"], len(source["pages"]))
            self.assertEqual(source["sha256"], hashlib.sha256((ROOT / source["file"]).read_bytes()).hexdigest())
            for number, record in enumerate(source["pages"], 1):
                self.assertEqual(number, record["pdf_page"])
                page = ROOT / record["path"]
                self.assertTrue(page.is_file(), page)
                header, body = page.read_text(encoding="utf-8").split("\n", 1)
                meta = json.loads(header[5:-4])
                self.assertEqual(meta["pdf_page"], number)
                self.assertEqual(meta["source_sha256"], source["sha256"])
                self.assertEqual(meta["content_sha256"], hashlib.sha256(body.strip().encode()).hexdigest())

    def test_visual_risk_is_not_marked_verified(self):
        manifest = json.loads((ROOT / "knowledge/manifest.json").read_text(encoding="utf-8"))
        flagged = [p for p in manifest["sources"]["slide"]["pages"] if "MATH_REVIEW_REQUIRED" in p["flags"] or "IMAGE_PRESENT" in p["flags"]]
        self.assertTrue(flagged)
        self.assertTrue(all(p["status"] != "VERIFIED" for p in flagged))

    def test_ambiguous_math_and_diagrams_keep_pdf_evidence(self):
        math_meta, math_body = parse_page(page_path("outline", 12))
        self.assertIn("mod 1", math_body)
        self.assertIn("MATH_REVIEW_REQUIRED", math_meta["flags"])
        diagram_meta, diagram_body = parse_page(page_path("outline", 2))
        self.assertTrue(diagram_meta["needs_visual_review"])
        self.assertIn("outline-p0002-i1.png", diagram_body)
        slide_meta, slide_body = parse_page(page_path("slide", 178))
        self.assertIn("MATH_REVIEW_REQUIRED", slide_meta["flags"])
        self.assertIn("slide-p0178.png", slide_body)
