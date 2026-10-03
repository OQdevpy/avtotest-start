import {
  CONTENT_TYPE, b64d, b64e, deriveKey, exportPublic, newKeyPair, open, seal,
} from "./envelope";
import { deviceId, kvDel, kvGet, kvSet } from "./store";
import { transport } from "./transport";

const BASE = "/api";
let session = null; // { key: CryptoKey, token, sid, name, expiresAt }
let onLogout = () => {};

export class ApiError extends Error {
  constructor(status, code, data) {
    super(code);
    this.status = status;
    this.code = code;
    this.data = data;
  }
}

export function setLogoutHandler(fn) {
  onLogout = fn;
}

export async function restoreSession() {
  const s = await kvGet("session");
  if (s && new Date(s.expiresAt) > new Date()) {
    session = s;
    return s;
  }
  await kvDel("session");
  return null;
}

export async function login(code) {
  const pair = await newKeyPair();
  const res = await transport(`${BASE}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "omit",
    body: JSON.stringify({
      code,
      device_id: await deviceId(),
      client_pub: b64e(await exportPublic(pair)),
    }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(res.status, data.error || "error", data);

  const key = await deriveKey(pair, b64d(data.server_pub), b64d(data.salt), data.sid);
  session = { key, token: data.token, sid: data.sid, name: data.student.full_name, expiresAt: data.expires_at };
  await kvSet("session", session);
  return session;
}

export async function logout() {
  try {
    if (session) await post("/auth/logout/", {});
  } catch {
    /* sessiya allaqachon yaroqsiz bo'lishi mumkin */
  }
  await clearSession();
}

async function clearSession() {
  session = null;
  await kvDel("session");
}

async function headers() {
  return { Authorization: `Bin ${session.token}`, "X-Device-Id": await deviceId() };
}

async function handle(res, path) {
  const ct = res.headers.get("Content-Type") || "";
  let data = null;
  if (ct.startsWith(CONTENT_TYPE)) {
    data = (await open(session.key, await res.arrayBuffer(), { path, direction: "res" })).data;
  } else if (ct.startsWith("application/json")) {
    data = await res.json();
  }
  if (res.status === 401) {
    await clearSession();
    onLogout(data?.error);
  }
  if (!res.ok) throw new ApiError(res.status, data?.error || `http_${res.status}`, data);
  return data;
}

function nonce() {
  return b64e(crypto.getRandomValues(new Uint8Array(16)));
}

export async function get(path) {
  if (!session) throw new ApiError(401, "no_session");
  const full = BASE + path;
  const res = await transport(full, { headers: await headers(), credentials: "omit", cache: "no-store" });
  return handle(res, full);
}

export async function post(path, payload = {}) {
  if (!session) throw new ApiError(401, "no_session");
  const full = BASE + path;
  // _ts va _n — replay himoyasi (server ikkinchi marta qabul qilmaydi).
  const body = await seal(session.key, { ...payload, _ts: Date.now(), _n: nonce() }, { path: full, direction: "req" });
  const res = await transport(full, {
    method: "POST",
    headers: { ...(await headers()), "Content-Type": CONTENT_TYPE },
    credentials: "omit",
    body,
  });
  return handle(res, full);
}

/** Rasm/audio: shifrlangan .bin → Blob URL. Chaqiruvchi URL.revokeObjectURL qilishi kerak. */
export async function media(ref) {
  const full = `${BASE}/media/${ref}.bin`;
  const res = await transport(full, { headers: await headers(), credentials: "omit", cache: "no-store" });
  if (!res.ok) throw new ApiError(res.status, "media");
  const { mime, data } = await open(session.key, await res.arrayBuffer(), { path: full, direction: "res" });
  return URL.createObjectURL(new Blob([data], { type: mime }));
}

export const currentSession = () => session;
