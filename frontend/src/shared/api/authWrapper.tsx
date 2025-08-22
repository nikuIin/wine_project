import { HTTPCode } from "@shared/enums/httpCodes";
import { UnauthorizedError } from "@shared/errors/htttpErrors";
import { refreshTokens } from "@shared/tokens";

type AsyncMethod = (...args: unknown[]) => Promise<Response>;

export async function authWrapper() {
  return function (_target: object, _propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod: AsyncMethod = descriptor.value;

    descriptor.value = async function (...args: unknown[]): Promise<Response> {
      try {
        // Try to send request
        let response: Response = await originalMethod.apply(this, args);

        // Check if response is unautorized
        if (response.status === HTTPCode.UNAUTHORIZED_401) {
          // Attempt to refresh tokens asynchronously
          const isTokensRefreshed = await refreshTokens();
          if (!isTokensRefreshed) {
            throw new UnauthorizedError("User unauthorized");
          }
          response = await originalMethod.apply(this, args);
        }

        // Return response result
        return response;
      } catch (error) {
        console.error(error);
        throw new Error(`Error with request to the server. Error: ${error}`);
      }
    };
  };
}
