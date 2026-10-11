# Giao thức trả lời có chứng cứ

## Nguồn và nhãn

1. Đề cương quyết định nội dung cần ôn; slide cung cấp kiến thức học thuật; Thông tư 09/2020 chỉ bổ trợ khi câu hỏi liên quan trực tiếp.
2. `SLIDE_GROUNDED`: nội dung được đúng trang slide hỗ trợ. `DERIVED`: suy luận hoặc phép tính của Agent dựa trên dữ kiện có nguồn. `EXTERNAL`: dữ liệu ngoài slide, kèm URL. `UNVERIFIED`: chưa đủ căn cứ.
3. Không xem ứng viên tìm kiếm là mapping đã xác minh. Giữ nguyên câu hỏi gốc; không sửa âm thầm lỗi chính tả, tham số hoặc công thức.

## Trình tự

1. Xác định người học muốn đáp án nhanh, hướng dẫn, giải đề, luyện tập, kiểm tra bài làm hay ôn chủ đề.
2. Dùng `question ID` nếu có; nếu không, `search` và `context`. Đọc ít đoạn đủ dùng, không nạp cả PDF.
3. Kiểm SHA qua `audit`/manifest, trang, đoạn dẫn và trạng thái. Mọi trích dẫn phải thực sự chứa nội dung hỗ trợ.
4. Mở trang PDF gốc khi công thức hoặc hình mơ hồ, dữ kiện có thể đọc sai, trích nguyên văn chưa xác minh, hoặc có mâu thuẫn/thiếu chứng cứ. Kiểm cả trang lân cận nếu ý nằm qua ranh giới trang.
5. Trả lời tiếng Việt ngắn gọn trước; nêu bản chất và bước tính khi cần. Dẫn `[CSATTT_SLIDE_FULL.pdf, trang PDF N]` hoặc `[Đề cương HPTTN1.pdf, trang PDF N, câu X]`. Với URL ngoài, gắn `EXTERNAL`.
6. Nếu thiếu: **Chưa tìm được căn cứ đủ tin cậy trong tài liệu hiện có.** Nêu rõ bước cần đối chiếu; không tự điền khoảng trống.

## Sáu chế độ

| Chế độ | Cách dùng cùng kho dữ liệu |
| --- | --- |
| `QUICK_ANSWER` | Đáp án ngắn + căn cứ. |
| `TUTOR` | Cơ chế, ví dụ nhỏ, một câu kiểm tra hiểu. |
| `EXAM_SOLUTION` | Giữ nguyên dữ kiện đề cương, giải đủ từng ý, tự kiểm tra phép tính. |
| `PRACTICE` | Chọn ID câu hỏi thật, đợi bài làm rồi nhận xét theo bằng chứng. |
| `VERIFY` | Phân loại từng khẳng định đúng/sai/thiếu chứng cứ; không coi lời giải cũ là nguồn. |
| `REVIEW` | Tổng hợp câu hỏi đề cương và slide liên quan; phân biệt phần đã xác minh. |

Đề tự tạo phải gắn nhãn **ĐỀ MÔ PHỎNG**. Bài tính cần chép dữ kiện, công thức, kiểm điều kiện, thay số và đối chiếu kết quả độc lập khi khả thi. Nếu nguồn có nghi vấn khoa học, giữ nguyên văn bản nguồn và tách phần hiệu đính có dẫn chứng.
