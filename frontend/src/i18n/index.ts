import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import ml from "./locales/ml.json";
import ta from "./locales/ta.json";
import kn from "./locales/kn.json";
import te from "./locales/te.json";

const savedLang = localStorage.getItem("bakemanage_lang") || "en";

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ml: { translation: ml },
    ta: { translation: ta },
    kn: { translation: kn },
    te: { translation: te },
  },
  lng: savedLang,
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
