const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function postChat(messages) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  if (!response.ok) {
    let errorDetail = `Server error (${response.status})`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorDetail = errorData.detail;
      }
    } catch {
      // Response body was not valid JSON; use the generic message
    }
    throw new ApiError(errorDetail, response.status);
  }

  const data = await response.json();

  if (!data.response) {
    throw new ApiError("Received an empty response from the AI service.", 502);
  }

  return data;
}
