export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly cause?: unknown;
  public readonly isOperational: boolean;

  constructor(message: string, statusCode = 500, code = 'INTERNAL_ERROR', cause?: unknown, isOperational = true) {
    super(message);
    Object.setPrototypeOf(this, new.target.prototype); // restore prototype chain
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.code = code;
    this.cause = cause;
    this.isOperational = isOperational;
    Error.captureStackTrace(this);
  }
}

