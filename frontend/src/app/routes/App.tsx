import { Routes, Route } from "react-router-dom";
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import { ruBaseDictionary, enBaseDictionary, kzBaseDictionary, Languages } from "@shared/index";

i18n
  .use(initReactI18next)
  .use(LanguageDetector)
  .init({
    resources: {
      [Languages.RUSSIAN]: { translation: { ...ruBaseDictionary } },
      [Languages.ENGLISH]: { translation: { ...enBaseDictionary } },
      [Languages.KAZAKHSTAN]: { translation: { ...kzBaseDictionary } },
    },
    fallbackLng: Languages.RUSSIAN,
    interpolation: {
      escapeValue: false,
    },
  });

export function App() {
  return (
    <Routes>
      <Route path="/"></Route>
    </Routes>
  );
}
