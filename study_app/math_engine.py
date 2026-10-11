"""Small, exact integer exercises. No floating point cryptographic arithmetic."""
from math import gcd, isqrt


def integer(value):
    text = str(value).strip()
    if len(text) > 10 or not text.lstrip('-').isdigit():
        raise ValueError('Nhập số nguyên nhỏ (tối đa 10 chữ số).')
    return int(text)


def prime(n):
    return 2 <= n <= 10000 and all(n % d for d in range(2, isqrt(n) + 1))


def inv(a, n):
    if n <= 1 or gcd(a, n) != 1:
        raise ValueError('Không tồn tại nghịch đảo với môđun này.')
    return pow(a, -1, n)


def modpow_steps(a, exponent, modulus):
    result, steps = 1, []
    for bit in bin(exponent)[2:]:
        before = result
        result = result * result % modulus
        if bit == '1':
            result = result * a % modulus
        steps.append(f'Bit {bit}: bình phương {before}, ' + ('nhân cơ số, ' if bit == '1' else '') + f'lấy mod {modulus} → {result}')
    return result, steps


def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    slope = ((3*x1*x1+a)*inv(2*y1, p) if P == Q else (y2-y1)*inv(x2-x1, p)) % p
    x3 = (slope*slope-x1-x2) % p
    return (x3, (slope*(x1-x3)-y1) % p)


def mul(k, P, a, p):
    if k < 0: return mul(-k, (P[0], -P[1] % p), a, p)
    R = None
    while k:
        if k & 1: R = add(R, P, a, p)
        P = add(P, P, a, p); k //= 2
    return R


def point_text(P):
    return 'O' if P is None else f'({P[0]},{P[1]})'


PRESETS = {
    'rsa': {'title':'RSA · Đề cương bài 1', 'question_id':'TN1-Q037', 'page':10, 'values':{'p':17,'q':31,'e':7,'m':32}, 'fields':['p','q','e','m'], 'target':'Bản mã C', 'formula':r'n=pq,\quad \varphi(n)=(p-1)(q-1),\quad ed\equiv1\pmod{\varphi(n)},\quad C=M^e\bmod n', 'source':'EXTERNAL · RFC 8017 §5.1; DERIVED · phép tính từ dữ kiện đề.', 'url':'https://www.rfc-editor.org/rfc/rfc8017.html#section-5.1'},
    'elgamal': {'title':'ElGamal · Đề cương bài 2', 'question_id':'TN1-Q046','page':11, 'values':{'p':211,'g':39,'x':113,'k':23,'m':34}, 'fields':['p','g','x','k','m'], 'target':'C1,C2 (hai số cách bởi dấu phẩy)', 'formula':r'y=g^x\bmod p,\quad C_1=g^k\bmod p,\quad C_2=M y^k\bmod p', 'source':'EXTERNAL · Handbook of Applied Cryptography §8.4; DERIVED · phép tính từ đề.', 'url':'https://cacr.uwaterloo.ca/hac/about/chap8.pdf'},
    'dh': {'title':'Diffie–Hellman · Đề cương bài 1', 'question_id':'TN1-Q050','page':12,'values':{'p':11,'g':2,'a':4,'b':7},'fields':['p','g','a','b'],'target':'Khóa chung K','formula':r'Y_A=g^a\bmod p,\quad Y_B=g^b\bmod p,\quad K=Y_B^a=Y_A^b\bmod p','source':'EXTERNAL · RFC 2631 §2.1.1; DERIVED · phép tính từ đề. Slide 178 minh họa nguyên lý trao đổi khóa.','url':'https://www.rfc-editor.org/rfc/rfc2631.html#section-2.1.1'},
    'ecc': {'title':'ECC · Đề cương bài 1','question_id':'TN1-Q048','page':12,'values':{'p':11,'a':1,'b':6,'gx':2,'gy':7,'k':6},'fields':['p','a','b','gx','gy','k'],'target':'kG: nhập x,y hoặc O','formula':r'\begin{aligned}y^2&\equiv x^3+ax+b\pmod p\\\lambda&=(y_2-y_1)(x_2-x_1)^{-1}\quad(P\ne Q)\\\lambda&=(3x_1^2+a)(2y_1)^{-1}\quad(P=Q)\\x_3&=\lambda^2-x_1-x_2\\y_3&=\lambda(x_1-x_3)-y_1\end{aligned}','source':'EXTERNAL · SEC 1 v2 §2.2.1; DERIVED · điểm và bội điểm tính từ đề. Các phép tính tọa độ lấy mod p; nghịch đảo chỉ dùng khi mẫu khác 0.','url':'https://www.secg.org/sec1-v2.pdf'},
    'ecdh': {'title':'ECDH · Đề cương bài 1','question_id':'TN1-Q051','page':12,'values':{'p':11,'a':1,'b':6,'gx':2,'gy':7,'ka':3,'kb':5},'fields':['p','a','b','gx','gy','ka','kb'],'target':'Khóa chung: nhập x,y hoặc O','formula':r'Q_A=k_A G,\quad Q_B=k_B G,\quad S=k_AQ_B=k_BQ_A','source':'EXTERNAL · SEC 1 v2 §3.3.1; DERIVED · phép tính từ dữ kiện đề.','url':'https://www.secg.org/sec1-v2.pdf'},
}


