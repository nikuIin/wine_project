export const Languages = {
  DEFAULT: "ru-RU",
  RUSSIAN: "ru-RU",
  ENGLISH: "en-EN",
  KAZAKHSTAN: "kz-KZ",
};

export type Language = (typeof Languages)[keyof typeof Languages];
