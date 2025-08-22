import { App } from "@app/routes";
import { ThemeProvider } from "@shared/index";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router";

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import { ruBaseDictionary, enBaseDictionary, kzBaseDictionary, Languages } from "@shared/index";

// Multingualism configuration
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

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    {/*Theme configuration*/}
    <ThemeProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
);
