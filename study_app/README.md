# Ứng dụng học Tốt nghiệp 1 — bản học được đến 19/10

## Mở trên Windows 11

Nhấp đúp **`MO_UNG_DUNG.cmd`** ở thư mục gốc. Trình duyệt mở **http://127.0.0.1:8765**. Máy này đã có Python; không cần cài thư viện, tài khoản hoặc kết nối mạng để học. Trên máy khác cần Python 3.10 trở lên. Đóng ứng dụng bằng `DUNG_UNG_DUNG.cmd`; đóng tab cũng không mất tiến độ.

Sau cập nhật repository, file mở so phiên bản mã/ngân hàng/giao diện đã nạp với file hiện tại và tự thay máy chủ cũ do launcher quản lý. Nếu bạn tự chạy từ terminal, đóng terminal đó rồi mở lại. Khi thấy báo bản cũ, mở lại ứng dụng và tải lại tab.

Hoặc chạy ở thư mục repository:

```powershell
python -m study_app.server
```

Ngày đầu: mở **Phiên học hôm nay**, viết câu trả lời, nộp để mở đáp án, đánh dấu các ý thực sự có trong bài rồi lưu đánh giá. Mục **Ôn tập & câu sai** giữ ý thiếu và ngày ôn tiếp theo. Khi chưa đến 12/10, ứng dụng mở ngày 1; sau đó chọn ngày theo lịch, vẫn có thể mở từng ngày riêng.

## Chức năng đã dùng được

| Phần | Phạm vi bản này |
|---|---|
| Phiên học | 51 trang ngày, 12/10–01/12/2026; nhiệm vụ, thời lượng, câu hỏi, lịch dời, mức hoàn thành |
| Thẻ lý thuyết | 28 câu: Q001–016, Q032–036, Q068–074; câu hỏi trước, bản nháp, 2 mức gợi ý, đáp án, rubric, nguồn PDF |
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
- `content/bank.json`: 80 câu chính và 43 mục con nguyên văn, 28 đáp án/rubric, chứng cứ theo trang, lịch 51 ngày.
- `content/child_coverage.csv`: kiểm kê riêng 43 mục con, yêu cầu/bước còn thiếu và rubric đã đối chiếu; hiện 12/43 đủ đáp án, 6 có hỗ trợ thực hành một phần, 25 chờ review.
- `content/day_coverage.csv`: coverage câu chính/mục con và mã chưa review theo từng ngày; không tính thực hành một phần thành đáp án hoàn chỉnh.
- `content/coverage.csv`: ma trận câu gốc, trang đề cương, trang slide đã đối chiếu và tình trạng bao phủ. `PRACTICE_READY_PARTIAL` nghĩa chỉ có một bài thực hành hỗ trợ, chưa đủ mọi yêu cầu câu hỏi.
- `content/plan.csv`: lịch có thể đọc bằng Excel; dữ liệu chuẩn trong ứng dụng là JSON + SQLite.
- `build_content.py`: dựng lại ngân hàng, kiểm tra SHA slide và đề cương. Không thay tài liệu gốc hoặc kho truy xuất.

Slide là căn cứ chính. Ví dụ và phân tích vận dụng ghi `DERIVED`; công thức thuật toán dùng chuẩn bổ sung ghi `EXTERNAL`, vì slide không cung cấp đầy đủ các thuật toán số học. Mỗi câu lý thuyết có liên kết trang PDF và đoạn chứng cứ. Hình đề gốc được giữ kèm cho câu hỏi có sơ đồ; không thay hình bằng sơ đồ ASCII.

Các quy tắc mật khẩu cũ trong slide được ghi rõ là nội dung giáo trình, không gán thành chuẩn triển khai hiện hành. ElGamal bài 1 thiếu k, ECC bài 2 ghi “mod 1”, ECC mã hóa thông điệp số thiếu quy tắc ánh xạ: không tự sửa hoặc tạo một kết quả duy nhất.

