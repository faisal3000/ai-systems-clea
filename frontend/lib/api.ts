// frontend/lib/api.ts

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

/**
 * POST helper for both JSON and form-encoded requests.
 */
export async function post(
  path: string,
  body: Record<string, any>,
  options: { form?: boolean; token?: string } = {}
): Promise<any> {
  const headers: Record<string, string> = {};

  if (options.form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else {
    headers["Content-Type"] = "application/json";
  }

  if (options.token) {
    headers["Authorization"] = `Bearer ${options.token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: options.form
      ? new URLSearchParams(body as Record<string, string>).toString()
      : JSON.stringify(body),
  });

  return res.json();
}
