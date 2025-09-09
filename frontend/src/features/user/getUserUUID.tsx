import { setUserUUID } from "@entities/user/model";
import {
  apiFetch,
  HTTPCode,
  InternalServerError,
  type UUID,
} from "@shared/index";
import type { AppDispatch } from "@shared/store";

interface LightRegistrationResponse {
  user_id: UUID;
}

export const LightRegistration = async (dispatch: AppDispatch) => {
  const response = await apiFetch("/api/v1/auth/light-register", {
    method: "POST",
  });

  if (!response.ok) {
    if (response.status === HTTPCode.CONFLICT_409) {
      throw new Error("User with this data already exists.");
    } else if (response.status === HTTPCode.INTERNAL_SERVER_ERROR_500) {
      throw new InternalServerError("Internal server error");
    }
  }

  const response_body: LightRegistrationResponse = await response.json();

  dispatch(setUserUUID(response_body.user_id));
};
