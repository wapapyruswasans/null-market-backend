// 장바구니: 수량 +/- 와 삭제를 새로고침 없이 처리 (shop.py 의 /cart/update, /cart/delete 와 JSON 통신)
async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}
const won = (n) => n.toLocaleString("ko-KR") + "원";

document.querySelectorAll(".cart-table tbody tr").forEach((row) => {
  const itemId = Number(row.dataset.itemId);
  const qtyEl = row.querySelector(".qty");
  const subtotalEl = row.querySelector(".subtotal");
  const price = Number(subtotalEl.dataset.price);

  row.querySelectorAll(".qty-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const newQty = Number(qtyEl.textContent) + Number(btn.dataset.delta);
      if (newQty < 1) return;
      const data = await postJSON("/cart/update", { item_id: itemId, quantity: newQty });
      if (!data.ok) return alert(data.msg || "오류가 났어요");
      qtyEl.textContent = newQty;
      subtotalEl.textContent = won(price * newQty);
      document.getElementById("cart-total").textContent = data.total.toLocaleString("ko-KR");
    });
  });

  row.querySelector(".delete-btn").addEventListener("click", async () => {
    if (!confirm("삭제할까요?")) return;
    const data = await postJSON("/cart/delete", { item_id: itemId });
    if (!data.ok) return alert(data.msg || "오류가 났어요");
    row.remove();
    document.getElementById("cart-total").textContent = data.total.toLocaleString("ko-KR");
    if (!document.querySelector(".cart-table tbody tr")) location.reload();
  });
});
