import { useTranslation } from "react-i18next";
import Cart from "../components/pos/Cart";
import ProductGrid from "../components/pos/ProductGrid";

export default function POS() {
  const { t } = useTranslation();
  return (
    <div>
      <h1>{t("pos.title")}</h1>
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1rem" }}>
        <ProductGrid />
        <Cart />
      </div>
    </div>
  );
}
