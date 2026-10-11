# Ứng dụng học Tốt nghiệp 1 — bản học được cho tuần đầu

## Mở trên Windows 11

Nhấp đúp **`MO_UNG_DUNG.cmd`** ở thư mục gốc. Trình duyệt mở **http://127.0.0.1:8765**. Máy này đã có Python; không cần cài thư viện, tài khoản hoặc kết nối mạng để học. Trên máy khác cần Python 3.10 trở lên. Đóng ứng dụng bằng `DUNG_UNG_DUNG.cmd`; đóng tab cũng không mất tiến độ.

Hoặc chạy ở thư mục repository:

```powershell
python -m study_app.server
```

Ngày đầu: mở **Phiên học hôm nay**, viết câu trả lời, nộp để mở đáp án, đánh dấu các ý thực sự có trong bài rồi lưu đánh giá. Mục **Ôn tập & câu sai** giữ ý thiếu và ngày ôn tiếp theo. Khi chưa đến 12/10, ứng dụng mở ngày 1; sau đó chọn ngày theo lịch, vẫn có thể mở từng ngày riêng.

## Chức năng đã dùng được

| Phần | Phạm vi bản này |
|---|---|
| Phiên học | 51 trang ngày, 12/10–01/12/2026; nhiệm vụ, thời lượng, câu hỏi, lịch dời, mức hoàn thành |
| Thẻ lý thuyết | 23 câu tuần đầu: Q001–011, Q032–036, Q068–074; câu hỏi trước, bản nháp, 2 mức gợi ý, đáp án, rubric, nguồn PDF |
| Ôn lại | SQLite lưu bài, ý thiếu, mức tự tin, số lần nhớ, ngày ôn; mốc +1/+3/+7/+14/+30 |
| Toán | RSA, ElGamal, DH, ECC, ECDH; số nguyên chính xác, từng bước, chế độ mẫu/giảm gợi ý/tự giải, đồ thị điểm hữu hạn |
| Sơ đồ | Ba giao thức băm/salt/Lamport, mô hình phòng thủ nhiều lớp; SVG tô sáng, ẩn/hiện và điền thành phần |
| Đọc mã | Hai bài C nguyên văn Q028–029, chọn dòng lỗi và viết cơ chế trước khi mở giải thích |
| Thi | Hai đề luyện tuần đầu có rubric; ba đề mẫu gốc có đồng hồ 180 phút và lưu bài, **chưa đủ đáp án kiểm chứng** |
| Sao lưu | Xuất/khôi phục JSON, hợp nhất lịch sử; lịch học chỉnh tay hoặc dời phần còn lại |

### Cách đánh giá

Lý thuyết và tự luận **tự đối chiếu rubric**, không giả lập chấm ngữ nghĩa hoặc dùng từ khóa để khẳng định đúng. Điểm là tỷ lệ ý được người học xác nhận; cần ≥85%, đủ ý cốt lõi, không sai trọng yếu. Phép tính và đáp án điền sơ đồ kiểm tra kết quả trực tiếp; bài mã chỉ kiểm tra vị trí dòng, cơ chế vẫn cần tự đối chiếu.

Một lần xem mẫu, dùng gợi ý hoặc thiếu tự tin không tính nhớ độc lập. Hai lần nhớ độc lập vào các ngày ôn khác nhau mới ghi ổn định. Luyện nhiều lần trong cùng ngày không tăng bậc lịch ôn. Trả lời sai sẽ quay về mốc 1 ngày. Đây là lịch ôn đơn giản, **không phải FSRS**.

Đánh dấu nhiệm vụ là tự báo cáo đã làm. Câu chỉ được ghi “đã làm & đối chiếu” khi có bài nộp và đánh giá; mở trang không làm tăng tiến độ.

## Dữ liệu và nguồn

