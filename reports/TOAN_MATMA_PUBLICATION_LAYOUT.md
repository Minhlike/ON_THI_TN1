# Nghiệm thu bố cục xuất bản giáo trình Toán mật mã

Ngày 17/10/2026 · Nhánh `codex/week1-offline-study` · Nội dung khóa tại `1179eca2ac9740b0e99a753b4f96bd6ac86f2de8`.

## Kết quả

Đã tối ưu bố cục và xuất lại bằng Microsoft Word 2016 trên Windows. **144 → 143 trang A4**. Không đặt mục tiêu giảm trang; giữ khả năng đọc và sự liền mạch của lời giải trước.

Tệp học chính vẫn là `co_so_matmahoc/toan_matma.docx`. [PDF đối chiếu Word 2016](TOAN_MATMA_WORD2016.pdf) và [dấu vết kiểm tra chi tiết](TOAN_MATMA_PUBLICATION_LAYOUT.json).

## Bất biến nội dung

| Hạng mục | Trước | Sau | Cách xác nhận |
|---|---:|---:|---|
| Dạng toán | 27 | 27 | Giữ nguyên văn và thứ tự đề mục |
| Bài mẫu | 37 | 37 | Giữ nguyên văn và thứ tự bài |
| Đáp án tự luyện | 69 | 69 | Toàn bộ văn bản và ô bảng khớp baseline |
| Bài về nhà | 7 | 7 | Giữ nội dung, ảnh và thứ tự |
| Phương trình OMML | 1.360 | 1.360 | Cấu trúc toán và mọi ký tự khớp theo thứ tự |
| Nhãn Jacobi limUpp | 70 | 70 | Cấu trúc nhãn trên dấu bằng giữ nguyên |
| Bảng Word | 76 | 76 | Mỗi hàng, ô, chỉ số và dữ liệu khớp |
| Ảnh nhúng | 75 | 75 | Hash từng media và thứ tự sử dụng khớp |
| Mục Casio chi tiết | 35 | 35 | Không rút gọn hoặc chuyển vị trí nội dung |

Đối chiếu nội dung bỏ qua **số trang được sinh trong mục lục**; đối chiếu OMML chỉ bỏ qua định dạng `w:rPr` và metadata Word, không bỏ qua cấu trúc phép toán `m:*`. Không sửa lý thuyết, phép tính, kết quả, thuật toán hoặc ký hiệu; không thêm phụ lục. 64 tệp nguồn vẫn khớp SHA256.

## Các thay đổi thiết kế

| Thành phần | Trước | Sau |
|---|---|---|
| Style | Nhiều đoạn Normal và ghi đè trực tiếp | Style riêng cho lý thuyết, quy trình, bài mẫu, lời giải, Casio, bài luyện, đáp án, kết luận, hình và phương trình |
| Chữ chính | Times New Roman 14 với định dạng trực tiếp xen kẽ | Style nội dung Times New Roman 14; chữ đen, nền trắng; phông toán Cambria Math giữ nguyên |
| Phân cấp | Chương và dạng đã có heading; vai trò nội bộ chưa tách style | Chương 18 đậm, dạng 16 đậm, đề mục 14 đậm; kế thừa heading để giữ điều hướng Word |
| Phân trang | Keep with next/keep lines rộng, cả nhiều ô bảng | Chỉ giữ các cụm cần thiết; tiêu đề đi cùng phần mở đầu; công thức ngắn đi cùng nhau; phép tính cuối đi cùng kết luận |
| Đầu chương | Phân trang phụ thuộc các khối giữ cùng nhau | Chương tiếp nối khi còn đủ chỗ; giữ phân trang riêng cho mục lục và phần học đầu tiên |
| Phương trình riêng | Chủ yếu căn giữa từng dòng | Căn trái trên cùng lề tính toán; giãn dòng tự động, không dùng chiều cao cố định hoặc dấu cách để canh |
| Bảng | Cỡ chữ, căn lề, cột và padding thiếu nhất quán | Căn số theo cột, cột tính theo dữ liệu, viền đen 0,5 pt; chữ 14, bảng số từ 9 cột dùng 13; padding dọc 1–2 pt |
| Bảng qua trang | Header cần được bảo vệ theo từng bảng | Cả 76 bảng đặt lặp header và không chẻ hàng; bảng tính gọn giữ liền khối, BSGS không dồn riêng hàng cuối |
| Ảnh và chú thích | Kích thước chung, chú thích ít phân biệt | Giữ tỷ lệ và media gốc; hình chi tiết khoảng 16,94 cm, sơ đồ GCD gọn khoảng 14,72 cm; chú thích 11,5 nghiêng, đen, sát hình |
| Casio | Nhiều đoạn chưa có style theo vai trò | Nhãn đậm, khoảng cách và style riêng, công thức native giữ nguyên; không thêm hộp hoặc bảng trình bày |

Màu sẵn có **bên trong ảnh slide gốc** được giữ để bảo toàn chứng cứ. Chữ được biên tập trong Word là màu đen. Không cắt, vẽ lại, nén hoặc thay media.

## Kiểm tra bản xuất

- Word **16.0, build 16.0.4756**, Microsoft Office 2016: mở và xuất PDF thành công; BuildUp cả **1.360 phương trình** trên bản QA không lưu.
- Rà toàn bộ **143 ảnh trang** qua các tờ tổng quan và mở riêng các trang quan trọng: EEA, Jacobi, TT4, BSGS, bảng RSA rộng, ECC, sơ đồ và bài nhà. Không phát hiện chồng chữ, mất công thức, mất dữ kiện hoặc tràn lề trong bản xem.
- Kiểm tọa độ lớp chữ PDF: **không có ký tự vượt vùng kiểm tra**. Đối chiếu **15,174 ký tự toán** theo từng trang: không có trang thiếu ký tự. Kiểm tra sự hiện diện ký tự được dùng cùng ảnh trang, không coi là chứng minh toán học mới.
- Có **1 bảng thực sự qua trang**; header lặp, mỗi hàng giữ nguyên khối. Các bảng BSGS có cả hai nhóm nhãn trong cùng một bảng được giữ liền để tránh header gây nhầm ngữ cảnh.
- Mục lục và số trang cập nhật bằng Word. Giữ đủ chuỗi học từ nhận diện đến lỗi dễ mắc; đáp án và Casio nằm tại bài tương ứng.
- Chưa in thử trên máy in vật lý. Đây là nghiệm thu hiển thị bằng Word 2016 và PDF; không tuyên bố kết quả in vật lý đã được kiểm tra.

## Sao lưu và dấu vân tay

Bản trước dàn trang được lưu trong `.qa/crypto/publication_layout/baseline_1179eca.docx` và `baseline_1179eca.pdf`, đồng thời có trong Git tại commit khóa nội dung. Không ghi đè bản sao này.

- DOCX trước: `4bced2ea03d0f8a6ca9d51ebaf5716379145ea4f12bcc4187e9224566db2c746`.
- DOCX sau: `4d3d6c9dbe87d212e5bc51cbfb9786c8ad35a164de096050e8e39b77ab90b9f9`.
- PDF sau: `9103b5945b416d29a4a4b2da7c399352c380b1725ea0bbe8e9f8c1155e317a16`.

Báo cáo kiểm toán nội dung trước vẫn giữ các thông số và hash của phiên bản khóa tại `1179eca`; báo cáo này ghi nhận bản dàn trang kế tiếp. Không mở lại đợt sửa nội dung trong nhiệm vụ xuất bản.
