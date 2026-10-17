# Kiểm toán nội dung cuối giáo trình Toán mật mã

Ngày 17/10/2026 · Nhánh `codex/week1-offline-study` · Baseline `acea81ef155abb34104dd6034fc2d66f8aa0f943`.

## Kết luận

Đã rà **37 bài mẫu, 69 đáp án tự luyện và 7 bài về nhà**. Trong phạm vi kiểm tra được mô tả dưới đây, không còn lỗi toán học đã biết. Đã sửa **hai lỗi ghi số mũ FACT**, **một diễn giải Casio sai ngữ cảnh**, bổ sung **bốn vị trí thiếu dữ kiện, điều kiện hoặc bước lập luận** và mở rộng **24 mục Casio**.

Bản nội dung sẵn sàng cho một đợt tối ưu bố cục riêng. Đợt này không đổi font, hệ thống heading, bảng gốc, hình slide hoặc phương pháp của giảng viên.

- Tệp học chính: `co_so_matmahoc/toan_matma.docx` — **144 trang, 1.360 công thức OMML, 70 limUpp, 76 bảng, 75 ảnh**.
- [PDF xuất trực tiếp bằng Word 2016](TOAN_MATMA_WORD2016.pdf) để kiểm toán hiển thị. Người học vẫn có toàn bộ nội dung và hình trong một tệp Word.
- [Danh mục 113 đơn vị kiểm toán và thay đổi cụ thể](TOAN_MATMA_FINAL_CONTENT_AUDIT.json).

## Ma trận nghiệm thu

| Hạng mục | Đã kiểm tra | Lỗi thực sự | Đã sửa | Chưa xác minh |
|---|---|---|---|---|
| OMML trên Word 2016 | PDF 144 trang, ký tự toán theo từng trang, ảnh trang, native Equation và khả năng chỉnh sửa | Không tái hiện mất công thức trên Word | Giữ nguyên 1.344 công thức cũ; 16 biểu thức mới dùng OMML | Không tái hiện độc lập lỗi LibreOffice |
| 37 bài mẫu | Dữ kiện, phương pháp, điều kiện, bước trung gian, bảng, kết quả và phép thử hoặc chứng minh | Không phát hiện đáp số chính sai; hai số mũ FACT bị ghi sai | Sửa hai số mũ và bổ sung các bước cần thiết | Không dùng thử số thay cho chứng minh tổng quát |
| 69 đáp án tự luyện | Đủ 37 câu T và 32 câu B; ghép từng câu với đáp án, kiểm các tập nghiệm và phép thử | T32 chưa kiểm rõ biệt thức trước bảng | Thêm kiểm tra 19 nguyên tố và biệt thức khác 0 | Câu lý thuyết được rà bằng định nghĩa và sơ đồ, không gán nhãn Python chứng minh |
| 7 bài về nhà | Giữ dữ kiện ảnh; kiểm từng hàng bảng và mọi phép cộng/nhân đôi ECC | Không phát hiện lỗi đáp số mới | Bổ sung chu trình máy ở cả 7 bài | Dữ kiện MH có modulo nhỏ hơn tổng vẫn giữ và cảnh báo |
| 35 mục Casio chi tiết | Chế độ, phím, vòng lặp, nguồn, giới hạn và phép tính dự kiến | Hai lỗi FACT; một diễn giải lẫn với Euler; nhiều mục thiếu chu trình | Sửa 3 vị trí và mở rộng 24 mục | Chưa thử trên máy vật lý hoặc trình giả lập |
| Bảo toàn nội dung | Đủ 27 dạng, 37 bài mẫu, 69 đáp án, 7 bài nhà và 35 mục Casio; nguồn, hình, bảng và styles | Không phát hiện nội dung bị bỏ | Không thiết kế lại hình thức | Word cập nhật mục lục và phân trang do nội dung dài hơn |

## Lỗi trước và sau

| Vị trí | Trước | Sau | Kiểm chứng |
|---|---|---|---|
| Casio bài mẫu 14 | FACT 9975 ghi `3·52·7·19` | 3·5²·7·19, viết bằng OMML | 3·25·7·19 = 9975 |
| Casio bài mẫu 15 | FACT 2032 ghi `24·127` | 2⁴·127, viết bằng OMML | 16·127 = 2032 |
| Casio bài mẫu 11 | Lập bảng x² modulo 17 nhưng yêu cầu so số dư với 1 hoặc p−1 như tiêu chuẩn Euler | Ghép các số dư thành Q₁₇ rồi kiểm tư cách thuộc tập | Q₁₇ = {1,2,4,8,9,13,15,16}; tiêu chuẩn Euler dùng số mũ (p−1)/2 |

