"""Offline, provenance-first retrieval for Tốt nghiệp 1.

Generated text is a cache of the immutable PDFs, not an edited answer key.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOW = ROOT / "knowledge"
MANIFEST = KNOW / "manifest.json"
DB = KNOW / "index" / "study.sqlite3"
QUESTIONS = KNOW / "questions" / "questions.jsonl"
MAP = KNOW / "questions" / "question_slide_map.jsonl"
REVIEWS = KNOW / "questions" / "reviewed_mappings.jsonl"
EXTRACTOR = "pymupdf4llm-1.28.2"
GENERATOR_VERSION = 1  # bump when question parsing or index structure changes
STOP = set("anh chi hay trinh bay cho biet cua trong va la gi ve mot cac co duoc voi the nao theo tu sau bai cau khai niem lay so vi du cu the doi tuong nhu nhung neu lien quan"
           .split())
ALIASES = {
    "public key": "khóa công khai",
    "firewall": "tường lửa",
    "malware": "mã độc",
    "mang rieng ao": "VPN",
    "bo dem tran": "tràn bộ đệm",
}


def fold(s: str) -> str:
    s = s.replace("Đ", "D").replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", s.casefold()) if unicodedata.category(c) != "Mn")


def tokens(s: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9]+", fold(s)) if len(x) > 2 and x not in STOP]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(p: Path, rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def sources() -> dict[str, Path]:
    import pymupdf
    pdfs = list(ROOT.glob("*.pdf"))
    slides = [p for p in pdfs if p.name == "CSATTT_SLIDE_FULL.pdf"]
    outlines = [p for p in pdfs if "HPTTN1" in fold(p.name).upper()]
    laws = [p for p in pdfs if "09-2020" in p.name]
    if len(slides) != 1 or len(outlines) != 1 or len(laws) != 1:
        raise RuntimeError("Expected one slide, outline and 09/2020 PDF; inspect actual filenames")
    return {"slide": slides[0], "outline": outlines[0], "law": laws[0]}


def page_path(source_id: str, number: int) -> Path:
    return KNOW / source_id / "pages" / f"p{number:04d}.md"


def parse_page(p: Path) -> tuple[dict, str]:
    raw = p.read_text(encoding="utf-8")
    first, body = raw.split("\n", 1)
    return json.loads(first.removeprefix("<!-- ").removesuffix(" -->")), body.strip()


def extract_source(source_id: str, p: Path, previous: dict | None) -> dict:
    import pymupdf
    import pymupdf4llm
    digest = sha(p)
    doc = pymupdf.open(p)
    old_pages = (previous or {}).get("pages", [])
    if previous and previous.get("sha256") == digest and previous.get("extractor") == EXTRACTOR and len(old_pages) == len(doc) and all(page_path(source_id, i).exists() for i in range(1, len(doc) + 1)):
        print(f"{source_id}: unchanged; reused {len(doc)} pages", file=sys.stderr)
        return previous
    pages = []
    for i, page in enumerate(doc):
        raw = page.get_text()
        # Layout extraction is deterministic; no OCR or generated image description.
        try:
            body = pymupdf4llm.to_markdown(doc, pages=[i], show_progress=False).strip()
            method = "pymupdf4llm"
        except Exception as exc:
            body = raw.strip()
            method = "pymupdf_fallback"
        images = len(page.get_images())
        low_text = len(raw.strip()) < 50
        math = bool(re.search(r"(?:\bmod\b|[=≡∑∏√∫αβφλ]|\^[0-9]|[xy][23]\s*=)", raw, re.I))
        bad_unicode = "\ufffd" in raw or "\ufffd" in body
        flags = [name for name, yes in (("LOW_TEXT", low_text), ("IMAGE_PRESENT", images > 0), ("MATH_REVIEW_REQUIRED", math), ("UNICODE_REPLACEMENT", bad_unicode), ("EXTRACTOR_FALLBACK", method != "pymupdf4llm")) if yes]
        status = "EXTRACTION_FAILED" if not body and not low_text else "VISUAL_REVIEW_REQUIRED" if flags else "EXTRACTED_UNREVIEWED"
        # A blank page is still recorded and requires checking.
        if not body:
            flags.append("EMPTY_EXTRACTION")
            status = "VISUAL_REVIEW_REQUIRED"
        displayed = None
        trailing = re.findall(r"(?m)^\s*(\d{1,4})\s*$", raw)
        if trailing and int(trailing[-1]) == i + 1:
            displayed = i + 1
        meta = {
            "source_id": source_id, "source_file": p.name, "source_sha256": digest,
            "pdf_page": i + 1, "displayed_slide_number": displayed if source_id == "slide" else None,
            "chapter": None, "section": None, "extraction_method": method,
            "extraction_status": status, "needs_visual_review": status == "VISUAL_REVIEW_REQUIRED",
            "content_sha256": hashlib.sha256(body.encode()).hexdigest(), "flags": flags,
            "image_count": images, "text_chars": len(raw),
        }
        out = page_path(source_id, i + 1)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("<!-- " + json.dumps(meta, ensure_ascii=False) + " -->\n\n" + body + "\n", encoding="utf-8")
        pages.append({"pdf_page": i + 1, "path": out.relative_to(ROOT).as_posix(), "status": status, "flags": flags, "content_sha256": meta["content_sha256"]})
        if (i + 1) % 50 == 0:
            print(f"{source_id}: {i + 1}/{len(doc)}", file=sys.stderr)
    return {"file": p.name, "sha256": digest, "page_count": len(doc), "extractor": EXTRACTOR, "pages": pages}


def extract_outline_diagrams(manifest: dict) -> None:
    """Preserve embedded diagrams in the outline without inventing captions."""
    import pymupdf
    source = manifest["sources"]["outline"]
    asset_root = KNOW / "assets"
    asset_root.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(ROOT / source["file"]) as doc:
        for page_number, page in enumerate(doc, 1):
            refs = []
            for image_number, info in enumerate(page.get_images(full=True), 1):
                data = doc.extract_image(info[0])
                filename = f"outline-p{page_number:04d}-i{image_number}.{data['ext']}"
                asset = asset_root / filename
                if not asset.exists() or asset.read_bytes() != data["image"]:
                    asset.write_bytes(data["image"])
                refs.append(f"[Ảnh gốc {image_number} của trang PDF {page_number}](../../assets/{filename})")
            if not refs:
                continue
            pp = page_path("outline", page_number)
            meta, body = parse_page(pp)
            body = re.sub(r"\n*## Ảnh gốc từ PDF\n[\s\S]*$", "", body).strip()
            body += "\n\n## Ảnh gốc từ PDF\n" + "\n".join("- " + x for x in refs)
            meta["content_sha256"] = hashlib.sha256(body.encode()).hexdigest()
            meta["needs_visual_review"] = True
            meta["extraction_status"] = "VISUAL_REVIEW_REQUIRED"
            if "IMAGE_PRESENT" not in meta["flags"]:
                meta["flags"].append("IMAGE_PRESENT")
            rendered = "<!-- " + json.dumps(meta, ensure_ascii=False) + " -->\n\n" + body + "\n"
            if pp.read_text(encoding="utf-8") != rendered:
                pp.write_text(rendered, encoding="utf-8")
            record = source["pages"][page_number - 1]
            record["content_sha256"] = meta["content_sha256"]
            record["status"] = meta["extraction_status"]
            record["flags"] = meta["flags"]

    # This page's formula and arrows are not faithfully represented by text extraction.
    slide_number = 178
    slide_source = manifest["sources"]["slide"]
    with pymupdf.open(ROOT / slide_source["file"]) as slides:
        if len(slides) >= slide_number:
            asset = asset_root / "slide-p0178.png"
            png = slides[slide_number - 1].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).tobytes("png")
            if not asset.exists() or asset.read_bytes() != png:
                asset.write_bytes(png)
            pp = page_path("slide", slide_number)
            meta, body = parse_page(pp)
            body = re.sub(r"\n*## Ảnh gốc từ PDF\n[\s\S]*$", "", body).strip()
            body += "\n\n## Ảnh gốc từ PDF\n- [Trang PDF 178, sơ đồ và công thức](../../assets/slide-p0178.png)"
            meta["content_sha256"] = hashlib.sha256(body.encode()).hexdigest()
            meta["needs_visual_review"] = True
            meta["extraction_status"] = "VISUAL_REVIEW_REQUIRED"
            if "MATH_REVIEW_REQUIRED" not in meta["flags"]:
                meta["flags"].append("MATH_REVIEW_REQUIRED")
            rendered = "<!-- " + json.dumps(meta, ensure_ascii=False) + " -->\n\n" + body + "\n"
            if pp.read_text(encoding="utf-8") != rendered:
                pp.write_text(rendered, encoding="utf-8")
            record = slide_source["pages"][slide_number - 1]
            record["content_sha256"] = meta["content_sha256"]
            record["status"] = meta["extraction_status"]
            record["flags"] = meta["flags"]


def annotate_slide_sections(manifest: dict) -> None:
    """Carry explicit lesson titles forward; never infer a missing lesson number."""
    import pymupdf
    source = manifest["sources"]["slide"]
    chapter = None
    with pymupdf.open(ROOT / source["file"]) as doc:
        for page_number, page in enumerate(doc, 1):
            raw = page.get_text().strip()
            cover = re.search(r"(?m)^Bài\s+\d{1,2}\.[^\n]*", raw)
            if cover:
                chapter = cover.group(0).strip()
            pp = page_path("slide", page_number)
            meta, body = parse_page(pp)
            title = next((re.sub(r"[*_#<>/]+", "", line).strip() for line in body.splitlines() if line.lstrip().startswith("#")), None)
            meta["chapter"] = chapter
            meta["section"] = title if title and not title.startswith("Bài ") else None
            if len(re.findall(rf"(?m)^\s*{page_number}\s*$", raw)) > 1 and "DUPLICATE_PAGE_NUMBER" not in meta["flags"]:
                meta["flags"].append("DUPLICATE_PAGE_NUMBER")
            rendered = "<!-- " + json.dumps(meta, ensure_ascii=False) + " -->\n\n" + body + "\n"
            if pp.read_text(encoding="utf-8") != rendered:
                pp.write_text(rendered, encoding="utf-8")
            source["pages"][page_number - 1]["flags"] = meta["flags"]


def normalize_generated_markdown(manifest: dict) -> None:
    """Remove extractor trailing spaces without changing words or line order."""
    for source_id in ("slide", "outline"):
        source = manifest["sources"][source_id]
        for number in range(1, source["page_count"] + 1):
            pp = page_path(source_id, number)
            meta, body = parse_page(pp)
            body = "\n".join(line.rstrip(" ") for line in body.splitlines()).strip()
            meta["content_sha256"] = hashlib.sha256(body.encode()).hexdigest()
            rendered = "<!-- " + json.dumps(meta, ensure_ascii=False) + " -->\n\n" + body + "\n"
            if pp.read_text(encoding="utf-8") != rendered:
                pp.write_text(rendered, encoding="utf-8")
            source["pages"][number - 1]["content_sha256"] = meta["content_sha256"]


QSTART = re.compile(r"^\s*(?:(Câu|Bài)\s*(\d+)\s*\.?|([1-9]\d?)\.)\s+", re.I)
SECTION = re.compile(r"^(?:ĐỊNH DANH|ÔN TẬP|Ôn tập|MẬT MÃ|BÀI TẬP TUẦN|Dạng\s+\d|ĐỀ SỐ|Chương\s+\d|MÔN THI:)")
SUB = re.compile(r"(?m)^\s*([a-d])\)\s+(.+?)(?=\n\s*[a-d]\)\s+|\Z)", re.S)


def bullet_subquestions(body: str) -> list[str]:
    groups: list[list[str]] = []
    current: list[str] | None = None
    for line in body.splitlines()[1:]:
        stripped = line.strip()
        if stripped == "-" or stripped.startswith("- "):
            if current:
                groups.append(current)
            current = [line.rstrip()]
        elif current is not None:
            current.append(line.rstrip())
    if current:
        groups.append(current)
    return ["\n".join(group).strip() for group in groups] if len(groups) >= 2 else []


def make_questions(manifest: dict) -> list[dict]:
    records = []
    current = None
    section = "ĐỊNH DANH VÀ XÁC THỰC"
    seq = 0
    in_exam_header = False
    for n in range(1, manifest["sources"]["outline"]["page_count"] + 1):
        _, body = parse_page(page_path("outline", n))
        # Use the PDF text layer for question boundaries. Markdown is retained separately.
        import pymupdf
        with pymupdf.open(ROOT / manifest["sources"]["outline"]["file"]) as doc:
            text = doc[n - 1].get_text()
        for line in text.splitlines():
            s = line.strip()
            if not s:
                if current:
                    current["original_text"] += "\n"
                continue
            if s.startswith("BAN CƠ YẾU CHÍNH PHỦ"):
                if current:
                    current["original_text"] = current["original_text"].strip()
                    records.append(current)
                    current = None
                in_exam_header = True
                continue
            if in_exam_header:
                if s.startswith("ĐỀ SỐ"):
                    section = "ĐỀ THI MẪU " + s
                    in_exam_header = False
                continue
            if SECTION.match(s):
                section = s
                continue
            match = QSTART.match(s)
            if match and (match.group(1) or n >= 17):
                if current:
                    current["original_text"] = current["original_text"].strip()
                    records.append(current)
                seq += 1
                current = {
                    "question_id": f"TN1-Q{seq:03d}", "section_id": section,
                    "question_type": "UNCLASSIFIED", "original_text": s, "pdf_page": n,
                    "end_pdf_page": n, "subquestion": None, "given_parameters": [],
                    "expected_task": None, "topics": [], "slide_references": [],
                    "mapping_status": "UNMAPPED", "validation_notes": ["Text extracted from PDF; diagram/formula may require visual check"],
                }
            elif current:
                current["original_text"] += "\n" + line.rstrip()
                current["end_pdf_page"] = n
    if current:
        current["original_text"] = current["original_text"].strip()
        records.append(current)
    expanded = []
    for q in records:
        body = q["original_text"]
        f = fold(body)
        if re.search(r"\b(?:p|q|e|n|k|m|c)\s*=|tinh|giai ma|ma hoa", f) and any(x in f for x in ("rsa", "elgamal", "diffie", "duong cong", "ecc")):
            q["question_type"] = "CALCULATION"
        elif any(x in body for x in ("#include", "<?php", "đoạn mã")):
            q["question_type"] = "CODE_ANALYSIS"
        elif "giao thuc" in f or "so do" in f:
            q["question_type"] = "PROTOCOL_ANALYSIS"
        elif "luat iptables" in f or "luat cho ids" in f or "phan tich luat" in f:
            q["question_type"] = "RULE_ANALYSIS"
        elif "so sanh" in f or "khac biet" in f or "uu nhuoc" in f:
            q["question_type"] = "COMPARISON"
        elif "tan cong" in f or "khai thac" in f:
            q["question_type"] = "ATTACK_ANALYSIS"
        elif "mo hinh mang" in f or "nha quan tri" in f:
            q["question_type"] = "SCENARIO"
        else:
            q["question_type"] = "EXPLANATION"
        q["topics"] = list(dict.fromkeys(x for x in ("RSA", "Elgamal", "ECC", "Diffie-Hellman", "XSS", "SQL Injection", "VPN", "SIEM", "IDS", "IPS", "tường lửa", "mật khẩu", "mã độc") if fold(x) in f))
        if q["question_type"] == "CALCULATION":
            q["given_parameters"] = re.findall(r"\b[A-Za-z][A-Za-z0-9]*\s*=\s*(?:\([^)]+\)|-?\d+(?:,\d+)?)", body)
        task = re.search(r"\b(?:Trình bày|Hãy xác định|Xác định|Tính|Giải mã|Mô tả|Phân tích|Nêu|Hãy tìm|Tìm)\b", body, re.I)
        q["expected_task"] = task.group(0) if task else None
        if "sơ đồ" in f or "mod 1" in f or "" in body:
            q["validation_notes"].append("VISUAL_REVIEW_REQUIRED: diagram or ambiguous math text")
        expanded.append(q)
        labeled = list(SUB.finditer(body))
        parts = [(m.group(1), m.group(0).strip()) for m in labeled]
        if not parts and q["question_type"] == "CALCULATION":
            parts = [(chr(ord("a") + i), value) for i, value in enumerate(bullet_subquestions(body)) if i < 26]
        for label, original in parts:
            child = dict(q)
            child["question_id"] = q["question_id"] + "-" + label
            child["original_text"] = original
            child["subquestion"] = label
            child["parent_question_id"] = q["question_id"]
            child["validation_notes"] = q["validation_notes"][:]
            expanded.append(child)
    write_jsonl(QUESTIONS, expanded)
    lines = ["# Chỉ mục câu hỏi đề cương", "", "Các ID là định danh theo thứ tự xuất hiện; mục con dùng hậu tố a–d. Đọc `questions.jsonl` để xem nguyên văn và trang PDF.", ""]
    for q in expanded:
        if q["subquestion"] is None:
            summary = re.sub(r"\s+", " ", q["original_text"])[:130].rstrip()
            lines.append(f"- [{q['question_id']}](questions.jsonl): trang PDF {q['pdf_page']}, {q['section_id']} — {summary}")
    (QUESTIONS.parent / "QUESTION_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return expanded


def build_index(manifest: dict, questions: list[dict]) -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    db = sqlite3.connect(DB)
    db.executescript("CREATE TABLE chunks (id TEXT PRIMARY KEY, source_id TEXT, pdf_page INT, status TEXT, text TEXT, normalized TEXT); CREATE VIRTUAL TABLE chunks_fts USING fts5(id UNINDEXED, normalized); CREATE INDEX chunks_source ON chunks(source_id,pdf_page);")
    for source_id in ("slide", "outline"):
        for n in range(1, manifest["sources"][source_id]["page_count"] + 1):
            meta, body = parse_page(page_path(source_id, n))
            chunk_id = f"{source_id}:p{n:04d}"
            db.execute("INSERT INTO chunks VALUES (?,?,?,?,?,?)", (chunk_id, source_id, n, meta["extraction_status"], body, fold(body)))
            db.execute("INSERT INTO chunks_fts VALUES (?,?)", (chunk_id, fold(body)))
    db.commit()
    db.close()


def search_db(query: str, limit: int = 5, source_id: str | None = None) -> list[dict]:
    if not DB.exists():
        raise RuntimeError("Index missing. Run build first.")
    expanded = query + " " + ALIASES.get(fold(query).strip(), "")
    terms = list(dict.fromkeys(tokens(expanded)))[:12]
    if not terms:
        return []
    expression = " OR ".join('"' + x + '"' for x in terms)
    db = sqlite3.connect(DB)
    sql = "SELECT c.id,c.source_id,c.pdf_page,c.status,c.text,bm25(chunks_fts) AS score FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.id WHERE chunks_fts MATCH ?"
    args: list = [expression]
    if source_id:
        sql += " AND c.source_id=?"
        args.append(source_id)
    sql += " ORDER BY score LIMIT ?"
    args.append(max(limit * 20, 80))
    rows = db.execute(sql, args).fetchall()
    db.close()
    hits = [dict(zip(("id", "source_id", "pdf_page", "status", "text", "score"), row)) for row in rows]
    query_terms = set(terms)
    definition = "khai niem" in fold(query) or "la gi" in fold(query)
    for hit in hits:
        body = hit["text"]
        body_terms = set(tokens(body))
        coverage = len(query_terms & body_terms) / len(query_terms)
        compact = " ".join(re.findall(r"[a-z0-9]+", fold(body)))
        phrase = any(" ".join(terms[i:i+2]) in compact for i in range(len(terms)-1))
        head = next((line for line in body.splitlines() if line.lstrip().startswith("#")), "")
        head_compact = " ".join(re.findall(r"[a-z0-9]+", fold(head)))
        topic_phrase = " ".join(terms[:2])
        title_bonus = bool(topic_phrase and head_compact.startswith(topic_phrase))
        body_after_heading = " ".join(re.findall(r"[a-z0-9]+", fold(body.partition("\n")[2])))
        definition_bonus = definition and bool(topic_phrase and re.search(re.escape(topic_phrase) + r".{0,100}\bla\b", body_after_heading))
        substantive = min(len(body), 500) / 500
        # Original BM25 remains a tie-breaker; term coverage and a direct
        # definition matter more than a tiny index page repeating a title.
        hit["rank"] = coverage * 10 + (2 if phrase else 0) + (2 if title_bonus else 0) + (3 if definition_bonus else 0) + substantive + min(-hit["score"] / 20, 1)
    hits.sort(key=lambda h: (-h["rank"], h["pdf_page"]))
    return hits[:limit]


def excerpt(text: str, query: str, max_chars: int = 500) -> str:
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    words = set(tokens(query))
    wants_definition = "khai niem" in fold(query) or "la gi" in fold(query)
    ranked = sorted(lines, key=lambda line: sum(w in tokens(line) for w in words) + (2 if len(line) > 60 else 0) + (3 if wants_definition and re.search(r"\bla\b", fold(line)) else 0), reverse=True)
    return (ranked[0] if ranked else "")[:max_chars]


def make_mapping(questions: list[dict]) -> list[dict]:
    rows = []
    for q in questions:
        if q["subquestion"]:
            parent = next(x for x in questions if x["question_id"] == q["parent_question_id"])
            query = parent["original_text"].splitlines()[0] + " " + q["original_text"]
        else:
            query = q["original_text"].splitlines()[0]
        hits = search_db(query, 3, "slide")
        refs = []
        for hit in hits:
            ex = excerpt(hit["text"], query)
            if not ex or len(set(tokens(ex)) & set(tokens(query))) < 2:
                continue
            rows.append({"question_id": q["question_id"], "slide_page": hit["pdf_page"], "relevant_excerpt": ex, "mapping_status": "UNVERIFIED_CANDIDATE", "note": "Lexical candidate; subject-matter relevance and page text need review"})
            refs.append(hit["pdf_page"])
        q["slide_references"] = refs
        q["mapping_status"] = "UNVERIFIED_CANDIDATE" if refs else "UNMAPPED"
    if REVIEWS.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        current_sha = manifest["sources"]["slide"]["sha256"]
        for review in read_jsonl(REVIEWS):
            if review["source_sha256"] != current_sha:
                continue
            pp = page_path("slide", review["slide_page"])
            _, body = parse_page(pp)
            if review["relevant_excerpt"] not in body:
                continue
            target = next((r for r in rows if r["question_id"] == review["question_id"] and r["slide_page"] == review["slide_page"]), None)
            if target is None:
                target = {"question_id": review["question_id"], "slide_page": review["slide_page"]}
                rows.append(target)
            target.update({"relevant_excerpt": review["relevant_excerpt"], "mapping_status": review["mapping_status"], "note": review["note"], "review_source_sha256": current_sha})
            q = next(x for x in questions if x["question_id"] == review["question_id"])
            if review["slide_page"] not in q["slide_references"]:
                q["slide_references"].append(review["slide_page"])
            q["mapping_status"] = review["question_mapping_status"]
    write_jsonl(MAP, rows)
    write_jsonl(QUESTIONS, questions)
    return rows


def audit_data(manifest: dict, deep: bool = True) -> dict:
    errors = []
    for source_id, entry in manifest["sources"].items():
        p = ROOT / entry["file"]
        if not p.exists() or sha(p) != entry["sha256"]:
            errors.append(f"{source_id}: source SHA mismatch or missing")
        if source_id == "law":
            continue
        if len(entry["pages"]) != entry["page_count"]:
            errors.append(f"{source_id}: page count mismatch")
        for n in range(1, entry["page_count"] + 1):
            pp = page_path(source_id, n)
            if not pp.exists():
                errors.append(f"{source_id}:{n} missing")
                continue
            if deep:
                meta, body = parse_page(pp)
                if meta["pdf_page"] != n or meta["source_sha256"] != entry["sha256"] or hashlib.sha256(body.encode()).hexdigest() != meta["content_sha256"]:
                    errors.append(f"{source_id}:{n} metadata or content mismatch")
    if QUESTIONS.exists():
        questions = read_jsonl(QUESTIONS)
        ids = [q["question_id"] for q in questions]
        if len(ids) != len(set(ids)):
            errors.append("duplicate question IDs")
        for row in read_jsonl(MAP) if MAP.exists() else []:
            if row["question_id"] not in ids or row["slide_page"] < 1 or row["slide_page"] > manifest["sources"]["slide"]["page_count"]:
                errors.append("invalid mapping reference")
                break
            _, body = parse_page(page_path("slide", row["slide_page"]))
            if row["relevant_excerpt"] not in body:
                errors.append(f"mapping excerpt missing: {row['question_id']}")
    return {"ok": not errors, "errors": errors}


def write_extraction_report(manifest: dict) -> None:
    lines = ["# Kiểm kê và chất lượng trích xuất", "", "Dữ liệu được trích máy, **không tự động được coi là đã đối chiếu**. Số trang dưới đây là trang PDF vật lý.", ""]
    for source_id in ("slide", "outline", "law"):
        e = manifest["sources"][source_id]
        lines.extend([f"## {source_id}: {e['file']}", "", f"- SHA-256: `{e['sha256']}`", f"- Số trang PDF: {e['page_count']}"])
        if source_id == "law":
            lines.append("- Chỉ kiểm kê; PDF dạng ảnh, không trích xuất trong đợt này.\n")
            continue
        pages = e["pages"]
        for status in ("VERIFIED", "EXTRACTED_UNREVIEWED", "VISUAL_REVIEW_REQUIRED", "EXTRACTION_FAILED"):
            lines.append(f"- {status}: {sum(x['status'] == status for x in pages)}")
        for flag in ("LOW_TEXT", "IMAGE_PRESENT", "MATH_REVIEW_REQUIRED", "UNICODE_REPLACEMENT", "EMPTY_EXTRACTION", "EXTRACTOR_FALLBACK", "DUPLICATE_PAGE_NUMBER"):
            selected = [x["pdf_page"] for x in pages if flag in x["flags"]]
            if selected:
                lines.append(f"- {flag}: {len(selected)} trang; " + ", ".join(str(n) for n in selected[:100]) + (" …" if len(selected) > 100 else ""))
        lines.append("")
    lines.extend(["## Đối chiếu trực quan đã thực hiện", "", "- Đề cương trang PDF 2: sơ đồ xác thực mật khẩu không hiện đủ trong text layer; ảnh gốc được giữ trong `knowledge/assets/`.", "- Đề cương trang PDF 12: bản PDF gốc thực sự ghi `mod 1` ở bài ECC thứ hai. Đây là dữ kiện nghi vấn của **nguồn gốc**, chưa được tự sửa. Ký hiệu lũy thừa/chỉ số cũng bị phẳng hóa khi trích text.", "- Slide trang PDF 178: công thức và mũi tên trong sơ đồ khóa công khai mất trật tự ở text layer; có ảnh gốc chọn lọc để kiểm chứng.", "", "## Việc cần kiểm chứng", "", "- Các trang gắn `VISUAL_REVIEW_REQUIRED` cần đọc PDF/hình gốc khi dùng làm chứng cứ. Chưa có kiểm tra thủ công toàn bộ slide.", "- Phát hiện ảnh chỉ dựa trên ảnh nhúng; sơ đồ vector, bảng và công thức có thể cần đối chiếu dù không có cờ ảnh. Chưa OCR toàn bộ tài liệu.", "- `EXTRACTED_UNREVIEWED` chỉ nghĩa là có văn bản trích xuất; không xác nhận đúng công thức, thứ tự bảng hay ngữ nghĩa.", ""])
    report = ROOT / "reports/EXTRACTION_AUDIT.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")


def cmd_build(_args) -> None:
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    previous_sources_snapshot = copy.deepcopy(previous.get("sources", {}))
    src = sources()
    new = {"schema_version": 1, "generator_version": GENERATOR_VERSION,
           "review_sha256": sha(REVIEWS) if REVIEWS.exists() else None, "sources": {}}
    import pymupdf
    for source_id in ("slide", "outline"):
        new["sources"][source_id] = extract_source(source_id, src[source_id], previous.get("sources", {}).get(source_id))
    normalize_generated_markdown(new)
    annotate_slide_sections(new)
    extract_outline_diagrams(new)
    law = src["law"]
    new["sources"]["law"] = {"file": law.name, "sha256": sha(law), "page_count": len(pymupdf.open(law)), "processing": "not extracted; supplementary source only"}
    old_sources = previous_sources_snapshot
    slide_changed = old_sources.get("slide") != new["sources"]["slide"]
    outline_changed = old_sources.get("outline") != new["sources"]["outline"]
    generator_changed = previous.get("generator_version") != GENERATOR_VERSION
    review_changed = previous.get("review_sha256") != new["review_sha256"]
    write_json(MANIFEST, new)
    if outline_changed or generator_changed or not QUESTIONS.exists():
        qs = make_questions(new)
    else:
        qs = read_jsonl(QUESTIONS)
    if slide_changed or outline_changed or generator_changed or not DB.exists():
        build_index(new, qs)
    if slide_changed or outline_changed or generator_changed or review_changed or not MAP.exists():
        mappings = make_mapping(qs)
        print(f"questions={len(qs)} mapping_candidates={len(mappings)}")
    write_extraction_report(new)
    print(json.dumps(audit_data(new, False), ensure_ascii=False))


def ensure_fresh() -> dict:
    if not MANIFEST.exists():
        raise RuntimeError("Manifest missing. Run build first.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for source_id, entry in manifest["sources"].items():
        if sha(ROOT / entry["file"]) != entry["sha256"]:
            raise RuntimeError(f"Source changed: {source_id}; run build")
    return manifest


def display_hit(hit: dict, max_chars: int = 600) -> None:
    print(f"[{hit['id']}] PDF p.{hit['pdf_page']} | {hit['status']} | rank={hit['rank']:.3f}")
    print(hit["text"][:max_chars].strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=5); s.add_argument("--source", choices=["slide", "outline"])
    q = sub.add_parser("question"); q.add_argument("id")
    p = sub.add_parser("page"); p.add_argument("source", choices=["slide", "outline"]); p.add_argument("number", type=int)
    c = sub.add_parser("context"); c.add_argument("query"); c.add_argument("--limit", type=int, default=5); c.add_argument("--max-chars", type=int, default=4000)
    sub.add_parser("audit"); sub.add_parser("status"); sub.add_parser("eval")
    args = parser.parse_args()
    if args.cmd == "build":
        cmd_build(args); return
    manifest = ensure_fresh()
    if args.cmd == "audit":
        print(json.dumps(audit_data(manifest), ensure_ascii=False, indent=2)); return
    if args.cmd == "status":
        qs = read_jsonl(QUESTIONS)
        print(json.dumps({"branch_data": "local", "sources": {k: {"file": v["file"], "pages": v["page_count"], "sha256": v["sha256"]} for k, v in manifest["sources"].items()}, "questions": {"parent": sum(q["subquestion"] is None for q in qs), "subquestion": sum(q["subquestion"] is not None for q in qs)}, "mapping_status": {x: sum(q["mapping_status"] == x for q in qs) for x in sorted(set(q["mapping_status"] for q in qs))}, "index_exists": DB.exists()}, ensure_ascii=False, indent=2)); return
    if args.cmd == "page":
        p = page_path(args.source, args.number)
        if not p.exists(): parser.error("Page not found")
        print(p.read_text(encoding="utf-8")); return
    if args.cmd == "question":
        all_questions = read_jsonl(QUESTIONS)
        rows = [q for q in all_questions if q["question_id"].casefold() == args.id.casefold()]
        if not rows: parser.error("Question ID not found")
        if rows[0].get("parent_question_id"):
            parent = next(q for q in all_questions if q["question_id"] == rows[0]["parent_question_id"])
            print("PARENT QUESTION:\n" + parent["original_text"] + "\n")
        print(json.dumps(rows[0], ensure_ascii=False, indent=2))
        for row in read_jsonl(MAP):
            if row["question_id"] == rows[0]["question_id"]:
                print(json.dumps(row, ensure_ascii=False))
        return
    if args.cmd == "search":
        hits = search_db(args.query, min(max(args.limit, 1), 20), args.source)
        if not hits: print("Chưa tìm được căn cứ đủ tin cậy trong tài liệu hiện có.")
        for hit in hits: display_hit(hit)
        return
    if args.cmd == "context":
        all_questions = read_jsonl(QUESTIONS)
        qs = [q for q in all_questions if q["question_id"].casefold() == args.query.casefold()]
        query = qs[0]["original_text"] if qs else args.query
        if qs and qs[0].get("parent_question_id"):
            query = next(q["original_text"] for q in all_questions if q["question_id"] == qs[0]["parent_question_id"])
        if qs:
            print(f"QUESTION {qs[0]['question_id']} [outline PDF p.{qs[0]['pdf_page']}; {qs[0]['mapping_status']}]\n{query}\n")
        hits = search_db(query, min(max(args.limit, 1), 10), "slide")
        mapped = {r["slide_page"]: r for r in read_jsonl(MAP) if qs and r["question_id"] == qs[0]["question_id"]}
        verified_pages = [n for n, r in mapped.items() if r["mapping_status"] == "VERIFIED_MAPPING"]
        for number in verified_pages:
            if not any(h["pdf_page"] == number for h in hits):
                meta, body = parse_page(page_path("slide", number))
                hits.append({"id": f"slide:p{number:04d}", "source_id": "slide", "pdf_page": number, "status": meta["extraction_status"], "text": body, "score": 0})
        hits.sort(key=lambda h: (0 if h["pdf_page"] in verified_pages else 1, -h.get("rank", 0)))
        hits = hits[: min(max(args.limit, 1), 10)]
        if not hits:
            print("Chưa tìm được căn cứ đủ tin cậy trong tài liệu hiện có."); return
        budget = max(args.max_chars, 1000)
        used = 0
        for hit in hits:
            mapping = mapped.get(hit["pdf_page"])
            mapping_status = mapping["mapping_status"] if mapping else "UNVERIFIED_CANDIDATE"
            ex = mapping["relevant_excerpt"] if mapping and mapping_status == "VERIFIED_MAPPING" else excerpt(hit["text"], query, 1000)
            note = f"\nPhạm vi: {mapping['note']}" if mapping and mapping_status == "VERIFIED_MAPPING" else ""
            text = f"[{hit['id']}; CSATTT_SLIDE_FULL.pdf, trang PDF {hit['pdf_page']}; extraction={hit['status']}; mapping={mapping_status}]\n{ex}{note}\n"
            if used + len(text) > budget:
                break
            print(text); used += len(text)
        print(f"CONTEXT_CHARS={used}; verify candidate relevance and visually review flagged pages before asserting an answer")
        return
    if args.cmd == "eval":
        from eval_retrieval import run_eval
        run_eval()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
