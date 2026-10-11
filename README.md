# Ôn thi Tốt nghiệp 1

## Ứng dụng học offline

Nhấp đúp **[MO_UNG_DUNG.cmd](MO_UNG_DUNG.cmd)** để mở ứng dụng tại **http://127.0.0.1:8765**. Có thể tự trả lời, đối chiếu rubric, luyện toán/sơ đồ/mã nguồn, thi tự luận và lưu tiến độ trên máy.

**Bản hiện tại học được tuần đầu (23 câu đã đối chiếu).** Lịch đủ 51 ngày; đáp án các phần sau vẫn đang chờ kiểm chứng. [Hướng dẫn và phạm vi](study_app/README.md) · [Báo cáo kiểm thử](reports/STUDY_APP_WEEK1.md).

## Kho tài liệu và truy xuất

Kho tri thức cục bộ cho học phần Tốt nghiệp 1 (An toàn thông tin). Ba PDF gốc ở thư mục root. Văn bản trích xuất theo từng trang nằm ở `knowledge/`; mỗi trang ghi SHA của PDF và trạng thái kiểm chứng. Nội dung trích xuất là dữ liệu nguồn, chưa phải đáp án.

## Cài đặt và sử dụng

```powershell
python -m pip install -r requirements.txt
python tools/study.py build
python tools/study.py status
python tools/study.py search "khóa công khai"
python tools/study.py question TN1-Q001
python tools/study.py page slide 51
python tools/study.py context TN1-Q001
python tools/study.py audit
python tools/study.py eval
python -m unittest discover -s tests -v
```

`build` bỏ qua PDF không đổi dựa trên SHA-256. SQLite ở `knowledge/index/` là cache cục bộ, có thể dựng lại. Các file Markdown, JSONL và manifest được commit để Chat đọc qua GitHub. Không cần API key, GPU hoặc dịch vụ nền. Thông tư chỉ được kiểm kê, chưa trích xuất.

`knowledge/questions/reviewed_mappings.jsonl` lưu các ánh xạ đã đối chiếu thủ công, gắn SHA nguồn; thay đổi file này rồi chạy `build` để cập nhật bản đồ. Khi sửa logic parser/index trong `tools/study.py`, tăng `GENERATOR_VERSION` để làm mới dữ liệu phụ thuộc.

**Giới hạn:** nhiều trang slide có hình hoặc công thức. Trạng thái `EXTRACTED_UNREVIEWED` và `VISUAL_REVIEW_REQUIRED` không xác nhận đúng nội dung. Mapping tìm kiếm là ứng viên cho đến khi có người đối chiếu PDF. Xem [báo cáo trích xuất](reports/EXTRACTION_AUDIT.md), [đánh giá tìm kiếm](reports/RETRIEVAL_EVALUATION.md), [quy trình Agent](docs/STUDY_AGENT_PROTOCOL.md), [hướng dẫn Chat](docs/CHAT_HANDOFF.md).
