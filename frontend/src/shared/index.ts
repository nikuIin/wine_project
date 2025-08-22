export { ThemeContext, type Theme } from "@shared/theme/context";
export { ThemeProvider } from "@shared/theme/provider";
export { useTheme } from "@shared/theme/hooks";

export { ValidationError } from "@shared/errors/validationErrors";
export { asUUID } from "@shared/uuid";
export type { UUID } from "@shared/uuid";
export { apiFetch } from "@shared/api/baseFetch";
export type { Role } from "@shared/enums/roles";
export { HTTPCode } from "@shared/enums/httpCodes";
export { Languages, type Language } from "@shared/enums/languages";
export {
  UnauthorizedError,
  InternalServerError,
  UnprocessableContentError,
} from "@shared/errors/htttpErrors";

export {
  ruBaseDictionary,
  enBaseDictionary,
  kzBaseDictionary,
} from "@shared/i18n/dictionaries/baseDictionaries";