def calculate(kind, values):
    if kind not in PRESETS: raise ValueError('Chọn một thuật toán có trong danh sách.')
    v = {key:integer(values[key]) for key in PRESETS[kind]['fields']}
    steps, points, selected = [], [], None
    if kind == 'rsa':
        p,q,e,m = (v[key] for key in ['p','q','e','m'])
        if not prime(p) or not prime(q) or p == q: raise ValueError('p, q phải là hai số nguyên tố khác nhau, không quá 10000.')
        n=p*q; phi=(p-1)*(q-1)
        if not 1 < e < phi or gcd(e,phi) != 1: raise ValueError('Cần 1 < e < φ(n) và gcd(e,φ(n))=1.')
        if not 0 <= m < n: raise ValueError('Thông điệp số cần nằm trong [0,n).')
        d=inv(e,phi); c,trace=modpow_steps(m,e,n)
        steps=[f'n={p}×{q}={n}; φ(n)={phi}',f'gcd({e},{phi})=1; d={d}; e×d mod φ(n)={e*d%phi}',*trace,f'C={c}; giải mã C^d mod n={pow(c,d,n)}']
        expected=str(c)
    elif kind in ('elgamal','dh'):
        p,g=v['p'],v['g']
        if not prime(p) or not 1 < g < p: raise ValueError('p phải nguyên tố ≤10000 và 1 < g < p.')
        order=next(i for i in range(1,p) if pow(g,i,p)==1)
        steps=[f'Bậc của g={g} trong nhóm là {order} (p−1={p-1}).']
        if order != p-1: steps.append('Lưu ý: g không sinh toàn bộ nhóm nhân; giữ nguyên dữ kiện và ghi nhận giới hạn này.')
        if kind == 'elgamal':
            x,k,m=v['x'],v['k'],v['m']
            if not 1 <= x <= p-2 or not 1 <= k <= p-2 or not 0 < m < p: raise ValueError('Cần 1≤x,k≤p−2 và 0<M<p. Bài thiếu k chưa có bản mã duy nhất.')
            y=pow(g,x,p); c1=pow(g,k,p); shared=pow(y,k,p); c2=m*shared%p
            steps += [f'y=g^x mod p={y}',f'C1=g^k mod p={c1}',f's=y^k mod p={shared}; C2=M×s mod p={c2}',f'Giải mã C2×(C1^x)⁻¹ mod p={c2*inv(pow(c1,x,p),p)%p}']
            expected=f'{c1},{c2}'
        else:
            a,b=v['a'],v['b']
            if not 1 <= a < p-1 or not 1 <= b < p-1: raise ValueError('Số mũ bí mật phải thuộc [1,p−2].')
            ya,yb=pow(g,a,p),pow(g,b,p); shared=pow(yb,a,p)
            steps += [f'YA={g}^{a} mod {p}={ya}',f'YB={g}^{b} mod {p}={yb}',f'A tính YB^a mod p={shared}; B tính YA^b mod p={pow(ya,b,p)}']
            expected=str(shared)
    else:
        p,a,b,gx,gy=(v[key] for key in ['p','a','b','gx','gy'])
        if not prime(p) or p <= 3 or p > 101: raise ValueError('Đồ thị trường hữu hạn cần p nguyên tố, 3<p≤101. Đề ghi mod 1 không tạo trường; không tự sửa thành 11.')
        if (4*a*a*a+27*b*b)%p == 0: raise ValueError('Đường cong suy biến: Δ=0 mod p.')
        if not 0 <= gx < p or not 0 <= gy < p or (gy*gy-gx**3-a*gx-b)%p: raise ValueError('G phải là điểm trên đường cong với tọa độ trong [0,p).')
        G=(gx,gy); points=[(x,y) for x in range(p) for y in range(p) if (y*y-x**3-a*x-b)%p==0]
        order=1; cur=G
        while cur is not None:
            cur=add(cur,G,a,p); order+=1
        steps=[f'{len(points)} điểm hữu hạn và O; bậc G={order}.']
        if kind == 'ecc':
            k=v['k']
            if not 1 <= k <= 100: raise ValueError('Chọn 1≤k≤100 để quan sát các bước.')
            cur=None
            for i in range(1,k+1):
                if cur is not None and (cur[0]!=gx or (cur[1]+gy)%p!=0):
                    numerator,denominator=(3*cur[0]**2+a,2*cur[1]) if cur==G else (gy-cur[1],gx-cur[0])
                    inverse=inv(denominator,p); slope=numerator*inverse%p
                    steps.append(f'({i-1}G)+G: mẫu={denominator%p}, nghịch đảo={inverse}, λ={numerator%p}×{inverse} mod {p}={slope}')
                elif cur is not None:
                    steps.append(f'{i-1}G và G đối nhau → O.')
                cur=add(cur,G,a,p); steps.append(f'{i}G={point_text(cur)}')
            selected=cur; expected=point_text(cur)
        else:
            ka,kb=v['ka'],v['kb']
            if not 1 <= ka < order or not 1 <= kb < order: raise ValueError(f'Khóa bí mật phải nằm trong [1,{order-1}].')
            qa,qb=mul(ka,G,a,p),mul(kb,G,a,p); selected=mul(ka,qb,a,p)
            steps += [f'QA={ka}G={point_text(qa)}',f'QB={kb}G={point_text(qb)}',f'KA×QB={point_text(selected)}; KB×QA={point_text(mul(kb,qa,a,p))}']
            expected=point_text(selected)
    return {'expected':expected,'steps':steps,'points':points,'selected':selected,'values':v}


def normalized_answer(value):
    return str(value).replace(' ','').replace('(','').replace(')','').upper()
