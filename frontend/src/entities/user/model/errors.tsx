class UserError extends Error {
  public detail: string | null = "Error, those related to the user entity.";

  constructor(message: string, detail?: string) {
    super(message);

    // Rewrite prototype from Error to UserError for right extending
    Object.setPrototypeOf(this, UserError.prototype);

    this.name = "UserError";
    if (detail) {
      this.detail = detail;
    }
  }
}

export class UserNotFoundError extends UserError {
  public status: number | null = null;

  constructor(message: string, status: number | null = null, detail?: string) {
    super(message, detail ?? "Error, when user not found");

    this.name = "UserNotFoundError";
    this.status = status;

    Object.setPrototypeOf(this, UserNotFoundError.prototype);
  }
}
