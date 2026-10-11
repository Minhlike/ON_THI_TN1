"""Build the reviewed learning bank without changing any original document."""
import csv
import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'study_app' / 'content'
OUT.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT / 'knowledge/manifest.json').read_text('utf-8'))
SHA = manifest['sources']['slide']['sha256']
assert hashlib.sha256((ROOT / 'CSATTT_SLIDE_FULL.pdf').read_bytes()).hexdigest() == SHA
assert hashlib.sha256((ROOT / manifest['sources']['outline']['file']).read_bytes()).hexdigest() == manifest['sources']['outline']['sha256']
questions = [json.loads(s) for s in (ROOT / 'knowledge/questions/questions.jsonl').read_text('utf-8').splitlines()]
primary = {q['question_id']: q for q in questions if re.fullmatch(r'TN1-Q\d{3}', q['question_id'])}
cards = []

def card(n, title, pages, answer, rubric, hints, note='', derivations=''):
    q = primary[f'TN1-Q{n:03}']
    sources = []
    for p in pages:
        raw = (ROOT / f'knowledge/slide/pages/p{p:04}.md').read_text('utf-8').split('-->', 1)[-1].strip()
        sources.append({'page': p, 'sha256': SHA, 'excerpt': raw, 'label': 'SLIDE_GROUNDED', 'visual_reviewed': True})
    items = []
    for i, label in enumerate(rubric):
        # Core definitions are essential; examples and applications are identified separately.
        items.append({'id': f'r{i+1}', 'label': label, 'essential': i == 0, 'keywords': re.findall(r'[\wÀ-ỹ]+', label.lower())[:7]})
    cards.append({'id': q['question_id'], 'title': title, 'topic': q['section_id'], 'question': q['original_text'], 'outline_page': q['pdf_page'], 'type': 'theory', 'status': 'VERIFIED_WITH_DERIVATIONS' if derivations else 'SLIDE_GROUNDED', 'answer': answer, 'rubric': items, 'hints': hints, 'sources': sources, 'note': note, 'derivations': derivations, 'difficulty': 2})

card(1, 'Hiểm họa với mạng Wi-Fi', [57,66],
 'Hiểm họa ATTT là những khả năng tác động lên thông tin hoặc hệ thống, dẫn tới thay đổi, hư hại, sao chép, ngăn cản tiếp cận hoặc làm ngừng trệ hoạt động. Hiểm họa có thể tự nhiên, vô ý hoặc có chủ ý. Với Wi-Fi của Học viện, ví dụ vận dụng: kẻ lạ đoán được mật khẩu để truy cập trái phép; điểm truy cập giả dẫn đến lộ thông tin đăng nhập; gây nhiễu hoặc mất điện làm gián đoạn truy cập. Đây là các tình huống giả định để phân tích, không phải sự cố đã được xác nhận ở Học viện.',
 ['Định nghĩa là khả năng tác động gây hại, chưa đồng nhất với một cuộc tấn công đã xảy ra.', 'Nêu ít nhất ba ví dụ cụ thể đối với hệ thống Wi-Fi.', 'Gắn ví dụ với bí mật, toàn vẹn hoặc khả dụng; phân biệt tình huống giả định với sự kiện thực tế.'],
 ['Nhớ sự khác nhau giữa một khả năng và hành vi tấn công.', 'Xét tài khoản truy cập, đường truyền và nguồn điện.'], derivations='Các ví dụ Wi-Fi là DERIVED từ định nghĩa và nhóm hiểm họa ở slide 57, 66.')
card(2, 'Định danh và xác thực', [108,110],
 'Định danh là gắn định danh cho người dùng và kiểm tra sự tồn tại của định danh đó; bước này chưa kiểm tra tính chân thực. Xác thực kiểm tra danh tính đã khai có chân thực hay không, bằng nhân tố và giao thức xác thực. Ví dụ: nhập tên tài khoản là định danh, chứng minh bằng mật khẩu là xác thực. Hai bước giúp hệ thống nhận diện đúng chủ thể, hạn chế giả mạo và hỗ trợ kiểm soát truy cập; xác thực chưa bao gồm quyết định quyền hạn.',
 ['Định danh: gắn định danh, kiểm tra sự tồn tại, chưa chứng minh danh tính.', 'Xác thực: kiểm tra tính chân thực của danh tính đã khai.', 'Nêu vai trò, ví dụ và phân biệt với việc xác định quyền hạn.'], ['Bạn khai mình là ai, rồi chứng minh điều gì?', 'Tách tên tài khoản, mật khẩu và quyền đọc tệp.'], derivations='Ví dụ đăng nhập và phần liên hệ vai trò là cách vận dụng định nghĩa slide 108, 110.')