**Số lỗi toán học được sửa:** hai lỗi ký hiệu số mũ trong phần kết quả máy. **Số diễn giải thao tác được sửa:** một. Không có đáp số cuối nào của 37 bài mẫu, 69 đáp án hoặc 7 bài về nhà phải thay trong đợt này. Các lỗi slide đã được chú giải từ đợt trước không được tính lại là lỗi mới.

## Bốn vị trí bổ sung dữ kiện điều kiện và lập luận

1. **Bài mẫu 6:** giải thích tạo các bình phương nhỏ và ghép mũ trước khi dùng bảng bit ở Dạng 5. Người học không cần biết trước thuật toán ở Dạng 6.
2. **Bài mẫu 27:** ghi rõ yêu cầu mã hóa `101101` rồi giải mã; kiểm từng bất đẳng thức siêu tăng, tổng 609 < 737 và UCLN qua bảng. Đối chiếu Chương 3, trang PDF 22, slide 128: đề thực sự cho bản tin `101101` và yêu cầu giải mã ngược lại.
3. **T32:** kiểm 19 nguyên tố và 4·1³ + 27·1² = 31, dư 12 khác 0, trước khi liệt kê điểm.
4. **Bài mẫu 30:** nhắc nhóm có 13 điểm, G khác O nên cấp 13; khóa 7 và số ngẫu nhiên 3 nằm trong khoảng 1 đến 12.

## Hoàn thiện Casio

Các mục mở rộng: **H01, H02, H03, H04, H05, H06, H07, M04, M06, M11, M13, M16, M17, M18, M20, M21, M22, M24, M25, M27, M28, M30, M35, M37**. M là số bài mẫu; H là số bài về nhà. Các mã này chỉ có trong báo cáo, không thêm mã tra cứu vào giáo trình.

- **BSGS:** tạo hệ số 31⁻⁸, dựng bảng nhỏ từ 1 và 31, bảng lớn từ 45, tìm lần gặp và tính 26; giải thích cách dùng dư mới ở lần nhập kế tiếp.
- **Euclid mở rộng:** nhập cả x và y khi có hệ số âm, rồi chuyển đúng trạng thái sang hàng sau.
- **Tìm căn:** có chu trình A/b của TT1, tính d = 52 của TT2 và trọn một vòng r/c/d của TT4 trước khi lặp.
- **RSA, ElGamal, chữ ký và bài nhà:** có chu trình bình phương A, cập nhật hoặc giữ b theo bit và đầu vào kế tiếp; không chỉ thử cột đầu/cuối.
- **ECC:** hoàn chỉnh tử, nghịch đảo, lambda, x₃ và y₃; chuẩn hóa số âm bằng cộng bội modulo. Phép trừ điểm dùng điểm đối.
- Giữ lập luận trên giấy. Không dùng nghịch đảo số thực thay nghịch đảo modulo. Dùng ngoặc khi lấy ÷R của cả tổng hoặc hiệu; không dùng Ans làm số dư ngay sau ÷R.