- Dữ liệu cá nhân: `%LOCALAPPDATA%\ON_THI_TN1\study.sqlite3`. Không nằm trong Git. Sao lưu qua giao diện trước khi chuyển máy.
- Kiểm thử riêng: `python -m study_app.server --port 8766 --data-dir .qa/app-data`. Không dùng dữ liệu kiểm thử làm thành tích học thật.
- `content/bank.json`: 80 câu chính và 43 mục con nguyên văn, 23 đáp án/rubric, chứng cứ theo trang, lịch 51 ngày.
- `content/coverage.csv`: ma trận câu gốc, trang đề cương, trang slide đã đối chiếu và tình trạng bao phủ. `PRACTICE_READY_PARTIAL` nghĩa chỉ có một bài thực hành hỗ trợ, chưa đủ mọi yêu cầu câu hỏi.
- `content/plan.csv`: lịch có thể đọc bằng Excel; dữ liệu chuẩn trong ứng dụng là JSON + SQLite.
- `build_content.py`: dựng lại ngân hàng, kiểm tra SHA slide và đề cương. Không thay tài liệu gốc hoặc kho truy xuất.

Slide là căn cứ chính. Ví dụ và phân tích vận dụng ghi `DERIVED`; công thức thuật toán dùng chuẩn bổ sung ghi `EXTERNAL`, vì slide không cung cấp đầy đủ các thuật toán số học. Mỗi câu lý thuyết có liên kết trang PDF và đoạn chứng cứ. Hình đề gốc được giữ kèm cho câu hỏi có sơ đồ; không thay hình bằng sơ đồ ASCII.

Các quy tắc mật khẩu cũ trong slide được ghi rõ là nội dung giáo trình, không gán thành chuẩn triển khai hiện hành. ElGamal bài 1 thiếu k, ECC bài 2 ghi “mod 1”, ECC mã hóa thông điệp số thiếu quy tắc ánh xạ: không tự sửa hoặc tạo một kết quả duy nhất.

Nguồn thuật toán: [RSA — RFC 8017 §5.1](https://www.rfc-editor.org/rfc/rfc8017.html#section-5.1), [ElGamal — HAC §8.4](https://cacr.uwaterloo.ca/hac/about/chap8.pdf), [DH — RFC 2631 §2.1.1](https://www.rfc-editor.org/rfc/rfc2631.html#section-2.1.1), [ECC/ECDH — SEC 1 v2](https://www.secg.org/sec1-v2.pdf). Liên kết ngoài chỉ mở khi người dùng chọn; học offline vẫn xem được công thức và kết quả. KaTeX 0.18.7, font và giấy phép được lưu sẵn trong `static/vendor/katex`, có URL và SHA gói trong `provenance.json`.

Nguồn bổ sung cho bài C: [WG14 N1570, lời nói đầu, trang PDF 14](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=14) ghi việc loại bỏ `gets`; §7.21.7.2 và §7.21.6.5 quy định `fgets`/`snprintf`. Đoạn mã trong đề vẫn được giữ nguyên để phân tích.

## Việc còn lại trước nghiệm thu đủ 51 ngày

1. Đối chiếu đáp án cho phần sau tuần 1, xây rubric cho ba đề mẫu chính thức.
2. Bổ sung các bài mã PHP/XSS, Snort, iptables, sơ đồ VPN/IPsec; hiện câu hỏi gốc có sẵn, đáp án chưa được mở như dữ liệu kiểm chứng.
3. Mở rộng toán để bao phủ mọi yêu cầu của từng bài, thay vì chỉ các bảng thuật toán hiện có.
4. Nhập đề cương mới có phiên bản, so khớp/gộp có xác nhận, lập lại lịch theo độ khó và ngày thi mới. Bản này chỉ có dời lịch thủ công và lịch ôn từng câu.

**Bản này đạt mốc học được tuần đầu; chưa tuyên bố hoàn thành hệ thống học đủ 51 ngày.**

## Kiểm tra

```powershell
python -m unittest discover -s tests -v
python tools/study.py audit
```

Xem [báo cáo nghiệm thu tuần đầu](../reports/STUDY_APP_WEEK1.md) để biết thao tác và phạm vi đã thử. Các file PDF và `Giai_de_cuong.docx` không bị chỉnh sửa trong lần triển khai ứng dụng này.