card(3, 'Ba nhóm nhân tố xác thực', [112,113,114,115],
 'Ba nhóm chính: cái người dùng biết (mật khẩu, câu trả lời riêng tư), cái người dùng có (thẻ, smartcard, OTP token, SIM) và cái thuộc về bản thể (vân tay, khuôn mặt, võng mạc, giọng nói). Nhóm biết đơn giản, chi phí thấp nhưng có thể lộ hoặc quên. Nhóm có phù hợp kết hợp đa nhân tố, nhưng tốn chi phí và có thể mất, chiếm đoạt hoặc làm giả. Slide nêu nhóm bản thể khó làm mất/đánh cắp, nhưng chi phí cao, có thể đổi theo thể trạng và có hạn chế xác thực qua mạng. Slide còn liệt kê hành vi và vị trí là hai nhóm bổ sung.',
 ['Phân loại đúng biết, có, bản thể và ví dụ cho từng nhóm.', 'Ưu/nhược của nhóm biết và nhóm có.', 'Ưu/nhược của nhóm bản thể; nêu hai nhóm bổ sung nếu cần.'], ['Phân loại theo điều người dùng biết, sở hữu và là.', 'So sánh chi phí, lộ lọt, mất vật mang và khả năng thay đổi.'], note='Các nhận xét tuyệt đối về sinh trắc trong slide là cách diễn đạt của tài liệu; không suy ra rằng dữ liệu sinh trắc không thể bị sao chép hay hệ thống không thể bị giả mạo.')
card(4, 'Xác thực đa nhân tố', [112,118],
 'Xác thực đa nhân tố kết hợp ít nhất hai nhóm nhân tố khác nhau. Ví dụ thẻ thông minh (có) và PIN (biết); hoặc mật khẩu và OTP nhận trên thiết bị đã đăng ký. Hai mật khẩu đều thuộc nhóm biết nên chưa tạo thành đa nhân tố. Việc kết hợp giảm phụ thuộc vào một bằng chứng xác thực bị lộ.',
 ['Kết hợp ít nhất hai nhóm nhân tố khác nhau.', 'Nêu một ví dụ và xác định đúng nhóm của mỗi nhân tố.', 'Giải thích vì sao hai mật khẩu chưa phải đa nhân tố.'], ['Đếm nhóm nhân tố, không chỉ đếm số lần nhập.', 'Dùng ví dụ smartcard cùng mã PIN.'], derivations='Định nghĩa tổng hợp từ phân loại slide 112 và ví dụ slide 118; phản ví dụ hai mật khẩu là DERIVED.')
card(5, 'Mật khẩu và nguyên nhân yếu', [121,122,126,135],
 'Mật khẩu là thông tin bí mật người dùng đưa ra để qua thủ tục xác thực. Có mật khẩu một lần và dài hạn. Độ an toàn phụ thuộc độ dài, tập ký tự và cách lựa chọn/sử dụng. Mật khẩu ngắn, dễ đoán, có trong từ điển, gắn thông tin cá nhân; ghi ở nơi dễ tiếp cận, để người khác nhìn thấy hoặc chia sẻ đều làm giảm an toàn.',
 ['Định nghĩa mật khẩu là thông tin bí mật dùng cho xác thực.', 'Giải thích độ dài, tập ký tự và lựa chọn dễ đoán.', 'Nêu nguyên nhân từ hành vi sử dụng/lưu giữ/chia sẻ.'], ['Xét cả chất lượng chuỗi và cách sử dụng.', 'Nhớ từ điển, thông tin cá nhân, nhìn trộm và nơi lưu.'])
card(6, 'Hiểm họa với mật khẩu', [125,126,127,129],
 'Hiểm họa gồm dò đoán/vét cạn/từ điển; nhìn trộm hoặc bàn giao cho người khác; đánh cắp CSDL; chặn bắt dữ liệu chứa mật khẩu; bẫy chương trình và lỗi thiết kế. Công cụ có thể dựa vào từ điển hoặc thử vét cạn; đánh cắp có thể qua keylogger, sniffing, XSS, SQL Injection và lừa đảo. Khi truyền qua mạng còn có dùng lại dữ liệu bắt được, khôi phục mật khẩu, sửa thông tin và giả làm bên kiểm tra.',
 ['Nêu các nhóm dò đoán, đánh cắp và chặn bắt.', 'Nêu hiểm họa từ hành vi sử dụng, chương trình và thiết kế.', 'Phân tích ít nhất một tình huống và hậu quả thay vì chỉ liệt kê tên.'], ['Nhớ các khâu: chọn, nhập, lưu, truyền và kiểm tra.', 'Vét cạn, từ điển, keylogger và giả bên kiểm tra.'], derivations='Yêu cầu phân tích tình huống là hoạt động vận dụng từ các nhóm trên slide.')
