import { apiFetch, HTTPCode } from "@shared";
import { UnauthorizedError, InternalServerError, UnprocessableContentError } from "@shared";
import getBrowserFingerprint from "get-browser-fingerprint";
import { TokenValidationError } from "../model/errors";

export const getTokens = async (userLogin: string, password: string): Promise<[string, string]> => {
  const user_creds = {
    login: userLogin,
    password: password,
    fingerprint: getBrowserFingerprint(),
  };

  const response = await apiFetch("/api/v1/token", {
    method: "POST",
    body: JSON.stringify(user_creds),
  });

  if (!response.ok) {
    if (response.status === HTTPCode.UNAUTHORIZED_401) {
      throw new UnauthorizedError("Invalid credentials");
    } else if (response.status === HTTPCode.UNPROCESSABLE_CONTENT_422) {
      // TODO: send message to the Sentry
      console.error(`Invalid JSON credentional data: ${user_creds}`);
      throw new UnprocessableContentError("Invalid data");
    } else if (response.status === HTTPCode.INTERNAL_SERVER_ERROR_500) {
      throw new InternalServerError("Internal server error");
    }
  }

  const body = await response.json();
  const isBodyValid =
    body.access_token !== undefined &&
    body.access_token !== null &&
    typeof body.access_token === "string" &&
    body.refresh_token !== undefined &&
    body.refresh_token !== null &&
    typeof body.refresh_token === "string";

  if (!isBodyValid) {
    throw new TokenValidationError("Tokens data is invalid");
  }

  const accessToken: string = body.access_token;
  const refreshToken: string = body.refresh_token;

  return [accessToken, refreshToken];
};
