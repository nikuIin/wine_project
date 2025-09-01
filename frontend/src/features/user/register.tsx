import type { AppDispatch } from "@shared/store";
import { apiFetch, HTTPCode, InternalServerError, UnprocessableContentError } from "@shared/index";
import getBrowserFingerprint from "get-browser-fingerprint";
import { TokenValidationError } from "@shared/tokens";
import { setUser } from "@entities/user/model";
import { parseUserFromTokens } from "./utils/parseUserFromTokens";

export const Register = async (login: string, password: string, email: string, dispatch: AppDispatch) => {
  const user_creds = {
    login: login,
    password: password,
    email: email,
    fingerprint: await getBrowserFingerprint(),
  };

  const response = await apiFetch("/api/v1/auth/register/", {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    method: "POST",
    body: JSON.stringify(user_creds),
  });

  if (!response.ok) {
    if (response.status === HTTPCode.CONFLICT_409) {
      throw new Error("User with this data already exists.");
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

  const user = parseUserFromTokens(body.access_token, body.refresh_token);
  dispatch(setUser(user));
};