card(7, 'Chính sách mật khẩu theo giáo trình', [131,132,133,134,135],
 'Theo slide, chính sách cần: độ dài tối thiểu và nhiều nhóm ký tự để khó dò; loại mật khẩu theo từ điển; quy định thời gian hiệu lực tối đa, tối thiểu để tránh quay lại mật khẩu cũ; hạn chế số lần thử và tăng thời gian chờ; thay mật khẩu ban đầu; lưu lịch sử mật khẩu. Slide còn nêu đổi bắt buộc theo kỳ và sinh mật khẩu tự động. Mỗi quy định phải đi kèm mục đích chống dò đoán, giảm lộ lọt hoặc tránh tái sử dụng. Khi trả lời cần phân biệt nội dung giáo trình với chính sách triển khai thực tế hiện nay.',
 ['Đề xuất độ dài/độ khó và loại mật khẩu dễ đoán, kèm ý nghĩa.', 'Hạn chế số lần thử, thời gian chờ và thời hạn/lịch sử.', 'Thay mật khẩu ban đầu; giải thích mục tiêu của các quy định.', 'Nhận diện quy định trong slide cần đối chiếu khi triển khai thực tế.'], ['Chia thành chất lượng mật khẩu, chống dò và vòng đời.', 'Đừng chỉ ghi quy định: thêm lý do chống tấn công gì.'], note='Slide 131–136 có các khuyến nghị cũ (đổi định kỳ, không tự chọn, độ dài 6–8–10). Đáp án này mô tả giáo trình; không dùng các con số đó như một chuẩn an toàn hiện hành.')
card(8, 'Quy tắc sử dụng mật khẩu', [135,136],
 'Theo slide: chọn mật khẩu đủ phức tạp, tránh từ điển và thông tin cá nhân; không ghi/lưu ở nơi dễ bị tiếp cận; không dùng một tài khoản trên nhiều hệ thống; phòng chống đánh cắp. Slide nêu thay đổi định kỳ khoảng 45 ngày, và với quản trị viên: thiết lập chính sách, định kỳ kiểm tra khả năng crack trong phạm vi hệ thống được quản lý. Cần giải thích mỗi quy tắc nhằm giảm đoán, lộ, dùng lại và đánh cắp.',
 ['Chọn đủ phức tạp, tránh từ điển/thông tin cá nhân.', 'Bảo vệ việc nhập/lưu, không dùng chung giữa nhiều hệ thống.', 'Nêu trách nhiệm quản trị và giải thích mục đích.'], ['Nhớ chọn, giữ, nhập và quản lý.', 'Gắn từng quy tắc với một nguy cơ.'], note='Đổi theo kỳ và cấm lưu trong ứng dụng là lời của slide cũ. Không suy ra mọi trình quản lý mật khẩu đều không an toàn.')
card(9, 'Xác thực lưu băm', [139,141],
 'Ban đầu Bob lưu (Alice, h(P_A)). Alice gửi (Alice, Pass); Bob tra tài khoản và tính h(Pass). Nếu h(Pass)=h(P_A), Bob chấp nhận; nếu khác thì từ chối. Khi có CSDL băm không salt, kẻ tấn công băm trước từ điển mật khẩu và đối chiếu các giá trị trong CSDL; một bảng có thể áp dụng cho nhiều tài khoản. Băm trong CSDL không bảo vệ Pass truyền trực tiếp trên đường truyền.',
 ['Điều kiện ban đầu: Alice có P_A, Bob lưu định danh và h(P_A).', 'Thông điệp Alice gửi và thao tác tra cứu/tính băm của Bob.', 'Điều kiện so sánh dẫn tới chấp nhận hoặc từ chối.', 'Cơ chế bảng băm sẵn và giới hạn bảo vệ đường truyền.'], ['Chia đáp án thành bốn ý a–d của đề.', 'Bob so sánh h(Pass) với giá trị nào đã lưu?'])
