import {
  apiFetch,
  HTTPCode,
  InternalServerError,
  ValidationError,
} from "@shared/index";

interface LoginBusyResponse {
  login_busy: boolean;
}

export const IsLoginBusy = async (login: string): Promise<boolean> => {
  const response = await apiFetch(`/api/v1/auth/is-user-exists/${login}`, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    method: "GET",
  });

  if (!response.ok) {
    if (response.status === HTTPCode.UNPROCESSABLE_CONTENT_422) {
      throw new ValidationError("Invalid request format");
    } else if (response.status === HTTPCode.INTERNAL_SERVER_ERROR_500) {
      throw new InternalServerError("Internal server error");
    }
  }

  const data: LoginBusyResponse = await response.json();
  return data.login_busy;
};
