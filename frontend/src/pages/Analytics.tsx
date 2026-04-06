import { useTranslation } from "react-i18next";

export default function Analytics() {
  const { t } = useTranslation();
  return <h1>{t("nav.analytics")}</h1>;
}
