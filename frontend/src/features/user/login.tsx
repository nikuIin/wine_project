import { clearUser, setUser, type User } from "@entities/user";
import { UnauthorizedError } from "@shared/index";
import { getTokens, type AccessTokenPayload, type RefreshTokenPayload } from "@shared/tokens";
import { decodeAccessToken, decodeRefreshToken } from "@shared/tokens";

export const login = async (login: string, password: string) => {
  try {
    const [accessToken, refreshToken] = await getTokens(login, password);

    const decodedAccessToken: AccessTokenPayload = decodeAccessToken(accessToken);
    const decodedRefreshToken: RefreshTokenPayload = decodeRefreshToken(refreshToken);

    const user: User = {
      user_id: decodedAccessToken.user_id,
      name: decodedRefreshToken.login,
      role: decodedAccessToken.role_id,
      avatarUrl: "TODO: set avatar in access token",
    };
    setUser(user);
  } catch (error) {
    if (!(error instanceof UnauthorizedError)) {
      throw error;
    } else {
      clearUser();
      console.error("Error when authorize", error);
      throw error;
    }
  }
};
