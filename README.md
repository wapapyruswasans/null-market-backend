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