card(10, 'Xác thực có salt', [140,141],
 'Bob lưu (Alice, S_A, h(P_A || S_A)). Alice gửi định danh và Pass. Bob lấy S_A, nối Pass với salt rồi tính h(Pass || S_A), so sánh với giá trị đã lưu để chấp nhận/từ chối. Salt khác nhau khiến cùng mật khẩu có băm khác nhau; bảng băm cần được tạo theo từng salt thay vì tái dùng một bảng cho mọi tài khoản. Salt không phải khóa bí mật và không thay việc bảo vệ kênh truyền.',
 ['Bản ghi ban đầu chứa định danh, salt và băm kết hợp.', 'Đúng thứ tự nối chuỗi, băm và đối chiếu với giá trị lưu.', 'Đúng điều kiện chấp nhận/từ chối.', 'Giải thích tác dụng chống bảng dùng chung; salt không mã hóa đường truyền.'], ['Salt có mặt ở bản ghi nào và ở phép tính nào?', 'Cả hai phía của phép so sánh phải dùng cùng S_A.'], derivations='Ý nghĩa salt được suy ra từ sơ đồ slide 140; đây không phải trích nguyên văn.')
card(11, 'Lamport OTP và MITM', [142],
 'Ban đầu Alice biết P_0; Bob lưu (Alice,n,h^n(P_0)). Alice gửi định danh; Bob trả n; Alice gửi h^{n−1}(P_0). Bob băm một lần và kiểm tra với h^n(P_0). Khi đúng, Bob chấp nhận rồi cập nhật (n−1,h^{n−1}(P_0)). Với n≥2, kẻ đứng giữa đổi yêu cầu thành n−1, lấy h^{n−2}(P_0), băm được giá trị Bob đang cần và giữ giá trị dùng được cho phiên sau. Do chỉ cần băm tiến, việc không xác thực yêu cầu của Bob tạo khả năng lừa Alice.',
 ['Điều kiện ban đầu và giá trị Bob lưu.', 'Ba thông điệp đúng thứ tự và đúng số lần băm.', 'Bob băm thêm một lần, so sánh rồi giảm n/cập nhật giá trị.', 'Giải thích MITM yêu cầu chỉ số nhỏ và khả năng băm tiến.'], ['Từ h^{n−1} đi thêm một lần băm sẽ được gì?', 'Kẻ đứng giữa cần xin một giá trị sớm hơn trong chuỗi.'], derivations='Ví dụ MITM với n−1 được triển khai cụ thể từ ghi chú trên slide 142.')
card(32, 'An toàn thông tin và ví dụ', [36,37,38,39,40],
 'An toàn thông tin bảo vệ thông tin và HTTT khỏi truy nhập, sử dụng, tiết lộ, gián đoạn, sửa đổi, phá hoại trái phép để bảo đảm bí mật, toàn vẹn và khả dụng. Ví dụ hệ thống quản lý điểm: chỉ người có quyền được đọc điểm; sửa điểm phải được kiểm soát và ghi nhận; người dùng hợp lệ truy cập được khi cần. Mỗi biện pháp phải gắn với một tính chất.',
 ['Định nghĩa bảo vệ thông tin/HTTT khỏi tác động trái phép.', 'Nêu đủ bí mật, toàn vẹn, khả dụng.', 'Ví dụ một hệ thống cụ thể và biện pháp tương ứng từng tính chất.'], ['Nhớ bộ ba CIA.', 'Dùng hệ thống quản lý điểm để gắn từng tính chất.'], derivations='Ví dụ quản lý điểm là DERIVED từ ba định nghĩa.')
card(33, 'Bảy nguyên tắc bảo đảm ATTT', [68,69,71,72,73],
 'Bảy nguyên tắc: tính hệ thống (các yếu tố tương tác, biến đổi); tổng thể (đồng bộ, phòng ngự nhiều lớp); bảo vệ liên tục (suốt vòng đời); đầy đủ hợp lý (rủi ro chấp nhận được, cân đối chi phí); mềm dẻo (cho phép cập nhật); đơn giản trong sử dụng (không cản người hợp lệ); công khai thuật toán/cơ chế (biết cơ chế vẫn không vượt qua được, không có nghĩa bắt buộc công bố). Khi chọn nguyên tắc quan trọng nhất, nêu lập luận trong bối cảnh; slide không xếp hạng duy nhất.',
 ['Nêu đúng bảy nguyên tắc.', 'Giải thích nội hàm của từng nguyên tắc.', 'Chọn một nguyên tắc và lập luận có bối cảnh; không tự gán thứ hạng cho slide.'], ['Có thể nhớ bằng bảy vị trí theo thứ tự rồi tự giải thích.', 'Hệ thống, tổng thể, liên tục, hợp lý, mềm dẻo, đơn giản, công khai.'], derivations='Việc đánh giá nguyên tắc quan trọng nhất là lập luận của người học, không phải kết luận có sẵn trên slide.')
