import { Routes, Route } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { Languages } from "@shared/index";
import { useEffect, useState } from "react";
import i18next from "i18next";

function getRandomInt(min: number, max: number) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function App() {
  const { t } = useTranslation();

  const [language, setLanguage] = useState<string>("ru");

  useEffect(() => {
    console.log(i18next.language);
  }, [language]);

  const changeLanguage = () => {
    const random = getRandomInt(0, 2);
    if (random == 0) {
      i18next.changeLanguage(Languages.RUSSIAN);
      setLanguage(Languages.RUSSIAN);
    } else if (random == 1) {
      i18next.changeLanguage(Languages.ENGLISH);
      setLanguage(Languages.ENGLISH);
    } else {
      i18next.changeLanguage(Languages.KAZAKHSTAN);
      setLanguage(Languages.KAZAKHSTAN);
    }
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <div>
            TEXT: {t("test")}
            <button onClick={changeLanguage}></button>
          </div>
        }
      ></Route>
    </Routes>
  );
}
