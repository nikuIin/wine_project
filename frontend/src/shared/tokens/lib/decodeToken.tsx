import { TokenValidationError, type AccessTokenPayload, type RefreshTokenPayload } from "@shared/tokens";

function decodeToken(token: string) {
  // Split token
  const token_data = token.split(".");
  // Validate token format
  if (token_data.length != 3) {
    throw new TokenValidationError("Token data is invalid");
  }

  // The second JWT part is payload
  const payload = token_data[1];

  try {
    return JSON.parse(atob(payload));
  } catch (error) {
    console.error("Token validation error", error);
    throw new TokenValidationError(`${error}`);
  }
}

export function decodeAccessToken(token: string): AccessTokenPayload {
  const accessPayload = decodeToken(token);
  try {
    return accessPayload as AccessTokenPayload;
  } catch (error) {
    console.error("Token validation error", error);
    throw new TokenValidationError(`${error}`);
  }
}
export function decodeRefreshToken(token: string): RefreshTokenPayload {
  const accessPayload = decodeToken(token);
  try {
    return accessPayload as RefreshTokenPayload;
  } catch (error) {
    console.error("Token validation error", error);
    throw new TokenValidationError(`${error}`);
  }
}