card(34, 'Sáu phương pháp bảo vệ', [75,76,77,364,365,375,378],
 'Sáu phương pháp: ngăn cản; kiểm soát truy cập; mật mã/che giấu; quy chế; cưỡng chế; giáo dục. Tường lửa áp dụng ngăn cản/kiểm soát bằng lọc lưu lượng; IDS phát hiện dấu hiệu bất thường, hỗ trợ giám sát/kiểm soát; SIEM thu thập và phân tích log tập trung để hỗ trợ phát hiện, quản lý sự kiện. Cả ba là phương tiện công nghệ; không phải một phương pháp thứ bảy hoặc biện pháp thay thế quy chế và giáo dục.',
 ['Liệt kê đúng sáu phương pháp và bản chất từng nhóm.', 'Phân biệt phương pháp với phương tiện triển khai.', 'Phân tích Firewall, IDS, SIEM dựa vào chức năng.'], ['Có ba nhóm kỹ thuật và ba nhóm tác động tới hành vi.', 'Slide 75 phân biệt cách bảo vệ và công cụ thực hiện.'], derivations='Phân lớp Firewall/IDS/SIEM là cách vận dụng từ chức năng slide 364–365,375,378 và hệ phân loại 75–77.')
card(35, 'Các lớp phương tiện', [75,78],
 'Có hai nhóm: chính tắc thực hiện chức năng theo thủ tục định trước không cần con người can thiệp trực tiếp; phi chính tắc quy định hành vi. Sơ đồ slide 75 chia chính tắc thành vật lý, phần cứng, phần mềm; phi chính tắc thành tổ chức, luật pháp, đạo đức. Ví dụ vận dụng: khóa cửa; thiết bị firewall; phần mềm chống mã độc; phân công trách nhiệm; quy định pháp luật; giáo dục ý thức trách nhiệm.',
 ['Phân biệt chính tắc và phi chính tắc.', 'Liệt kê đủ vật lý/phần cứng/phần mềm và tổ chức/luật pháp/đạo đức.', 'Ví dụ phù hợp cho mỗi lớp.'], ['Hai nhóm, mỗi nhóm có ba lớp.', 'Công cụ tự thi hành khác với quy định hành vi.'], derivations='Ví dụ cụ thể là vận dụng sơ đồ slide 75.')
card(36, 'Công nghệ, chính sách và con người', [68,69,75,77,78],
 'Công nghệ triển khai các cơ chế bảo vệ; chính sách đặt quy tắc, trách nhiệm và cách xử lý; con người xây dựng, vận hành và tuân thủ. Các yếu tố phải đồng bộ theo nguyên tắc hệ thống/tổng thể. Ví dụ: firewall cần chính sách cho phép/chặn đúng, người quản trị cập nhật luật và người dùng không chia sẻ tài khoản. Một cơ chế tốt vẫn bị giảm hiệu quả nếu quy định hoặc hành vi sử dụng yếu.',
 ['Nêu vai trò công nghệ, chính sách và con người.', 'Giải thích sự tương tác, cần đồng bộ và liên tục.', 'Ví dụ cho thấy điểm yếu của một yếu tố làm giảm hiệu quả chung.'], ['Tự hỏi: ai đặt quy tắc, công cụ nào thi hành, ai tuân thủ?', 'Dùng chính sách firewall hoặc chia sẻ mật khẩu làm ví dụ.'], derivations='Toàn bộ phần phân tích quan hệ là DERIVED từ nguyên tắc hệ thống/tổng thể và phương pháp, phương tiện trên slide; slide không có một đoạn nguyên văn đáp án cho câu này.')
card(68, 'Mạng máy tính và thành phần', [30,330,331,332],
 'Mạng máy tính liên kết các máy/thiết bị bằng kênh truyền để trao đổi dữ liệu và chia sẻ tài nguyên. Các thành phần cần trình bày: thiết bị đầu cuối/client/server; môi trường truyền và giao diện kết nối; thiết bị kết nối như switch/router; giao thức, phần mềm và dịch vụ. Sơ đồ LAN dùng switch nối client/server; WAN nối các mạng qua router; Internet liên kết nhiều mạng.',
 ['Định nghĩa liên kết thiết bị để truyền dữ liệu/chia sẻ tài nguyên.', 'Các nhóm thành phần: đầu cuối, truyền dẫn, kết nối, giao thức/phần mềm.', 'Phân biệt ví dụ LAN, WAN và Internet.'], ['Quan sát đường đi từ client qua switch tới server.', 'Vẽ bằng các nút thiết bị và đường kết nối.'], derivations='Định nghĩa mạng và cách nhóm thành phần được tổng hợp từ HTTT-TT/VT slide 30 và sơ đồ 330–332; không phải đoạn trích nguyên văn của slide.')
