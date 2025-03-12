import type { GqlError } from "nuxt-graphql-client";

function isGqlError(error: unknown): error is GqlError {
  return (error as GqlError).client !== undefined;
}

class ApiError extends Error {
  statusCode?: number;
  statusMessage: string;

  constructor({ statusCode, statusMessage }: { statusCode: number; statusMessage: string }) {
    super(`API Error: ${statusCode || "Unknown status code"}`);
    this.statusCode = statusCode;
    this.statusMessage = statusMessage;
  }
}

export type GqlErrorHandlingOptionsFunctions = {
  toast?: {
    title?: string;
    description?: string;
  };
  redirect?: boolean;
};

function HttpStatusCodeToErrorMessages(
  statusCode: number | undefined,
  operationName = "unknown"
): {
  title?: string;
  description?: string;
} {
  if (!statusCode) return {};
  switch (statusCode) {
    case 404:
      return {
        title: "Resource Not Found",
        description: `Page Not Found on ${operationName}`
      };
    case 403:
      return {
        title: "Request Forbidden",
        description: `Access Denied on ${operationName}`
      };
    case 500:
      return {
        title: "Internal Server Error",
        description: `Internal Server Error on ${operationName}`
      };
    case 401:
      return {
        title: "Reqest Unauthorized",
        description: `Unauthorized on ${operationName}`
      };
    case 400:
      return {
        title: "Bad Request",
        description: `Bad Request on ${operationName}`
      };
    case 405:
      return {
        title: "Method Not Allowed",
        description: `Method Not Allowed on ${operationName}`
      };
    case 409:
      return {
        title: "Conflict",
        description: `Conflict on ${operationName}`
      };
    case 422:
      return {
        title: "Unprocessable Entity",
        description: `Unprocessable Entity on ${operationName}`
      };
    case 429:
      return {
        title: "Too Many Requests",
        description: `Too Many Requests on ${operationName}`
      };
    case 502:
      return {
        title: "Bad Gateway",
        description: `Bad Gateway on ${operationName}`
      };
    case 503:
      return {
        title: "Service Unavailable",
        description: `Service Unavailable on ${operationName}`
      };
    case 504:
      return {
        title: "Gateway Timeout",
        description: `Gateway Timeout on ${operationName}`
      };
    default:
      return {};
  }
}

interface ErrorDetails {
  statusCode?: number;
  statusMessage: string;
  title?: string;
  description?: string;
  operationName?: string;
}

function extractErrorDetails(error: unknown): ErrorDetails {
  if (isGqlError(error)) {
    const { statusCode, operationName, gqlErrors } = error;
    const { title, description } = HttpStatusCodeToErrorMessages(statusCode, operationName);
    return {
      statusCode,
      statusMessage: `Error on ${operationName}\n${gqlErrors[0]?.message}`,
      title: title || `Error on ${operationName}`,
      description: gqlErrors[0]?.message || description,
      operationName
    };
  }

  if (error instanceof ApiError) {
    return {
      statusCode: error.statusCode,
      statusMessage: error.statusMessage,
      title: error.statusMessage,
      description: ""
    };
  }

  // Default error case
  return {
    statusCode: 500,
    statusMessage: JSON.stringify(error) || "Unknown Error",
    title: "Unknown Error",
    description: error ? String(error) : "Unknown Error"
  };
}

function handleErrorResponse(
  errorDetails: ErrorDetails,
  options?: GqlErrorHandlingOptionsFunctions,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  $toast?: any
) {
  if (options?.redirect) {
    showError(
      createError({
        statusCode: errorDetails.statusCode,
        statusMessage: errorDetails.statusMessage
      })
    );
    return;
  }

  if ($toast) {
    $toast.error(options?.toast?.title || errorDetails.title || "Unknown Error", {
      description: options?.toast?.description || errorDetails.description
    });
  }
}

export default function useErrorHandling(options?: GqlErrorHandlingOptionsFunctions) {
  const { $toast } = useNuxtApp();

  function onError(error: unknown) {
    if (!error) return;
    console.log("error", error);

    const errorDetails = extractErrorDetails(error);
    handleErrorResponse(errorDetails, options, $toast);
  }

  function throwErrorIfNoData(data: unknown, statusCode: number, statusMessage: string) {
    if (!data) {
      throw new ApiError({ statusCode, statusMessage });
    }
  }

  function onErrorInData(data: unknown) {
    if (!data) {
      throw new ApiError({ statusCode: 500, statusMessage: "No data received" });
    }
  }

  return { onError, throwErrorIfNoData, onErrorInData };
}
