import sys
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from study import search_db


class Retrieval(unittest.TestCase):
    def test_exact_question_id(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root / "tools/study.py"), "question", "TN1-Q001"], cwd=root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"question_id": "TN1-Q001"', result.stdout)
        self.assertIn("hiểm họa", result.stdout)

    def test_vietnamese_accent_variant(self):
        accented = search_db("hiểm họa an toàn thông tin", 10, "slide")
        plain = search_db("hiem hoa an toan thong tin", 10, "slide")
        self.assertTrue(accented)
        self.assertEqual([x["id"] for x in accented], [x["id"] for x in plain])

    def test_controlled_english_alias(self):
        self.assertIn(180, [x["pdf_page"] for x in search_db("public key", 5, "slide")])

    def test_negative_query_returns_no_evidence(self):
        self.assertEqual(search_db("zyxwvu987654321notpresent", 5, "slide"), [])
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root / "tools/study.py"), "context", "zyxwvu987654321notpresent"], cwd=root, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Chưa tìm được căn cứ đủ tin cậy", result.stdout)
