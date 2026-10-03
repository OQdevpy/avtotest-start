// Demo: Django o'rniga brauzer ichidagi server (demoServer.js). Shifrlash haqiqiy.
import { handle } from "./demoServer";

export const DEMO = true;

export async function transport(url, init = {}) {
  const path = new URL(url, location.href).pathname;
  const headers = new Headers(init.headers || {});
  const body = init.body == null ? null : init.body instanceof Uint8Array ? init.body : new TextEncoder().encode(init.body);
  const res = await handle({
    method: init.method || "GET",
    path,
    headers,
    body,
  });
  // Tarmoq kechikishini taqlid qilish
  await new Promise((r) => setTimeout(r, 60));
  return new Response(res.body, { status: res.status, headers: { "Content-Type": res.contentType } });
}
