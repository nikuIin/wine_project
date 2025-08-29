import { type User } from "@entities/user";
import { clearUser, setUser } from "@entities/user/model";
import { UnauthorizedError, type Language } from "@shared/index";
import type { AppDispatch } from "@shared/store";
import { getTokens, type AccessTokenPayload, type RefreshTokenPayload } from "@shared/tokens";
import { decodeAccessToken, decodeRefreshToken } from "@shared/tokens";

export const LoginFeat = async (login: string, password: string, language: Language, dispatch: AppDispatch) => {
  try {
    const [accessToken, refreshToken] = await getTokens(login, password, language);

    const decodedAccessToken: AccessTokenPayload = decodeAccessToken(accessToken);
    const decodedRefreshToken: RefreshTokenPayload = decodeRefreshToken(refreshToken);

    const user: User = {
      user_id: decodedAccessToken.user_id,
      name: decodedRefreshToken.login,
      role: decodedAccessToken.role_id,
      avatarUrl: "TODO: set avatar in access token",
    };

    dispatch(setUser(user));
    return user;
  } catch (error) {
    if (!(error instanceof UnauthorizedError)) {
      throw error;
    } else {
      dispatch(clearUser());
      console.error("Error when authorize", error);
      throw error;
    }
  }
};
