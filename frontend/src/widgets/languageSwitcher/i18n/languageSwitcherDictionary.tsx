import { Languages } from "@shared/index";

export const ruLanguageSwitcherDictionary = {
  chooseLanguage: "Выберите язык",
  notification: {
    success: {
      status: "Успешно!",
      message: "Язык успешно изменён.",
    },
    warning: {
      status: "Непредвиденная ошибка",
      message: `Не удалось изменить язык, язык установлен на ${Languages.DEFAULT}`,
    },
  },
};
export const enLanguageSwitcherDictionary = {
  chooseLanguage: "Choose language",
  notification: {
    success: {
      status: "Success!",
      message: "Language changed successfully.",
    },
    warning: {
      status: "Unexpected error",
      message: `Failed to change language, language set to ${Languages.DEFAULT}`,
    },
  },
};

export const kzLanguageSwitcherDictionary = {
  chooseLanguage: "Тілді таңдаңыз",
  notification: {
    success: {
      status: "Сәтті!",
      message: "Тіл сәтті өзгертілді.",
    },
    warning: {
      status: "Күтілмеген қате",
      message: `Тілді өзгерту мүмкін болмады, тіл ${Languages.DEFAULT} болып орнатылды`,
    },
  },
};
