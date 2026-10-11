# Dùng kho tri thức từ ChatGPT Chat qua GitHub

Repo: <https://github.com/Minhlike/ON_THI_TN1>. Chat có thể đọc file đã push qua GitHub nhưng không nên giả định chạy được script trên máy local.

1. Đọc `knowledge/manifest.json` để biết tên Unicode chính xác và SHA-256 của ba PDF. Hai nguồn chính là slide và đề cương; Thông tư chỉ được kiểm kê.
2. Tìm ID trong `knowledge/questions/QUESTION_INDEX.md`, rồi mở record nguyên văn ở `knowledge/questions/questions.jsonl`. Có thể lấy bản đề cương theo trang tại `knowledge/outline/pages/pNNNN.md`.
3. `knowledge/questions/question_slide_map.jsonl` chứa **ứng viên** trang slide. Mở `knowledge/slide/pages/pNNNN.md`, kiểm đoạn trích hiện diện và đọc trạng thái ở dòng metadata. Không gọi `UNVERIFIED_CANDIDATE` là đã xác minh.
4. Dẫn trang PDF vật lý, không suy ra từ số slide in. Khi công thức, sơ đồ, bảng hoặc dữ kiện chưa rõ, mở PDF gốc ở đúng trang. Nếu Chat không truy cập được PDF hoặc file Markdown, nói rõ giới hạn, yêu cầu đường dẫn/ảnh trang cần thiết; không khẳng định đã đối chiếu.
5. Kiểm đồng bộ: SHA trong manifest và mỗi trang phải khớp; khi có thể, so SHA file PDF trên GitHub. Nếu commit khác hoặc SHA không khớp, xem dữ liệu có thể cũ.

Chỉ dùng số ít trang cần cho câu trả lời. Giao thức đầy đủ ở `docs/STUDY_AGENT_PROTOCOL.md`.
