import { App } from "@app/routes";
import { ThemeProvider } from "@shared/index";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import React from "react";
import { Provider } from "react-redux";

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import {
  ruBaseDictionary,
  enBaseDictionary,
  kzBaseDictionary,
  Languages,
} from "@shared/index";
import {
  ruLoginDictionary,
  enLoginDictionary,
  kzLoginDictionary,
} from "@widgets/login";
export {
  ruContactFormDict,
  enContactFormDict,
  kzContactFormDict,
} from "@widgets/contactForm";
import {
  ruLanguageSwitcherDictionary,
  enLanguageSwitcherDictionary,
  kzLanguageSwitcherDictionary,
} from "@widgets/languageSwitcher";
import {
  ruMainIntroductionDictionary,
  enMainIntroductionDictionary,
  kzMainIntroductionDictionary,
} from "@widgets/mainIntroductionWidget";
import {
  ruConfidenceIndicatorDict,
  enConfidenceIndicatorDict,
  kzConfidenceIndicatorDict,
} from "@widgets/confidenceIndicator";

import {
  ruAboutUsDict,
  enAboutUsDict,
  kzAboutUsDict,
} from "@widgets/aboutUsWidget";

import { ruHeaderDict, enHeaderDict, kzHeaderDict } from "@widgets/header";

import { store, persistor } from "@app/store";
import { PersistGate } from "redux-persist/integration/react";
import {
  enContactFormDict,
  kzContactFormDict,
  ruContactFormDict,
} from "@widgets/contactForm";

// Multingualism configuration
i18n
  .use(initReactI18next)
  .use(LanguageDetector)
  .init({
    resources: {
      [Languages.RUSSIAN]: {
        translation: {
          ...ruBaseDictionary,
          ...ruLoginDictionary,
          ...ruLanguageSwitcherDictionary,
          ...ruMainIntroductionDictionary,
          ...ruHeaderDict,
          ...ruConfidenceIndicatorDict,
          ...ruAboutUsDict,
          ...ruContactFormDict,
        },
      },
      [Languages.ENGLISH]: {
        translation: {
          ...enBaseDictionary,
          ...enLoginDictionary,
          ...enLanguageSwitcherDictionary,
          ...enMainIntroductionDictionary,
          ...enHeaderDict,
          ...enConfidenceIndicatorDict,
          ...enAboutUsDict,
          ...enContactFormDict,
        },
      },
      [Languages.KAZAKHSTAN]: {
        translation: {
          ...kzBaseDictionary,
          ...kzLoginDictionary,
          ...kzLanguageSwitcherDictionary,
          ...kzMainIntroductionDictionary,
          ...kzHeaderDict,
          ...kzConfidenceIndicatorDict,
          ...kzAboutUsDict,
          ...kzContactFormDict,
        },
      },
    },
    fallbackLng: Languages.RUSSIAN,
    interpolation: {
      escapeValue: false,
    },
  });

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement,
);
root.render(
  <Provider store={store}>
    <PersistGate persistor={persistor}>
      <React.StrictMode>
        <ThemeProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </ThemeProvider>
      </React.StrictMode>
    </PersistGate>
  </Provider>,
);