Nguồn thuật toán: [RSA — RFC 8017 §5.1](https://www.rfc-editor.org/rfc/rfc8017.html#section-5.1), [ElGamal — HAC §8.4](https://cacr.uwaterloo.ca/hac/about/chap8.pdf), [DH — RFC 2631 §2.1.1](https://www.rfc-editor.org/rfc/rfc2631.html#section-2.1.1), [ECC/ECDH — SEC 1 v2](https://www.secg.org/sec1-v2.pdf). Liên kết ngoài chỉ mở khi người dùng chọn; học offline vẫn xem được công thức và kết quả. KaTeX 0.18.7, font và giấy phép được lưu sẵn trong `static/vendor/katex`, có URL và SHA gói trong `provenance.json`.

Nguồn bổ sung cho bài C: [WG14 N1570, lời nói đầu, trang PDF 14](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=14) ghi việc loại bỏ `gets`; §7.21.7.2 và §7.21.6.5 quy định `fgets`/`snprintf`. Đoạn mã trong đề vẫn được giữ nguyên để phân tích.

## Việc còn lại trước nghiệm thu đủ 51 ngày

1. Tiếp tục theo ngày: Q017–018 (20/10), Q019 (21/10), Q020 (22/10), sau đó các phần kế tiếp; xây rubric cho ba đề mẫu chính thức.
2. Bổ sung các bài mã PHP/XSS, Snort, iptables, sơ đồ VPN/IPsec; hiện câu hỏi gốc có sẵn, đáp án chưa được mở như dữ liệu kiểm chứng.
3. Mở rộng toán để bao phủ mọi yêu cầu của từng bài, thay vì chỉ các bảng thuật toán hiện có.

**Bản này đạt mốc học được đến 19/10; chưa hoàn thành nội dung đủ 51 ngày.** Nguồn học cố định là hai PDF hiện có. Điều chỉnh lịch thủ công, khôi phục JSON tiến độ và cập nhật đáp án đã kiểm chứng vẫn được hỗ trợ.

## Chính sách lưu và giờ thi

- Bài thi gửi bản chụp nội dung ngay khi nhập, có số phiên bản, không chờ 400 ms. Đồng hồ giao diện dựa trên giờ máy chủ và thời gian trôi đơn điệu.
- Chỉ nội dung **máy chủ nhận đầy đủ trước deadline** mới được tính vào bài nộp. Yêu cầu đã nhận được xếp thứ tự trước thao tác nộp; việc chờ xử lý SQLite qua deadline không làm mất nội dung đó. Yêu cầu đến đúng/sau deadline bị từ chối cập nhật bài.
- Hết giờ khóa ô nhập, chờ yêu cầu lưu đang chạy rồi nộp. Nộp lặp lại trả cùng bài, không tạo thêm lần ôn. Trạng thái “Đã lưu trên máy chủ” xác nhận đã ghi SQLite.
- Bản nháp được giữ ngay trong trình duyệt để phục hồi khi đóng tab hoặc mất kết nối. Nếu máy chủ chưa nhận trước hạn, nháp xuất hiện **riêng, không tính vào bài đã nộp**. Không thể chứng minh thời điểm gõ chỉ bằng giờ do trình duyệt gửi. Đừng xóa dữ liệu trình duyệt trước khi phục hồi phần chưa lưu; JSON xuất từ máy chủ chỉ chứa phần đã xác nhận.

## Quy tắc khôi phục

JSON v2 ghi thời điểm sửa thiết lập; vẫn đọc bản v1. Khôi phục trong một giao dịch: xung đột/không hợp lệ hủy toàn bộ. Mã phiên phải giữ nguyên đề, giờ bắt đầu và deadline. Bản thi đã nộp là kết thúc; bản cũ không mở lại/sửa bài đó. Phiên đang làm chọn số phiên bản mới hơn, rồi thời điểm sửa; cùng phiên bản khác nội dung hoặc hai bài nộp khác nhau bị báo xung đột. Bản nộp cũ hơn bản đang làm cũng bị báo xung đột để giữ dữ liệu.

Thiết lập/lịch/nháp chọn thời điểm sửa mới hơn; thiết lập v1 thiếu thời điểm chỉ khởi tạo khóa chưa có, không ghi đè. Bài làm giữ dữ liệu gốc theo ID và cập nhật phần chấm mới hơn. Lịch sử thực hành được hợp nhất theo ID. Không xóa lịch sử đang có.

## Kiểm tra

```powershell
python -m unittest discover -s tests -v
python tools/study.py audit
node tools/browser_check.cjs
```

Kiểm thử trình duyệt cần Node + Playwright và Chrome; đây chỉ là công cụ QA. Có thể chỉ định `QA_PYTHON`, `QA_CHROME`, `QA_PORT`, `QA_OUTPUT` và `NODE_PATH`. Script tự mở máy chủ/cơ sở dữ liệu/profile tách biệt, đóng các tiến trình do nó tạo, giữ dữ liệu QA tại đường dẫn in cuối để điều tra; không dùng tiến độ học thật. Đồng hồ giả và cổng chờ xử lý chỉ có trong fixture kiểm thử, không có API chỉnh giờ trong sản phẩm.

Xem [báo cáo sửa lỗi reviewer](../reports/REVIEWER_FIXES.md) và [báo cáo tuần đầu](../reports/STUDY_APP_WEEK1.md). Các file PDF và `Giai_de_cuong.docx` không bị chỉnh sửa.
