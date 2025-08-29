import { Languages, type Language } from "@shared/enums/languages";

const API_URL = import.meta.env.VITE_API_URL || "";

export function apiFetch(path: string, options: RequestInit = {}, language: Language = Languages.DEFAULT) {
  // Generate headers
  const defaultHeaders: HeadersInit = {
    "Accept-Language": language,
    "X-Forwarded-For": "AUTO_DETECT_IP",
    "User-Agent": navigator.userAgent,
  };

  const headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  // Union all
  const fetchOptions: RequestInit = {
    ...options,
    headers,
  };

  return fetch(`${API_URL}${path}`, fetchOptions);
}
