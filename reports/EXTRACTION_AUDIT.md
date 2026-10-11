# Kiểm kê và chất lượng trích xuất

Dữ liệu được trích máy, **không tự động được coi là đã đối chiếu**. Số trang dưới đây là trang PDF vật lý.

## slide: CSATTT_SLIDE_FULL.pdf

- SHA-256: `75e22524b318039d960b72339afed37b56b492e94d60e5f1e03aada2ddfe7ec6`
- Số trang PDF: 497
- VERIFIED: 0
- EXTRACTED_UNREVIEWED: 243
- VISUAL_REVIEW_REQUIRED: 254
- EXTRACTION_FAILED: 0
- LOW_TEXT: 54 trang; 22, 31, 42, 43, 44, 70, 87, 98, 102, 111, 145, 159, 167, 168, 171, 215, 216, 224, 227, 230, 235, 239, 256, 264, 268, 283, 285, 286, 288, 289, 293, 295, 300, 304, 306, 308, 310, 311, 330, 331, 332, 368, 369, 371, 372, 373, 379, 381, 385, 389, 395, 398, 400, 448
- IMAGE_PRESENT: 240 trang; 1, 2, 5, 6, 7, 8, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 26, 29, 31, 32, 33, 34, 35, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52, 55, 56, 58, 59, 60, 61, 63, 64, 67, 70, 74, 75, 79, 80, 87, 88, 89, 90, 92, 95, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 111, 120, 137, 138, 139, 140, 142, 143, 144, 145, 146, 159, 167, 168, 171, 172, 173, 174, 176, 178, 179, 181, 183, 184, 187, 188, 189, 190, 191, 192, 197, 198 …
- MATH_REVIEW_REQUIRED: 28 trang; 12, 53, 103, 104, 105, 122, 150, 154, 155, 164, 178, 184, 188, 189, 198, 233, 279, 280, 281, 287, 294, 296, 323, 334, 358, 405, 476, 492
- UNICODE_REPLACEMENT: 1 trang; 49
- DUPLICATE_PAGE_NUMBER: 41 trang; 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45

## outline: Đề cương HPTTN1.pdf

- SHA-256: `7814c8ba2ca321647cc6e575b29744c25a305a15920ef9d2bd560f8179b35739`
- Số trang PDF: 18
- VERIFIED: 0
- EXTRACTED_UNREVIEWED: 7
- VISUAL_REVIEW_REQUIRED: 11
- EXTRACTION_FAILED: 0
- IMAGE_PRESENT: 5 trang; 2, 3, 14, 15, 16
- MATH_REVIEW_REQUIRED: 9 trang; 7, 8, 9, 11, 12, 13, 14, 15, 16

## law: Thông tư-09-2020-TT-NHNN .pdf

- SHA-256: `877afd9336574a2c0077a1d247587973458590d1b9fee5226ce445d9228cc20e`
- Số trang PDF: 38
- Chỉ kiểm kê; PDF dạng ảnh, không trích xuất trong đợt này.

## Đối chiếu trực quan đã thực hiện

- Đề cương trang PDF 2: sơ đồ xác thực mật khẩu không hiện đủ trong text layer; ảnh gốc được giữ trong `knowledge/assets/`.
- Đề cương trang PDF 12: bản PDF gốc thực sự ghi `mod 1` ở bài ECC thứ hai. Đây là dữ kiện nghi vấn của **nguồn gốc**, chưa được tự sửa. Ký hiệu lũy thừa/chỉ số cũng bị phẳng hóa khi trích text.
- Slide trang PDF 178: công thức và mũi tên trong sơ đồ khóa công khai mất trật tự ở text layer; có ảnh gốc chọn lọc để kiểm chứng.

## Việc cần kiểm chứng

- Các trang gắn `VISUAL_REVIEW_REQUIRED` cần đọc PDF/hình gốc khi dùng làm chứng cứ. Chưa có kiểm tra thủ công toàn bộ slide.
- Phát hiện ảnh chỉ dựa trên ảnh nhúng; sơ đồ vector, bảng và công thức có thể cần đối chiếu dù không có cờ ảnh. Chưa OCR toàn bộ tài liệu.
- `EXTRACTED_UNREVIEWED` chỉ nghĩa là có văn bản trích xuất; không xác nhận đúng công thức, thứ tự bảng hay ngữ nghĩa.
