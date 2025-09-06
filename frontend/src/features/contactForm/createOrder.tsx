import {
  apiFetch,
  ConflictError,
  HTTPCode,
  NotFoundError,
  ValidationError,
} from "@shared/index";
import type { UUID } from "@shared/uuid";

export interface CreateOrderParams {
  sale_stage_id: number;
  lead_id: UUID;
  email: string | undefined;
  phone: string | undefined;
  name: string;
  cost: number;
  probability: number;
  priority: number;
}

export const createOrder = async (order: CreateOrderParams): Promise<void> => {
  const body = {
    sale_stage_id: order.sale_stage_id,
    lead_id: order.lead_id,
    fields: {
      name: order.name,
      email: order.email,
      phone: order.phone,
    },
    cost: order.cost,
    probability: order.probability,
    priority: order.priority,
  };

  const response = await apiFetch("/api/v1/deal", {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    method: "POST",
    body: JSON.stringify(body),
  });

  if (response.status === HTTPCode.NOT_FOUND_404) {
    throw new NotFoundError(
      "The data doesn't exists. Please, check if the lead with this id or sale stage exists.",
    );
  } else if (response.status === HTTPCode.CONFLICT_409) {
    throw new ConflictError("The deal already exists.");
  } else if (response.status === HTTPCode.UNPROCESSABLE_CONTENT_422) {
    throw new ValidationError("Invalid request format");
  }
};
