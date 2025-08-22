export class UnauthorizedError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UnauthorizedError";
    Object.setPrototypeOf(this, UnauthorizedError.prototype);
  }
}

export class InternalServerError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "InternalServerError";
    Object.setPrototypeOf(this, InternalServerError.prototype);
  }
}

export class UnprocessableContentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UnprocessableContentError";
    Object.setPrototypeOf(this, UnprocessableContentError.prototype);
  }
}
