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

export class NotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NotFoundError";
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

export class ConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConflictError";
    Object.setPrototypeOf(this, ConflictError.prototype);
  }
}
