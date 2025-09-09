import { ValidationError } from "@shared";

export class TokenValidationError extends ValidationError {
  constructor(message: string) {
    super(message);
    this.name = "TokenValidationError";
    Object.setPrototypeOf(this, TokenValidationError.prototype);
  }
}
