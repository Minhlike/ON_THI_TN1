# Hệ thống ôn thi Tốt nghiệp 1

- Slide là nguồn học thuật ưu tiên; đề cương xác định câu hỏi phải ôn. Thông tư 09/2020 chỉ dùng cho câu hỏi liên quan trực tiếp.
- Tra cứu `python tools/study.py` trước khi mở PDF; không nạp toàn bộ tài liệu trong mỗi phiên.
- Mọi khẳng định về tài liệu cần trang PDF và đoạn chứng cứ thực sự hỗ trợ. Mapping `UNVERIFIED_CANDIDATE` chỉ là gợi ý tìm kiếm.
- Nếu chứng cứ thiếu, công thức/hình nghi vấn, hoặc dữ liệu chưa kiểm chứng: mở đúng trang PDF để đối chiếu; nếu vẫn thiếu, nói rõ chưa xác minh.
- Không bịa nội dung, câu hỏi, công thức hoặc số trang. Phân biệt `SLIDE_GROUNDED`, `DERIVED`, `EXTERNAL`, `UNVERIFIED`.
- Trước khi sửa kho tri thức, chạy `audit` và kiểm tra SHA nguồn. Sau khi sửa truy xuất, chạy test và `eval`.
- Khi giải bài, giữ nguyên dữ kiện và quy ước đề; ghi riêng chỗ nghi sai, không tự thay số.
- Quy trình trả lời và sáu chế độ học: [docs/STUDY_AGENT_PROTOCOL.md](docs/STUDY_AGENT_PROTOCOL.md). Chỉ nạp khi cần trả lời hoặc hướng dẫn học.
