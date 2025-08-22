import { Languages } from "@shared";
import i18next from "i18next";

const API_URL = import.meta.env.VITE_API_URL || "";

export function apiFetch(path: string, options: RequestInit = {}) {
  // Generate headers
  const defaultHeaders: HeadersInit = {
    "Content-Type": "application/json",
    Accept: "application/json",
    "Accept-Language": i18next.language || Languages.DEFAULT,
    "X-Forwarded-For": "AUTO_DETECT_IP",
    "User-Agent": navigator.userAgent,
  };

  const headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  // Format body
  let body = options.body;
  if (body && !(body instanceof FormData)) {
    try {
      body = JSON.stringify(body);
    } catch (error) {
      console.error("Error serialized body to JSON", error);
    }
  }

  // Union all
  const fetchOptions: RequestInit = {
    ...options,
    headers,
    body,
  };

  return fetch(`${API_URL}${path}`, fetchOptions);
}
