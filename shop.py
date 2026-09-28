"""
장바구니 / 주문 / 마이페이지  (담당: 장바구니·주문·마이페이지 파트)
app.py 에서  from shop import shop_bp / app.register_blueprint(shop_bp)  로 연결됨
"""
from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, jsonify, abort)
from db import get_db

shop_bp = Blueprint('shop', __name__)


# ---------- 로그인 체크 (app.py 의 login_required 와 동일, fetch 요청이면 JSON 으로 응답) ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify(ok=False, msg='로그인이 필요합니다'), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


def load_cart(conn, user_id):
    items = conn.execute('''
        SELECT c.id, c.product_id, c.size, c.quantity,
               p.name, p.price, p.image,
               p.price * c.quantity AS subtotal
        FROM cart_items c
        JOIN products p ON p.id = c.product_id
        WHERE c.user_id = ?
        ORDER BY c.id DESC
    ''', (user_id,)).fetchall()
    total = sum(r['subtotal'] for r in items)
    return items, total


# ======================================================
#  장바구니
# ======================================================
@shop_bp.route('/cart')
@login_required
def cart():
    conn = get_db()
    items, total = load_cart(conn, session['user_id'])
    conn.close()
    return render_template('cart.html', items=items, total=total)


@shop_bp.route('/cart/add', methods=['POST'])
@login_required
def cart_add():
    data = request.get_json(silent=True) or request.form
    product_id = int(data.get('product_id', 0))
    size = data.get('size', 'FREE')
    quantity = max(1, int(data.get('quantity', 1)))

    conn = get_db()
    if conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone() is None:
        conn.close()
        return jsonify(ok=False, msg='없는 상품입니다'), 404

    # 같은 상품+사이즈가 이미 있으면 수량만 더함
    conn.execute('''
        INSERT INTO cart_items (user_id, product_id, size, quantity)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, product_id, size)
        DO UPDATE SET quantity = quantity + excluded.quantity
    ''', (session['user_id'], product_id, size, quantity))
    conn.commit()
    count = conn.execute("SELECT COALESCE(SUM(quantity), 0) FROM cart_items WHERE user_id = ?",
                         (session['user_id'],)).fetchone()[0]
    conn.close()
    return jsonify(ok=True, cart_count=count)


@shop_bp.route('/cart/update', methods=['POST'])
@login_required
def cart_update():
    data = request.get_json()
    item_id, quantity = int(data['item_id']), int(data['quantity'])
    conn = get_db()
    if quantity <= 0:
        conn.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?", (item_id, session['user_id']))
    else:
        conn.execute("UPDATE cart_items SET quantity = ? WHERE id = ? AND user_id = ?",
                     (quantity, item_id, session['user_id']))
    conn.commit()
    _, total = load_cart(conn, session['user_id'])
    conn.close()
    return jsonify(ok=True, total=total)


@shop_bp.route('/cart/delete', methods=['POST'])
@login_required
def cart_delete():
    data = request.get_json()
    conn = get_db()
    conn.execute("DELETE FROM cart_items WHERE id = ? AND user_id = ?",
                 (int(data['item_id']), session['user_id']))
    conn.commit()
    _, total = load_cart(conn, session['user_id'])
    conn.close()
    return jsonify(ok=True, total=total)


# ======================================================
#  주문
# ======================================================
@shop_bp.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    user_id = session['user_id']
    conn = get_db()
    items, total = load_cart(conn, user_id)

    if not items:
        conn.close()
        return redirect(url_for('shop.cart'))

    if request.method == 'GET':
        conn.close()
        return render_template('order.html', items=items, total=total)

    receiver = request.form.get('receiver', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    if not (receiver and phone and address):
        conn.close()
        return render_template('order.html', items=items, total=total,
                               error='배송 정보를 모두 입력해주세요')

    cur = conn.execute('''
        INSERT INTO orders (user_id, total_price, receiver, phone, address)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, total, receiver, phone, address))
    order_id = cur.lastrowid

    # 주문 시점의 상품명/가격을 복사해 둠 (나중에 상품 가격이 바뀌어도 주문 내역은 그대로)
    conn.executemany('''
        INSERT INTO order_items (order_id, product_id, name, price, size, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [(order_id, r['product_id'], r['name'], r['price'], r['size'], r['quantity']) for r in items])

    conn.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))   # 장바구니 비우기
    conn.commit()
    conn.close()
    return redirect(url_for('shop.order_complete', order_id=order_id))


@shop_bp.route('/order/<int:order_id>/complete')
@login_required
def order_complete(order_id):
    conn = get_db()
    o = _get_my_order(conn, order_id)
    conn.close()
    return render_template('order_complete.html', order=o)


# ======================================================
#  마이페이지
# ======================================================
@shop_bp.route('/mypage')
@login_required
def mypage():
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    orders = conn.execute('''
        SELECT o.*,
               (SELECT COUNT(*) FROM order_items i WHERE i.order_id = o.id) AS item_count,
               (SELECT name FROM order_items i WHERE i.order_id = o.id LIMIT 1) AS first_item
        FROM orders o
        WHERE o.user_id = ?
        ORDER BY o.id DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('mypage.html', user=user, orders=orders)


@shop_bp.route('/mypage/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    conn = get_db()
    o = _get_my_order(conn, order_id)
    items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    conn.close()
    return render_template('order_detail.html', order=o, items=items)


def _get_my_order(conn, order_id):
    o = conn.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?",
                     (order_id, session['user_id'])).fetchone()
    if o is None:
        conn.close()
        abort(404)   # 남의 주문은 못 봄
    return o
