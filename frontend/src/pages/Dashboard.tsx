import React from "react";
import { useTranslation } from "react-i18next";

export default function Dashboard() {
  const { t } = useTranslation();
  return <h1>{t("nav.dashboard")}</h1>;
}
