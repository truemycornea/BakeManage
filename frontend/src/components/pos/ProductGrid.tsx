import { useTranslation } from "react-i18next";

const SAMPLE_PRODUCTS = [
  { id: 1, name: "White Bread", price: 45, hsn: "1905" },
  { id: 2, name: "Croissant", price: 30, hsn: "1905" },
  { id: 3, name: "Chocolate Cake", price: 250, hsn: "1806" },
  { id: 4, name: "Barfi (500g)", price: 180, hsn: "1704" },
  { id: 5, name: "Coconut Ladoo", price: 120, hsn: "1704" },
  { id: 6, name: "Whole Wheat Bread", price: 55, hsn: "1905" },
];

interface ProductGridProps {
  onAddToCart?: (product: { product_name: string; unit_price: number; hsn_code: string }) => void;
}

export default function ProductGrid({ onAddToCart }: ProductGridProps) {
  const { t } = useTranslation();

  return (
    <div>
      <h2>{t("pos.add_item")}</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.75rem" }}>
        {SAMPLE_PRODUCTS.map((p) => (
          <button
            key={p.id}
            onClick={() => onAddToCart?.({ product_name: p.name, unit_price: p.price, hsn_code: p.hsn })}
            style={{
              padding: "1rem",
              border: "1px solid #ddd",
              borderRadius: "8px",
              background: "#fff",
              cursor: "pointer",
              textAlign: "left",
            }}
          >
            <div style={{ fontWeight: "bold" }}>{p.name}</div>
            <div style={{ color: "#555" }}>₹{p.price}</div>
            <div style={{ fontSize: "0.75rem", color: "#999" }}>HSN: {p.hsn}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
