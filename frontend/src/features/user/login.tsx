import { clearUser, setUser } from "@entities/user/model";
import { UnauthorizedError, type Language } from "@shared/index";
import type { AppDispatch } from "@shared/store";
import { getTokens } from "@shared/tokens";
import { parseUserFromTokens } from "./utils/parseUserFromTokens";

export const LoginFeat = async (login: string, password: string, language: Language, dispatch: AppDispatch) => {
  try {
    const [accessToken, refreshToken] = await getTokens(login, password, language);

    const user = parseUserFromTokens(accessToken, refreshToken);

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