card(69, 'Ba tính chất của mạng an toàn', [37,38,39,40],
 'Mạng an toàn phải bảo đảm bí mật (chỉ chủ thể có thẩm quyền nhận thông tin), toàn vẹn (không bị sửa đổi trái phép/ngoài ý muốn) và khả dụng (người hợp lệ sử dụng khi cần). Ví dụ vận dụng: mã hóa và kiểm soát quyền giảm nghe lén; kiểm tra toàn vẹn phát hiện sửa đổi; dự phòng và phòng chống DoS giảm gián đoạn. Phân tích phải gắn nguyên nhân và biện pháp với từng tính chất.',
 ['Định nghĩa đúng ba tính chất CIA.', 'Phân tích nguy cơ phá vỡ mỗi tính chất.', 'Cho ví dụ cụ thể phù hợp từng tính chất.'], ['Bí mật, toàn vẹn, khả dụng.', 'Nghe lén, sửa gói tin và gây gián đoạn tương ứng với tính chất nào?'], derivations='Các biện pháp trong ví dụ là vận dụng ba định nghĩa.')
card(70, 'Phân loại hiểm họa mạng', [333,59,60,61,62,63,64],
 'Hiểm họa là khả năng tác động gây hại thông tin/HTTT. Có sáu trục phân loại: bản chất xuất hiện (tự nhiên/nhân tạo); mức độ định trước (vô ý/chủ ý); nguồn trực tiếp (con người, phần mềm hợp lệ/trái phép); vị trí nguồn sinh (ngoài, trong vùng kiểm soát, tiếp cận đầu cuối, ngay trong hệ thống); phụ thuộc hoạt động (không phụ thuộc/chỉ khi hoạt động); mức tác động (thụ động/tích cực). Một hiểm họa có thể thuộc nhiều trục. Ví dụ nghe lén chủ ý là thụ động; chỉnh sửa trái phép là tích cực.',
 ['Định nghĩa đúng hiểm họa, phân biệt với tấn công.', 'Liệt kê và giải thích đủ sáu trục phân loại.', 'Phân tích ví dụ theo nhiều tiêu chí.'], ['Đừng trộn sáu tiêu chí thành một danh sách loại duy nhất.', 'Nguồn, vị trí, ý định, hoạt động và tác động.'], derivations='Ví dụ nghe lén/sửa đổi là vận dụng phân loại slide 64.')
card(71, 'Tấn công mạng: trong và ngoài', [334,335,336,337,338],
 'Tấn công HTTT là hành vi có chủ ý của con người nhằm phá vỡ an toàn thông tin/HTTT; tấn công là một tập con của hiểm họa. Có nhiều hệ phân loại. Theo đề xuất của slide: từ trong hệ thống gồm leo thang đặc quyền, chiếm quyền điều khiển, truy cập/sao chép/phát tán trái phép; từ ngoài gồm thăm dò, chặn thu, tấn công ứng dụng/dịch vụ và DoS/DDoS. Có thể bổ sung tên trong phân loại Microsoft/CompTIA, nhưng phải nêu đang dùng hệ nào.',
 ['Định nghĩa tấn công là hành vi có chủ ý và thuộc hiểm họa.', 'Phân loại trong/ngoài cùng các nhóm hành vi.', 'Ví dụ và hậu quả, không coi các hệ phân loại là một chuẩn duy nhất.'], ['Nhớ yếu tố có chủ ý.', 'Trong: quyền và dữ liệu; ngoài: thăm dò, chặn thu, dịch vụ, từ chối.'], derivations='Phân tích hậu quả của ví dụ là vận dụng.')
card(72, 'Lỗ hổng của mạng', [52],
 'Lỗ hổng là khiếm khuyết trong chức năng/thành phần HTTT có thể bị lợi dụng gây hại. Có thể tổ chức phân tích theo nơi phát sinh: phần mềm; cấu hình/quản trị; con người/quy trình; vật lý/hạ tầng. Ví dụ luật tường lửa chưa cập nhật hoặc thiếu cơ chế hạn chế thử mật khẩu được nêu trong slide 52. Slide còn dùng ví dụ không có UPS. Nêu rõ điểm yếu, hiểm họa khai thác và hậu quả; một lỗ hổng có thể liên quan nhiều hiểm họa.',
 ['Định nghĩa là khiếm khuyết có thể bị lợi dụng.', 'Nêu cách phân loại có tiêu chí và ví dụ phù hợp.', 'Phân biệt lỗ hổng, hiểm họa và hậu quả.'], ['Điểm yếu nằm ở đâu và bị tác động bằng cách nào?', 'Slide 52 có ví dụ tường lửa và UPS.'], derivations='Cách nhóm phần mềm/cấu hình/con người/vật lý là khung phân tích DERIVED, không phải phân loại nguyên văn của slide 52.')
