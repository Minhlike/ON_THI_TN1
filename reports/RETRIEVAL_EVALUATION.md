# Đánh giá truy xuất

Tập nhỏ gồm 8 truy vấn với các trang tham chiếu đã kiểm tra trên text layer PDF. Tập trang liên quan **chưa đầy đủ**; Precision@5 dưới đây chỉ là cận dưới theo các trang dương đã biết. Mapping ứng viên chưa được chấm là đúng.

| Truy vấn | Trang tham chiếu | Top 5 FTS | Hit@5 | P@5 cận dưới | FTS ms | Quét chuỗi trực tiếp top 5 | Quét ms |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| hiểm họa an toàn thông tin | [51] | [52, 57, 51, 127, 65] | 1 | 0.20 | 25.3 | [3, 46, 50, 51, 52] | 102.1 |
| hiem hoa an toan thong tin | [51] | [52, 57, 51, 127, 65] | 1 | 0.20 | 23.4 | [3, 46, 50, 51, 52] | 96.9 |
| tính chất mật mã khóa công khai | [180] | [180, 181, 177, 179, 258] | 1 | 0.20 | 28.6 | [] | 94.4 |
| SQL Injection | [292] | [296, 292, 294, 297, 293] | 1 | 0.20 | 2.5 | [129, 276, 277, 292, 293] | 93.2 |
| tràn bộ đệm | [302] | [303, 307, 302, 305, 313] | 1 | 0.20 | 5.8 | [302, 303, 304, 305, 306] | 79.1 |
| hệ thống phát hiện xâm nhập IDS | [374] | [374, 376, 364, 375, 16] | 1 | 0.20 | 31.1 | [] | 80.1 |
| mã hóa kênh truyền VPN | [218] | [218, 220, 221, 219, 192] | 1 | 0.20 | 19.7 | [] | 79.3 |
| Diffie-Hellman | [178] | [178] | 1 | 0.20 | 1.0 | [178] | 93.4 |

- Recall@5 theo trang dương đã biết / Hit@5: **8/8 (100.0%)**. Đây không phải recall đầy đủ của mọi trang liên quan.
- Precision@5 cận dưới: **0.200**. Các hit khác chưa được phán xét thủ công.
- Quét chuỗi trực tiếp: **5/8** hit; trung vị **93.3 ms**. FTS trung vị **21.6 ms**.
- Context xấp xỉ 5 kết quả, cắt 600 ký tự/trang: trung vị **1342 ký tự**.
- Truy vấn âm không có bằng chứng: **PASS**.
- Câu hỏi: **123** record (gồm ý nhỏ); ánh xạ: **326** (bao gồm ứng viên); ánh xạ đã xác minh: **1**. Tỷ lệ ánh xạ chính xác chưa đo được vì chưa có đối chiếu thủ công toàn bộ.
- Dẫn nguồn hợp lệ theo kiểm tra SHA, trang và đoạn trích trong dữ liệu: **PASS**. Điều này không xác nhận tính đúng của trích xuất so với hình PDF.

## Demo trên dữ liệu thật

- ID: `TN1-Q001`; nguyên văn câu hỏi:

```text
Bài 1. Trình bày khái niệm hiểm họa an toàn thông tin. Hãy lấy một số ví dụ cụ thể
về hiểm họa an toàn thông tin đối với hệ thống mạng wifi của Học viện Kỹ thuật
mật mã
```

- Mapping đã đối chiếu: slide trang PDF 51, hỗ trợ phần định nghĩa hiểm họa. Phần ví dụ Wi-Fi của câu hỏi vẫn ở trạng thái `PARTIALLY_MAPPED`.
- Evidence context trích từ trang 51: _▪_ **Hiểm họa ATTT** của HTTT là những **khả năng tác động** lên TT, HTTT dẫn tới sự thay đổi, hư hại, sao chép, sự ngăn chặn tiếp cận tới TT; tới sự phá huỷ hoặc sự ngừng trệ hoạt động của vật mang TT.
- Kiểm chứng trực tiếp text layer trang PDF 51 có hai cụm định nghĩa và kết luận: **True**; ảnh PDF cũng đã được xem trực quan.
- `question TN1-Q001`: 221.6 ms, 1953 ký tự; `context TN1-Q001 --limit 3`: 276.1 ms, 1413 ký tự.
- Truy vấn âm `Định lý Poincaré được chứng minh như thế nào?`: 211.1 ms, 103 ký tự; phản hồi từ chối đúng: **True**.

## Giới hạn và bước tiếp

Đánh giá hình, bảng, công thức và mức hỗ trợ ngữ nghĩa cần đối chiếu trực quan. Truy vấn quét chuỗi trực tiếp là baseline đơn giản; không mở rộng đồng nghĩa. Không dùng chỉ số tự ước lượng làm chứng cứ học thuật.
