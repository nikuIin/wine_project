import { apiFetch, UnauthorizedError } from "@shared";
import { HTTPCode } from "@shared";

export const refreshTokens = async (): Promise<boolean> => {
  const response = await apiFetch("/api/v1/auth/refresh");

  if (!response.ok) {
    if (response.status === HTTPCode.UNAUTHORIZED_401) {
      console.error(new UnauthorizedError("Refresh token not valid."));
    } else if (response.status === HTTPCode.FORBIDDEN_403) {
      console.error(new UnauthorizedError("Refresh token expired or blocked."));
    } else {
      // TODO: send mbe status to Sentry
    }
    return false;
  }

  return true;
};
