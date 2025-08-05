// frontend/lib/api.ts
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

/* -------------------------------------------------------- */
/*  low-level helpers                                       */
/* -------------------------------------------------------- */

/** Generic POST (JSON or form-urlencoded) */
export async function post(
  path: string,
  body: Record<string, any>,
  options: { form?: boolean; token?: string } = {}
): Promise<any> {
  const headers: Record<string, string> = {
    "Content-Type": options.form
      ? "application/x-www-form-urlencoded"
      : "application/json",
  };
  if (options.token) headers["Authorization"] = `Bearer ${options.token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: options.form
      ? new URLSearchParams(
          body as Record<string, string>
        ).toString()
      : JSON.stringify(body),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/** Simple GET with optional Bearer token */
export async function get(path: string, token?: string): Promise<any> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/* -------------------------------------------------------- */
/*  high-level wrappers used by your React components       */
/* -------------------------------------------------------- */

export async function login(username: string, password: string) {
  const data = { grant_type: "password", username, password };
  // FastAPI OAuth2 “password” flow expects form-encoded
  const { access_token } = await post("/auth/login", data, { form: true });
  return access_token as string;
}

export async function getMe(token: string) {
  return await get("/users/me", token);
}