card(73, 'Phòng thủ theo chiều sâu', [69],
 'Phòng thủ theo chiều sâu tổ chức nhiều lớp bảo vệ thống nhất, đồng bộ để khi một lớp bị vượt qua còn các lớp khác kiểm soát/phát hiện/giảm hậu quả. Ví dụ: kiểm soát cổng mạng, firewall, phân đoạn, kiểm soát máy chủ, quyền ứng dụng, giám sát nhật ký và sao lưu. Lớp sau phải có vai trò riêng; chỉ đặt nhiều sản phẩm giống nhau chưa chứng minh hiệu quả.',
 ['Giải thích nhiều lớp bảo vệ đồng bộ theo nguyên tắc tổng thể.', 'Phân tích vai trò từng lớp và tình huống một lớp thất bại.', 'Ví dụ cụ thể gắn chức năng bảo vệ/phát hiện/khôi phục.'], ['Một lớp bị vượt qua thì lớp nào xử lý tiếp?', 'Từ biên mạng đến máy chủ, ứng dụng, dữ liệu và giám sát.'], derivations='Định nghĩa và ví dụ được triển khai từ yêu cầu phòng ngự nhiều lớp slide 69.')
card(74, 'Đề xuất an toàn cho mô hình mạng', [69,330,331,365,375,378],
 'Đọc mô hình để xác định tài sản, vùng tin cậy, điểm kết nối và dịch vụ. Đề xuất bảo vệ theo lớp: firewall ở biên với luật tối thiểu cần thiết; tách dịch vụ công khai khỏi mạng nội bộ; phân vùng người dùng/máy chủ; kiểm soát quyền, bảo vệ máy chủ; giám sát bằng IDS và tập trung log để phân tích sự kiện. Mỗi biện pháp cần nêu vị trí, lưu lượng được phép và nguy cơ giảm được. Vì đề không cho một mô hình cố định, đây là phương pháp làm bài, không phải cấu hình áp dụng cho mọi mạng.',
 ['Nhận diện tài sản, luồng dữ liệu và vùng tin cậy của mô hình được cho.', 'Đặt các biện pháp theo lớp, vị trí và quyền tối thiểu.', 'Giải thích từng biện pháp xử lý nguy cơ nào và cách giám sát.'], ['Bắt đầu từ tài sản và đường đi của dữ liệu.', 'Không liệt kê tên sản phẩm; giải thích vị trí và chức năng.'], derivations='Phương pháp làm bài và sơ đồ luyện là DERIVED; chức năng công cụ có căn cứ ở slide 365,375,378.')

