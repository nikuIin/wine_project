import type { User } from "@entities/user";
import {
  decodeAccessToken,
  decodeRefreshToken,
  type AccessTokenPayload,
  type RefreshTokenPayload,
} from "@shared/tokens";

export const parseUserFromTokens = (accessToken: string, refreshToken: string): User => {
  const decodedAccessToken: AccessTokenPayload = decodeAccessToken(accessToken);
  const decodedRefreshToken: RefreshTokenPayload = decodeRefreshToken(refreshToken);

  const user: User = {
    user_id: decodedAccessToken.user_id,
    name: decodedRefreshToken.login,
    role: decodedAccessToken.role_id,
    avatarUrl: "TODO: set avatar in access token",
  };

  return user;
};
