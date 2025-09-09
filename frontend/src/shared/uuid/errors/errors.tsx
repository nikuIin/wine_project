import { ValidationError } from "@shared";

export class UUIDFormatError extends ValidationError {
  constructor(message: string) {
    super(message);
    Object.setPrototypeOf(this, UUIDFormatError.prototype);
  }
}
