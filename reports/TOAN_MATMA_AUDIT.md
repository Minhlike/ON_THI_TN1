# Nghiệm thu giáo trình Toán mật mã

Ngày kiểm tra: 17/10/2026. Nhánh: `codex/week1-offline-study`.

Baseline kiểm toán toán học: `a587bbb3de07d50c8c22fe9f837734cc1fc08835`. Baseline bổ sung ảnh slide: `16da57041a16cddb01f53d277edd7e2a4cf7ec07`.

Tệp bàn giao: `co_so_matmahoc/toan_matma.docx`.

## A Kiểm toán toán học

| Phạm vi | Số lượng |
|---|---:|
| Bài mẫu được rà soát | 37 |
| Bài tự luyện gốc được giữ và rà soát | 37 |
| Bài bổ sung trong phạm vi đã học | 32 |
| Bài về nhà được giữ và kiểm tra | 7 |
| Tổng số bài/câu, gồm cả câu lý thuyết | 113 |

Kiểm tra bằng số học nguyên, phân số, Decimal và SymPy 1.14.0:

- **735 kiểm tra** số/bảng: từng hàng của 11 bảng Euclid mở rộng, 43 bảng lũy thừa, 3 bảng CRT, 2 bảng TT4, 5 bảng ba lô, các bảng khóa Merkle–Hellman, căn Rabin, cấp phần tử và điểm ECC. Kiểm tra riêng kết quả 37 bài mẫu, bảy bài về nhà và các trường hợp không tồn tại nghịch đảo.
- **665 kiểm tra** đẳng thức/đồng dư đọc từ công thức OMML sau khi Word lưu lại, gồm các phép biến đổi số và tọa độ ECC. Ký hiệu Jacobi được tính theo ý nghĩa ký hiệu, không coi là phân số thông thường.
- **139 kiểm tra** phép tính trong chuỗi Casio và các ví dụ CALC/ngưỡng xác suất. Sáu chuỗi có trạng thái hoặc chức năng đặc biệt được đối chiếu riêng với hướng dẫn hãng và kiểm số độc lập.
- Các lượt kiểm tra có phạm vi giao nhau; không cộng chúng thành số bài độc lập. Không còn kiểm tra tự động thất bại.

### Những chỗ đã sửa hoặc bổ sung

| Nhóm vấn đề | Đơn vị đếm | Kết quả |
|---|---:|---|
| Tham chiếu số sai trong Casio | 1 | Bỏ `0,502797`; lời giải cũ đã có `0,507297`, nay ghi rõ công thức tích và `0,5072972343`. |
| Dẫn định lý chưa đủ trước lần dùng | 4 | Phát biểu rõ Fermat nhỏ, Bézout, Lagrange và CRT trước khi áp dụng. |
| Nhóm điều kiện cần viết rõ tại công thức/bài dùng | 6 | Dạng 5, 10, 11, 13, 16, 20: tư cách thuộc nhóm; điều kiện TT2/TT4; Blum và bốn căn; khóa RSA; miền ElGamal; điều kiện đường cong và mẫu ECC. |
| Kiểm tra điều kiện cụ thể được thêm trước bài mẫu | 14 | Có kiểm tra nguyên tố, GCD, cấp/phần tử sinh hoặc điểm thuộc đường cong theo đúng số liệu bài. |
| Lời giải Legendre/Jacobi được dựng lại | 10 | Bài mẫu 12–15 và T18–T23; kiểm từng bước và dấu. |
| Dấu bằng có chú thích native | 70 | Dùng `m:limUpp`; số tính chất ở trên dấu bằng, dấu âm vẫn thuộc biểu thức. |

Các số trong bảng là nhóm chỉnh sửa, có giao nhau. Không phát hiện thêm đáp số cuối sai trong những bài số gốc đã tính lại. Công thức ngưỡng sinh nhật/băm được phân biệt với xác suất chính xác; hệ số gần đúng được viết đủ chữ số để khớp phép bấm.

