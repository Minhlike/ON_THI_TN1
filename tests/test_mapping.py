import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from study import read_jsonl, page_path, parse_page


class Mapping(unittest.TestCase):
    def test_ids_unique_and_every_excerpt_exists_on_claimed_page(self):
        qs = read_jsonl(ROOT / "knowledge/questions/questions.jsonl")
        ids = [q["question_id"] for q in qs]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreater(len(ids), 50)
        manifest = json.loads((ROOT / "knowledge/manifest.json").read_text(encoding="utf-8"))
        for row in read_jsonl(ROOT / "knowledge/questions/question_slide_map.jsonl"):
            self.assertIn(row["question_id"], ids)
            _, body = parse_page(page_path("slide", row["slide_page"]))
            self.assertIn(row["relevant_excerpt"], body)
            if row["mapping_status"] == "VERIFIED_MAPPING":
                self.assertEqual(row["review_source_sha256"], manifest["sources"]["slide"]["sha256"])
                self.assertIn("đối chiếu trực quan", row["note"])

    def test_multi_page_question_retains_its_continuation(self):
        qs = read_jsonl(ROOT / "knowledge/questions/questions.jsonl")
        spanning = [q for q in qs if q["end_pdf_page"] > q["pdf_page"]]
        self.assertTrue(spanning)
        self.assertTrue(any("<?php" in q["original_text"] or "Anh/chị" in q["original_text"] for q in spanning))
