import React from "react";
import { useTranslation } from "react-i18next";

export default function Inventory() {
  const { t } = useTranslation();
  return <h1>{t("nav.inventory")}</h1>;
}
