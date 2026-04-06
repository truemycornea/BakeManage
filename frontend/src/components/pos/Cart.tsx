import { useTranslation } from "react-i18next";

interface CartItem {
  product_name: string;
  quantity: number;
  unit_price: number;
}

interface CartProps {
  items?: CartItem[];
  onCheckout?: () => void;
}

export default function Cart({ items = [], onCheckout }: CartProps) {
  const { t } = useTranslation();

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);

  return (
    <div style={{ border: "1px solid #ccc", borderRadius: "8px", padding: "1rem" }}>
      <h2>{t("pos.cart")}</h2>
      {items.length === 0 ? (
        <p style={{ color: "#888" }}>{t("pos.no_items_yet")}</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left" }}>{t("pos.product")}</th>
              <th>{t("pos.quantity")}</th>
              <th>{t("pos.price")}</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={i}>
                <td>{item.product_name}</td>
                <td style={{ textAlign: "center" }}>{item.quantity}</td>
                <td style={{ textAlign: "right" }}>₹{(item.quantity * item.unit_price).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <hr />
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <strong>{t("pos.subtotal")}</strong>
        <strong>₹{subtotal.toFixed(2)}</strong>
      </div>
      <button
        onClick={onCheckout}
        disabled={items.length === 0}
        style={{ marginTop: "1rem", width: "100%", padding: "0.75rem", background: "#1a1a2e", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer" }}
      >
        {t("pos.pay_now")}
      </button>
    </div>
  );
}
