import { useTranslation } from "react-i18next";

interface ReceiptData {
  sale_id: number;
  total: number;
  payment_method: string;
  date: string;
}

interface ReceiptModalProps {
  receipt: ReceiptData;
  onClose: () => void;
  onPrint: () => void;
}

export default function ReceiptModal({ receipt, onClose, onPrint }: ReceiptModalProps) {
  const { t } = useTranslation();

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "#fff", borderRadius: "12px", padding: "2rem", minWidth: "320px", textAlign: "center" }}>
        <h2>✅ {t("pos.sale_complete")}</h2>
        <p>Receipt #{receipt.sale_id}</p>
        <p>{t("pos.total")}: <strong>₹{receipt.total.toFixed(2)}</strong></p>
        <p>{t("pos.payment_method")}: {receipt.payment_method}</p>
        <p style={{ fontSize: "0.85rem", color: "#666" }}>{receipt.date}</p>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center", marginTop: "1rem" }}>
          <button onClick={onPrint} style={{ padding: "0.5rem 1rem", background: "#1a1a2e", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer" }}>
            {t("pos.print_receipt")}
          </button>
          <button onClick={onClose} style={{ padding: "0.5rem 1rem" }}>{t("common.cancel")}</button>
        </div>
      </div>
    </div>
  );
}
