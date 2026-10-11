"""Small, transparent retrieval benchmark against inspected source pages."""
from __future__ import annotations

import statistics
import subprocess
import sys
import time
from pathlib import Path

from study import ROOT, KNOW, fold, parse_page, page_path, search_db, read_jsonl, audit_data, unknown_slide_terms
import json

# Each cited reference page was inspected against the source PDF text layer.
# These are positive examples, not exhaustive relevance judgments.
CASES = [
    ("hiểm họa an toàn thông tin", {51}),
    ("hiem hoa an toan thong tin", {51}),
    ("tính chất mật mã khóa công khai", {180}),
    ("SQL Injection", {292}),
    ("tràn bộ đệm", {302}),
    ("hệ thống phát hiện xâm nhập IDS", {374}),
    ("mã hóa kênh truyền VPN", {218}),
    ("Diffie-Hellman", {178}),
]
NEGATIVE = "Định lý Poincaré được chứng minh như thế nào?"


def baseline(query: str, page_count: int) -> list[int]:
    needle = fold(query)
    matches = []
    for n in range(1, page_count + 1):
        _, body = parse_page(page_path("slide", n))
        if needle in fold(body):
            matches.append(n)
    return matches[:5]


def run_eval() -> None:
    manifest = json.loads((KNOW / "manifest.json").read_text(encoding="utf-8"))
    page_count = manifest["sources"]["slide"]["page_count"]
    lines = ["# Đánh giá truy xuất", "", "Tập nhỏ gồm 8 truy vấn với các trang tham chiếu đã kiểm tra trên text layer PDF. Tập trang liên quan **chưa đầy đủ**; Precision@5 dưới đây chỉ là cận dưới theo các trang dương đã biết. Mapping ứng viên chưa được chấm là đúng.", "", "| Truy vấn | Trang tham chiếu | Top 5 FTS | Hit@5 | P@5 cận dưới | FTS ms | Quét chuỗi trực tiếp top 5 | Quét ms |", "| --- | --- | --- | ---: | ---: | ---: | --- | ---: |"]
    hits = []
    precision = []
    fts_ms = []
    scan_ms = []
    scan_hits = []
    context_sizes = []
    for query, gold in CASES:
        t = time.perf_counter()
        rows = search_db(query, 5, "slide")
        ftime = (time.perf_counter() - t) * 1000
        got = [x["pdf_page"] for x in rows]
        t = time.perf_counter()
        scanned = baseline(query, page_count)
        stime = (time.perf_counter() - t) * 1000
        hit = bool(set(got) & gold)
        hits.append(hit)
        scan_hits.append(bool(set(scanned) & gold))
        precision.append(len(set(got) & gold) / 5)
        fts_ms.append(ftime)
        scan_ms.append(stime)
        context_sizes.append(sum(min(len(x["text"]), 600) for x in rows))
        safe = query.replace("|", "\\|")
        lines.append(f"| {safe} | {sorted(gold)} | {got} | {int(hit)} | {precision[-1]:.2f} | {ftime:.1f} | {scanned} | {stime:.1f} |")
    negative = bool(unknown_slide_terms(NEGATIVE))
    q = read_jsonl(KNOW / "questions/questions.jsonl")
    mappings = read_jsonl(KNOW / "questions/question_slide_map.jsonl")
    integrity = audit_data(manifest)
    def cli(*args: str) -> tuple[float, str]:
        start = time.perf_counter()
        proc = subprocess.run([sys.executable, str(ROOT / "tools/study.py"), *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
        return (time.perf_counter() - start) * 1000, proc.stdout

    question_ms, question_output = cli("question", "TN1-Q001")
    context_ms, context_output = cli("context", "TN1-Q001", "--limit", "3")
    negative_ms, negative_output = cli("context", NEGATIVE)
    import pymupdf
    with pymupdf.open(ROOT / manifest["sources"]["slide"]["file"]) as doc:
        raw_page51 = doc[50].get_text()
    direct_pdf_check = all(term in raw_page51 for term in ("Hiểm họa ATTT", "ngừng trệ hoạt động"))
    lines.extend(["", f"- Recall@5 theo trang dương đã biết / Hit@5: **{sum(hits)}/{len(hits)} ({sum(hits)/len(hits):.1%})**. Đây không phải recall đầy đủ của mọi trang liên quan.", f"- Precision@5 cận dưới: **{statistics.mean(precision):.3f}**. Các hit khác chưa được phán xét thủ công.", f"- Quét chuỗi trực tiếp: **{sum(scan_hits)}/{len(scan_hits)}** hit; trung vị **{statistics.median(scan_ms):.1f} ms**. FTS trung vị **{statistics.median(fts_ms):.1f} ms**.", f"- Context xấp xỉ 5 kết quả, cắt 600 ký tự/trang: trung vị **{statistics.median(context_sizes):.0f} ký tự**.", f"- Truy vấn âm không có bằng chứng: **{'PASS' if negative else 'FAIL'}**.", f"- Câu hỏi: **{len(q)}** record (gồm ý nhỏ); ánh xạ: **{len(mappings)}** (bao gồm ứng viên); ánh xạ đã xác minh: **{sum(x['mapping_status']=='VERIFIED_MAPPING' for x in mappings)}**. Tỷ lệ ánh xạ chính xác chưa đo được vì chưa có đối chiếu thủ công toàn bộ.", f"- Dẫn nguồn hợp lệ theo kiểm tra SHA, trang và đoạn trích trong dữ liệu: **{'PASS' if integrity['ok'] else 'FAIL'}**. Điều này không xác nhận tính đúng của trích xuất so với hình PDF.", "", "## Demo trên dữ liệu thật", "", "- ID: `TN1-Q001`; nguyên văn câu hỏi:", "", "```text", q[0]["original_text"], "```", "", "- Mapping đã đối chiếu: slide trang PDF 51, hỗ trợ phần định nghĩa hiểm họa. Phần ví dụ Wi-Fi của câu hỏi vẫn ở trạng thái `PARTIALLY_MAPPED`.", "- Evidence context trích từ trang 51: " + next(x["relevant_excerpt"] for x in mappings if x["question_id"] == "TN1-Q001" and x["slide_page"] == 51), f"- Kiểm chứng trực tiếp text layer trang PDF 51 có hai cụm định nghĩa và kết luận: **{direct_pdf_check}**; ảnh PDF cũng đã được xem trực quan.", f"- `question TN1-Q001`: {question_ms:.1f} ms, {len(question_output)} ký tự; `context TN1-Q001 --limit 3`: {context_ms:.1f} ms, {len(context_output)} ký tự.", f"- Truy vấn âm `{NEGATIVE}`: {negative_ms:.1f} ms, {len(negative_output)} ký tự; phản hồi từ chối đúng: **{'Chưa tìm được căn cứ đủ tin cậy' in negative_output}**.", "", "## Giới hạn và bước tiếp", "", "Đánh giá hình, bảng, công thức và mức hỗ trợ ngữ nghĩa cần đối chiếu trực quan. Truy vấn quét chuỗi trực tiếp là baseline đơn giản; không mở rộng đồng nghĩa. Không dùng chỉ số tự ước lượng làm chứng cứ học thuật.", ""])
    report = ROOT / "reports/RETRIEVAL_EVALUATION.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Hit@5={sum(hits)}/{len(hits)} FTS_median_ms={statistics.median(fts_ms):.1f} baseline_median_ms={statistics.median(scan_ms):.1f} negative={negative}")


if __name__ == "__main__":
    run_eval()
