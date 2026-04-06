import { useTranslation } from "react-i18next";

export default function Admin() {
  const { t } = useTranslation();
  return <h1>{t("nav.admin")}</h1>;
}
