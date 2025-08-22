import type { UUID } from "@shared/uuid";
import { UUIDFormatError } from "@shared/uuid";

export function asUUID(value: string): UUID {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(value)) {
    throw new UUIDFormatError("Invalid UUID format");
  }

  return value as UUID;
}
