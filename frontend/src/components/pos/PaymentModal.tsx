import { useState } from "react";
import { useTranslation } from "react-i18next";

interface PaymentModalProps {
  total: number;
  onConfirm: (method: string) => void;
  onClose: () => void;
}

export default function PaymentModal({ total, onConfirm, onClose }: PaymentModalProps) {
  const { t } = useTranslation();
  const [method, setMethod] = useState("CASH");

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "#fff", borderRadius: "12px", padding: "2rem", minWidth: "320px" }}>
        <h2>{t("pos.payment_method")}</h2>
        <p>{t("pos.total")}: <strong>₹{total.toFixed(2)}</strong></p>
        <div style={{ display: "flex", gap: "0.75rem", margin: "1rem 0" }}>
          {["CASH", "UPI", "CARD"].map((m) => (
            <button
              key={m}
              onClick={() => setMethod(m)}
              style={{ padding: "0.5rem 1rem", background: method === m ? "#1a1a2e" : "#eee", color: method === m ? "#fff" : "#333", border: "none", borderRadius: "6px", cursor: "pointer" }}
            >
              {t(`pos.${m.toLowerCase()}`)}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
          <button onClick={onClose} style={{ padding: "0.5rem 1rem" }}>{t("common.cancel")}</button>
          <button
            onClick={() => onConfirm(method)}
            style={{ padding: "0.5rem 1rem", background: "#1a1a2e", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer" }}
          >
            {t("pos.pay_now")}
          </button>
        </div>
      </div>
    </div>
  );
}
