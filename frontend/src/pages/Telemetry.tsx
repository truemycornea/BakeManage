import { useTranslation } from "react-i18next";

export default function Telemetry() {
  const { t } = useTranslation();
  return <h1>{t("nav.telemetry")}</h1>;
}
