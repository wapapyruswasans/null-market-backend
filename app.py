import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-later'

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if user is None or not check_password_hash(user['password_hash'], password):
        return "아이디 또는 비밀번호가 틀렸습니다", 401

    # 로그인 성공
    session['user_id'] = user['id']
    session['username'] = user['username']

    return f"{user['name']}님, 로그인 성공"

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    password_confirm = request.form.get('passwordConfirm')
    name = request.form.get('name')
    email = request.form.get('email')

    # 서버 쪽 검증 (JS 우회 대비)
    if password != password_confirm:
        return "비밀번호가 일치하지 않습니다", 400

    # 비밀번호 해시
    password_hash = generate_password_hash(password)

    # DB 저장
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password_hash, name, email) VALUES (?, ?, ?, ?)",
            (username, password_hash, name, email)
        )
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return "이미 존재하는 아이디 또는 이메일입니다", 400

    return f"{name}님, 회원가입 완료"

@app.route('/mypage')
@login_required
def mypage():
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session['user_id'],)
    ).fetchone()
    conn.close()

    return f"""
    <h2>마이페이지</h2>
    <p>아이디: {user['username']}</p>
    <p>이름: {user['name']}</p>
    <p>이메일: {user['email']}</p>
    <p>가입일: {user['created_at']}</p>
    <a href="/logout">로그아웃</a>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)