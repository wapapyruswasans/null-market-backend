// 상품 목록/상세 페이지에서 사용:  <script src="/static/js/add-to-cart.js"></script>
// 버튼 예시:  <button onclick="addToCart(3)">장바구니 담기</button>
// 사이즈 선택이 있으면:  addToCart(3, document.querySelector('select[name=size]').value)
async function addToCart(productId, size = "FREE", quantity = 1) {
  const res = await fetch("/cart/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_id: productId, size, quantity }),
  });
  if (res.status === 401) { alert("로그인이 필요해요"); location.href = "/login"; return; }
  const data = await res.json();
  if (data.ok) {
    if (confirm(`장바구니에 담았어요! (총 ${data.cart_count}개)\n장바구니로 이동할까요?`)) location.href = "/cart";
  } else {
    alert(data.msg || "담기에 실패했어요");
  }
}