Giữ nguyên dữ kiện bất thường: modulo 57 ở bài căn được phân tích thành 3·19; bài Merkle–Hellman mới có tổng dãy 958 lớn hơn M=737 vẫn giữ nguyên và giải thích vì sao bản tin 1011011 giải đúng, nhưng không bảo đảm mọi bản tin. Giữ phân biệt tên “Elliptic Diffie Helman” của đề với phép mã hóa ECC ElGamal thực sự được yêu cầu.

## B Tổ chức học tại chỗ

- **27 dạng** có nhận diện, trực giác, định lý/điều kiện, quy trình trên giấy, bài mẫu, tự luyện, đáp án và lỗi thường gặp.
- Giữ **37 bài mẫu**, bổ sung kết luận rõ cho từng bài.
- Đưa **37 câu cũ và 32 câu bổ sung**, cùng **69 đáp án tự kiểm**, về đúng dạng toán. Nhóm có nhiều câu gốc được chia lượt làm ngắn; đáp án nằm trong cùng đơn vị học.
- **35 hướng dẫn Casio chi tiết**: 28 vị trí bài mẫu và bảy bài về nhà. Có mục tiêu, chế độ, vị trí phím, chuỗi nhập, kết quả dự kiến và cách đưa kết quả vào bài thi. Các bài chứng minh/nhẩm ngắn có chỉ dẫn làm tay.
- Phân phối nội dung có ích của chương Casio, chương luyện/đáp án, bảng nhớ và phụ lục Casio cũ vào bài học; bỏ các kho tra cứu và mã K1–K9/C1–C3.
- Chương cuối vẫn giữ đủ bảy câu về nhà và cả năm ảnh đề gốc, kể cả ảnh hai câu ECC trùng slide 144.
- Kiểm tra tự động không còn chỉ dẫn buộc tra phụ lục/chương khác; ảnh gốc slide được nhúng tại dạng bài; số slide chỉ là chú thích nhận dạng ảnh, không thay nội dung học.

## C Kiểm toán Word

| Thành phần bản cuối | Số lượng |
|---|---:|
| Trang sau render bằng Microsoft Word | 140 |
| Bảng native Word | 76 |
| Hình nhúng | 75 (9 cũ và 66 ảnh slide bổ sung) |
| Công thức native OMML | 1.344 |
| Chú thích trên dấu bằng còn nguyên sau Word lưu | 70 |

- A4, nội dung chính Times New Roman 14 pt, chữ đen; mục lục tự động và số trang đã cập nhật. Bảng có tiêu đề lặp khi tiếp trang; các bảng ngắn được giữ liền khối.
- Render toàn bộ thành PDF và ảnh trang để rà bố cục; mở riêng các trang công thức Jacobi, bảng nhiều cột, Casio và ECC. Không phát hiện cắt chữ, tràn lề, mất hình hoặc đối tượng Equation Editor cũ. Không có công thức LaTeX thô trong nội dung.
- Cấu trúc ZIP/DOCX, các mục học, 37 mã câu T, 32 mã câu bổ sung và sáu phần của 35 hướng dẫn Casio đều qua kiểm tra.
- Nội dung chín tệp ảnh nhúng khớp SHA256 baseline; **64 tệp nguồn** gồm hai PDF và 62 PNG không đổi SHA256.

## D Bàn giao và giới hạn kiểm chứng