rows = [
 ('Kiểm tra đầu vào', [32,2,69,1,9]), ('Năm câu lý thuyết nền tảng',[32,33,34,35,36]), ('Tổng quan mạng: câu 1–3',[68,69,70]), ('Tổng quan mạng: câu 4–7',[71,72,73,74]), ('Định danh và nhân tố xác thực',[1,2,3,4]), ('Mật khẩu và chính sách',[5,6,7,8]), ('Ba giao thức xác thực',[9,10,11]),
 ('Kiểm soát truy cập',[12,13,14,15,16]), ('Mật mã và chữ ký số',[17,18]), ('Mã độc',[19]), ('Tấn công mạng',[20]), ('Tường lửa: chức năng và phân loại',[21,75,76]), ('Tường lửa: kiến trúc và iptables',[77,78,79,80]), ('IDS/IPS và Snort',[22]),
 ('VPN, IPsec và ESP',[23]), ('SIEM và giám sát',[24]), ('Buffer Overflow: hai bài C',[25,28,29]), ('XSS và phân loại',[26,61]), ('SQL Injection: hai bài PHP',[27,30,31]), ('RSA bài 1–4',[37,38,39,40]), ('RSA bài 5–8',[41,42,43,44]),
 ('ElGamal bài 1–3',[45,46,47]), ('ECC: liệt kê điểm',[48]), ('ECC: cộng và bội điểm',[48]), ('ECC: khóa, mã hóa và giải mã',[48]), ('ECC bài 2: kiểm tra dữ kiện',[49]), ('DH và ECDH bài 1',[50,51]), ('ECDH bài 2 và luyện trộn',[52,37,45,48,50]),
 ('Truy xuất nền tảng và mạng',[32,33,34,35,36,68,69,70,71,72,73,74]), ('Xác thực và truy cập',[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]), ('Mã độc, tấn công, tường lửa',[19,20,21,75,76,77,78,79,80]), ('IDS, VPN, SIEM và sơ đồ',[22,23,24]), ('Phân tích mã nguồn trộn',[25,26,27,28,29,30,31]), ('RSA và ElGamal trộn',[37,38,39,40,41,42,43,44,45,46,47]), ('ECC, ECDH và DH trộn',[48,49,50,51,52]),
 ('Thi thử đề mẫu số 1',[53,54,55,56,57]), ('Chữa đề mẫu số 1',[53,54,55,56,57]), ('Thi thử đề mẫu số 2',[58,59,60,61,62]), ('Chữa đề mẫu số 2',[58,59,60,61,62]), ('Thi thử đề mẫu số 3',[63,64,65,66,67]), ('Chữa đề mẫu số 3',[63,64,65,66,67]), ('Kiểm tra ngẫu nhiên toàn phạm vi',list(range(1,81))),
 ('Mười câu lý thuyết trọng điểm',[32,33,2,3,9,11,13,19,21,23]), ('Tốc độ RSA và ElGamal',[37,38,39,40,41,42,43,44,45,46,47]), ('ECC/ECDH và dữ kiện thiếu',[48,49,51,52]), ('Tái hiện giao thức và mạng',[9,10,11,23,74,77]), ('Mã nguồn, Snort và iptables',[28,29,30,31,22,80]), ('Thi thử tổng hợp A',[32,9,37,28,74]), ('Chữa tổng hợp A',[32,9,37,28,74]), ('Thi thử tổng hợp B và chữa lỗi',[69,11,50,29,35]), ('Kiểm tra đầu ra và lịch duy trì',list(range(1,81)))
]
assert len(rows) == 51
plan = []
for i,(title,nums) in enumerate(rows):
    ids=[f'TN1-Q{n:03}' for n in nums]
    exam_day=i in [35,37,39,47,49]
    tasks=[{'title':'Thi tự luận không xem tài liệu; chữa vào phiên sau','minutes':180}] if exam_day else [{'title':'Ôn câu đến hạn','minutes':20},{'title':'Truy xuất chủ đề chính','minutes':45},{'title':'Luyện chuyên sâu','minutes':40},{'title':'Kiểm tra không xem đáp án','minutes':30},{'title':'Chữa lỗi và ghi lịch ôn','minutes':15}]
    plan.append({'day':i+1,'date':str(date(2026,10,12)+timedelta(days=i)),'title':title,'card_ids':ids,'minutes':180 if exam_day else 150,'phase':min(i//7+1,8),'week':min(i//7+1,8),'tasks':tasks})

bank = {'version':1,'start':'2026-10-12','end':'2026-12-01','slide_sha256':SHA,'outline_sha256':manifest['sources']['outline']['sha256'],'cards':cards,'plan':plan,'questions':list(primary.values()),'subquestions':[q for q in questions if q['question_id'] not in primary], 'reviewed_on':'2026-10-11'}
(OUT/'bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2),'utf-8')
with (OUT/'coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['id','section','outline_page','learning_status','verified_slide_pages','evidence_label','first_day','question'])
    ready={c['id'] for c in cards}
    for q in primary.values():
        days=[p['day'] for p in plan if q['question_id'] in p['card_ids']]
        c=next((c for c in cards if c['id']==q['question_id']),None)
        partial=q['question_id'] in {f'TN1-Q{n:03}' for n in [28,29,37,46,48,50,51]}
        status='REVIEWED' if c else 'PRACTICE_READY_PARTIAL' if partial else 'AWAITING_REVIEW'
        w.writerow([q['question_id'],q['section_id'],q['pdf_page'],status,';'.join(str(s['page']) for s in c['sources']) if c else '',c['status'] if c else 'DERIVED/EXTERNAL' if partial else 'UNVERIFIED',min(days) if days else '',q['original_text']])
with (OUT/'plan.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['day','date','title','minutes','question_ids'])
    for p in plan: w.writerow([p['day'],p['date'],p['title'],p['minutes'],';'.join(p['card_ids'])])
print(f'{len(primary)} primary questions, {len(cards)} reviewed cards, {len(plan)} days')
