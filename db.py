import sqlite3

DB_PATH = 'users.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---------- 상품 (상품 목록 담당이 컬럼을 늘려도 됨. id/name/price/image 는 유지) ----------
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image TEXT,
            description TEXT
        )
    ''')

    # ---------- 장바구니 / 주문 ----------
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            size TEXT NOT NULL DEFAULT 'FREE',
            quantity INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, product_id, size)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            receiver TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT '결제완료',
            created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            size TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # 테스트용 샘플 상품 (상품이 하나도 없을 때만 넣음)
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
            [("오버핏 후드티", 39000, None),
             ("와이드 데님 팬츠", 49000, None),
             ("베이직 반팔 티셔츠", 19000, None)]
        )

    conn.commit()
    conn.close()
    print("DB 초기화 완료")

if __name__ == '__main__':
    init_db()