- Đã mở, cập nhật trường, lưu và xuất PDF bằng **Microsoft Word COM phiên bản 16.0**. Chưa xác định riêng giấy phép/build cài trên máy có phải Office 2016; không tuyên bố đã thử trên một bản Office 2016 độc lập khác.
- Các phím và giới hạn Casio được đối chiếu [hướng dẫn chính thức đúng fx-580VN X](https://support.casio.com/global/vi/fx/manual/fx-580VNX/), gồm PDF có biểu tượng bàn phím. **Chưa thao tác trên máy vật lý hoặc trình giả lập**; giá trị màn hình là kết quả dự kiến được kiểm tra số học.
- Cấu trúc chú thích dùng [OMML `limUpp` của Microsoft](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.math.limitupper?view=openxml-3.0.1), đã kiểm tra tồn tại và hiển thị sau Word lưu.
- Bản gốc được sao lưu trước sửa; bản bàn giao chỉ thay sau khi kiểm tra bản dựng và đối chiếu hash tệp đang dùng. Không sửa tài liệu nguồn hoặc ứng dụng học.
- SHA256 bản DOCX: `123eefd939a5769d0e003b345014544c636eb8a0bac76e0179f05fd6bcd973d4`.
- SHA256 bản baseline trước bổ sung ảnh: `cb605c50e0c4d915234842db3d3f0a40874d201716ea96c53ebbdbb1a40717d3`.

## E Học trong một tệp Word với hình gốc

- Nhúng **66 ảnh slide gốc**, phân bổ đủ **27 dạng bài**, gồm lưu đồ Euclid, nhân bình phương, CRT, Jacobi, căn modulo, BSGS, RSA, Rabin, ElGamal, ba lô, Merkle–Hellman, ECC, các sơ đồ băm/xác thực, hàm nén, chứng thư và chữ ký. Mỗi ảnh là một slide riêng, không phải ảnh trang PDF sáu slide thu nhỏ.
- Ảnh được render từ PDF ở 350 dpi, cắt theo khung slide đầy đủ và thêm lề trắng 1 point; đưa vào Word rộng 16,5 cm. Không vẽ lại, không sửa nội dung ảnh. Một số sơ đồ CA vốn là ảnh độ phân giải thấp trong slide; giữ ảnh gốc và giải thích các nhãn bằng chữ ngay bên dưới.
- Bỏ **71 dòng nguồn rời**; giữ phân biệt bài gốc và bài bổ sung. Chú thích tên hình và số slide nằm ngay cạnh ảnh; thông tin trang PDF và vùng cắt để đối chiếu nằm ở `reports/TOAN_MATMA_HINH_SLIDE.json`.
- Đặt ghi chú sửa thiếu/sai ngay dưới ảnh: điều kiện modulo Merkle–Hellman lớn hơn tổng dãy; hai điều kiện Blum; tổng dư của ba lô; điểm vô cực và nghịch đảo ECC; xác suất ngày sinh nhật; điều kiện nghịch đảo k trong chữ ký ElGamal. Ảnh có dấu hỏi trong sơ đồ chữ ký được giải thích vai trò và thứ tự xử lý ngay dưới hình.
- Đối chiếu trực tiếp slide 16 và sửa mô tả bài mẫu 31: **K trong hình là khóa đối xứng chung** của lớp bảo mật; PR_a/PU_a là cặp khóa người ký. Trường hợp lớp ngoài dùng mã hóa công khai được nói riêng, không gán cho hình dùng K.
- So sánh trước và sau khi Word lưu: **nội dung toàn bộ 1.344 phương trình OMML và 76 bảng giống baseline**; 70 nhãn trên dấu bằng giữ nguyên; toàn bộ 9 ảnh cũ và 66 ảnh mới khớp hash từng tệp nhúng; không dùng ảnh liên kết ngoài. Giữ 37 bài mẫu, 35 mục Casio chi tiết và chương bài tập về nhà.
- Render bản cuối bằng Word 16.0: **140 trang**, cập nhật mục lục và số trang. Kiểm tra toàn bộ qua ảnh trang; mở riêng các trang Jacobi, Merkle–Hellman và băm/xác thực để xem độ rõ, ghi chú và dấu công thức. Không phát hiện cắt mất nội dung, ảnh lấn lề hoặc chú thích rơi sang trang riêng.
- 64 tệp nguồn tiếp tục khớp SHA256. Bản trước được giữ trong thư mục QA local; chỉ thay tệp bàn giao sau khi đối chiếu hash và kiểm tra bản dựng.

Commit bàn giao được báo trong tin nhắn kết thúc; báo cáo, danh mục hình và DOCX nằm cùng commit.
