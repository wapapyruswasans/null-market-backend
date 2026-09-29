import sqlite3

DB_PATH = 'users.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # ---------- 유저 ----------
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

    # ---------- 상품 ----------
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

    # ---------- 태그 ----------
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS product_tags (
            product_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (product_id, tag_id)
        )
    ''')

    # ---------- 사용자 프로필 (추천용) ----------
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            height INTEGER,
            weight INTEGER,
            preferred_tags TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---------- 찜 목록 (추천용) ----------
    conn.execute('''
        CREATE TABLE IF NOT EXISTS wishlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, product_id)
        )
    ''')

    # ---------- 샘플 상품 (상품이 하나도 없을 때만) ----------
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
            [("오버핏 후드티", 39000, None),
             ("와이드 데님 팬츠", 49000, None),
             ("베이직 반팔 티셔츠", 19000, None)]
        )

    # ---------- 태그 마스터 데이터 (한 번만) ----------
    tags = [
        "color-black", "color-white", "color-red", "color-blue",
        "color-green", "color-yellow", "color-pink", "color-gray", "color-beige",
        "style-casual", "style-formal", "style-sporty", "style-minimal",
        "style-street", "style-vintage",
        "type-shirt", "type-hoodie", "type-pants", "type-skirt",
        "type-dress", "type-jacket", "type-coat", "type-shoes", "type-bag",
        "type-knit", "type-sweatshirt", "type-hat",              # ← 추가
        "season-spring", "season-summer", "season-fall", "season-winter", "season-all",
        "fit-oversize", "fit-slim", "fit-regular", "fit-wide",
        "gender-men", "gender-women", "gender-unisex",
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO tags (name) VALUES (?)",
        [(t,) for t in tags]
    )

    # ---------- 샘플 상품에 태그 달기 ----------
    tag_map = {
        "오버핏 후드티": ["color-black", "style-casual", "type-hoodie", "season-fall", "fit-oversize", "gender-unisex"],
        "와이드 데님 팬츠": ["color-blue", "style-casual", "type-pants", "season-all", "fit-wide", "gender-unisex"],
        "베이직 반팔 티셔츠": ["color-white", "style-minimal", "type-shirt", "season-summer", "fit-regular", "gender-unisex"],
    }
    for p in conn.execute("SELECT id, name FROM products").fetchall():
        for tag_name in tag_map.get(p['name'], []):
            conn.execute('''
                INSERT OR IGNORE INTO product_tags (product_id, tag_id)
                SELECT ?, id FROM tags WHERE name = ?
            ''', (p['id'], tag_name))

    conn.commit()
    conn.close()
    print("DB 초기화 완료")

if __name__ == '__main__':
    init_db()