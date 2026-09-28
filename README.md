# null-market-backend

쇼핑몰 프로젝트 - 백엔드 (Flask + SQLite)

## 기술 스택
- Python 3.12
- Flask
- SQLite

## 실행 방법

### 1. 저장소 클론
git clone https://github.com/wapapyruswasans/null-market-backend.git
cd null-market-backend

### 2. 라이브러리 설치
pip install -r requirements.txt

### 3. DB 초기화
python db.py

### 4. 서버 실행
python app.py

### 5. 접속
http://127.0.0.1:5000/login

## 현재 기능
- 회원가입 (아이디, 비밀번호, 이름, 이메일)
- 로그인 / 로그아웃
- 마이페이지 (로그인 사용자만 접근)

## 폴더 구조
- `app.py` - Flask 메인 앱 (라우트 정의)
- `db.py` - SQLite 연결 및 초기화
- `templates/` - HTML 템플릿
- `static/` - CSS/JS (예정)

## 브랜치 규칙
- `main` - 안정 버전
- `feature/기능명` - 새 기능 개발

## 장바구니 / 주문 / 마이페이지 (feature/cart-order-mypage)
- `shop.py` - 장바구니·주문·마이페이지 라우트 (Blueprint)
- `templates/base.html` - 공통 레이아웃 (헤더/네비). 새 페이지는 `{% extends "base.html" %}` 로 작성
- `static/css/shop.css`, `static/js/cart.js`
- 상품 페이지에서 담기 버튼: `static/js/add-to-cart.js` 의 `addToCart(상품id, 사이즈)` 호출

| URL | 설명 |
|---|---|
| `/cart` | 장바구니 |
| `/cart/add` (POST JSON) | 담기 `{product_id, size, quantity}` |
| `/order` | 주문서 → 결제 → `/order/<id>/complete` |
| `/mypage` | 내 정보 + 주문 내역 |
| `/mypage/orders/<id>` | 주문 상세 |

※ DB 테이블이 추가되었으므로 pull 후 `python db.py` 를 한 번 다시 실행하세요.