Đối chiếu [hướng dẫn đúng fx-580VN X](https://support.casio.com/global/vi/fx/manual/fx-580VNX/), gồm [÷R](https://support.casio.com/global/vi/fx/manual/fx-580VNX_VI/basic_calculations/remainder_calculations.html), [FACT](https://support.casio.com/global/vi/fx/manual/fx-580VNX_VI/basic_calculations/prime_factorization.html), [CALC](https://support.casio.com/global/vi/fx/manual/fx-580VNX_VI/function_calculations/using_calc/), [Table](https://support.casio.com/global/vi/fx/manual/fx-580VNX_VI/using_calculation_modes/creating_number/) và [giới hạn](https://support.casio.com/global/vi/fx/manual/fx-580VNX_VI/technical_informatoin/calculation_ranges/calculation_ranges.html). Đã mở hình phím và cài đặt trong PDF chính thức, gồm chọn Table một hàm ở trang PDF 16. Giá trị màn hình là **dự kiến đã kiểm số độc lập**, chưa phải kết quả thử máy vật lý.

## Phạm vi kiểm tra độc lập

- **735 kiểm tra số và bảng:** 11 bảng Euclid mở rộng, 43 bảng nhân bình phương, 3 CRT, 2 TT4, 5 ba lô, 2 khóa MH, 2 căn Rabin, 2 liệt kê ECC, các bảng cấp/lũy thừa và mốc bài mẫu/bài nhà. Kiểm từng trường q/r/hệ số hoặc bit/A/b, không chỉ hàng cuối.
- **666 đẳng thức và đồng dư số từ OMML**, dùng số nguyên và hữu tỉ chính xác. Jacobi được tính theo ý nghĩa ký hiệu, không coi là phân số thường. Công thức ký hiệu tổng quát được rà điều kiện và lập luận riêng.
- **352 kiểm tra mở rộng:** đủ 70 nhãn Jacobi theo phép đổi của TC1–TC4/định nghĩa; hai bảng BSGS từng ô; 32 phép ECC được dựng lại từ hai điểm, tử/mẫu, nghịch đảo, hệ số góc và tọa độ; ghép 69 cặp câu–đáp án; kiểm đầy đủ tập phần tử sinh, căn và vector ba lô.
- **234 kiểm tra phép tính trong chuỗi phím**, cùng 162 chuỗi ÷R đã kiểm dấu ngoặc và độ ưu tiên. Bảy chuỗi có trạng thái hoặc chức năng đặc biệt được đối chiếu riêng với tài liệu và giá trị độc lập; không gộp thành số thao tác thực nghiệm.
- Các lượt có phạm vi giao nhau; không cộng chúng thành số bài độc lập. Không còn kiểm tra tự động thất bại.

## Hiển thị và chỉnh sửa trên Word 2016

Máy cài Microsoft Office Professional Plus 2016. `WINWORD.EXE` xác nhận **Microsoft Office 2016, phiên bản 16.0.4756.1000**. PDF được tạo bằng chính Word trên Windows.

1. Mở baseline và xuất PDF; kiểm trực tiếp các trang 3, 4, 7, 24, 28, Jacobi và ECC. Các công thức chia Euclid, Fermat, lời giải, bảng và dữ kiện CRT đều hiển thị. Không tái hiện lỗi trắng trên Word; không sửa tương thích LibreOffice.
2. Word nhận và BuildUp được **1.344 phương trình cũ** trên bản sao thử nghiệm. Đã chỉnh một phương trình đang có từ a = nq + r thành b = nq + r bằng native Equation trên bản sao không lưu. **16 biểu thức mới** cũng qua BuildUp và phép thử chỉnh một biểu thức mới. Không ghi các thay đổi thử nghiệm vào tệp học.
3. Bản cuối có **1.360 phương trình Word**. Đối chiếu **15,174 ký tự toán ở 129 trang có phương trình** với lớp chữ Cambria/Cambria Math trong PDF, sau chuẩn hóa ký tự tương đương: không có trang thiếu ký tự. Kiểm đa tập ký tự chỉ xác nhận sự hiện diện; không thay kiểm toán ý nghĩa và kiểm tra ảnh trang.
4. Rà toàn bộ 144 ảnh trang; mở riêng các trang công thức và chuỗi máy quan trọng. Nhãn Jacobi nằm trên dấu bằng, dấu âm trong biểu thức. Không thấy cắt mất dữ kiện hoặc tràn công thức. Mục lục và số trang đã cập nhật.

## Bảo toàn và giới hạn

- Giữ nguyên nội dung **1.344 OMML cũ theo đúng thứ tự**. Thêm 16 biểu thức native cho kết quả FACT, điều kiện và lũy thừa trong giải thích.
- **76 bảng** giữ nội dung và định dạng. Khi so XML chỉ bỏ qua metadata Word rsid/paraId/textId và cache lastRenderedPageBreak. **75 ảnh nhúng** khớp hash toàn bộ; không thay ảnh slide. Styles và heading giữ nguyên; **64 tệp nguồn** tiếp tục khớp SHA256.
- Chưa thử Casio vật lý, trình giả lập hoặc một bản Word 2016 khác. Không coi kết quả trên máy này là kiểm chứng mọi bộ hiển thị DOCX. Không sửa công thức đang hợp lệ chỉ vì LibreOffice có triệu chứng khác.
- Hai nhận xét ngoài slide vẫn được giới hạn đúng nguồn: [NIST FIPS 202 ban hành tháng 8/2015](https://csrc.nist.gov/pubs/fips/202/final); [bài gốc của Shamir về phá hệ MH cơ bản](https://ieeexplore.ieee.org/abstract/document/4568386/). Không biến chúng thành khuyến nghị triển khai mật mã thực tế.

## Dấu vân tay bàn giao

- DOCX: `4bced2ea03d0f8a6ca9d51ebaf5716379145ea4f12bcc4187e9224566db2c746`.
- PDF Word 2016: `7ac3e0f9553f591d7e3fd06659ce085cd3c74846421953eb16fc357fc61839e2`.
- Baseline: `123eefd939a5769d0e003b345014544c636eb8a0bac76e0179f05fd6bcd973d4`.

Dừng sửa nội dung sau mốc này. Chỉ chuyển sang tối ưu bố cục khi có yêu cầu riêng.
