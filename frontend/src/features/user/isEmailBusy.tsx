import {
  apiFetch,
  HTTPCode,
  InternalServerError,
  ValidationError,
} from "@shared/index";

interface EmailBusyResponse {
  email_busy: boolean;
}

export const IsEmailBusy = async (email: string) => {
  const response = await apiFetch(`/api/v1/auth/is-email-busy/${email}`, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/sjon",
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

  const data: EmailBusyResponse = await response.json();
  return data.email_busy;
};
