// Brauzer ichidagi demo server: backend (Django) mantiqining nusxasi.
// Protokol aynan bir xil: ECDH P-256 + HKDF → AES-256-GCM, .bin konvert, AAD yo'lga bog'langan,
// _ts/_n replay himoyasi, qurilmaga bog'langan token, baholash "server"da.

import { CONTENT_TYPE, b64d, b64e, deriveKey, exportPublic, newKeyPair, open, seal } from "./envelope";
import { STUDENTS } from "./demoData";
import { kvGet, kvSet } from "./store";

const EXAM_SECONDS = 25 * 60;
const EXAM_SECONDS_LONG = 45 * 60;
const EXAM_LONG_THRESHOLD = 20;
const SESSION_HOURS = 12;
const MAX_SKEW = 120;
const enc = new TextEncoder();

// ---------- Kontent (deterministik, seed_demo bilan bir xil tuzilma) ----------

function sample(rng, arr, k) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a.slice(0, Math.min(k, a.length));
}

// Kontent haqiqiy bazadan (Firebase eksporti) — public/content.json.
// Rasmlar shu faylda nom bilan keladi, brauzer ularni to'g'ridan-to'g'ri
// public/media/ dan (GitHub Pages orqali) o'qiydi — shifrlanmaydi.
let DB = null;
let Q = null;

async function ensureContent() {
  if (DB) return;
  const base = import.meta.env.BASE_URL || "/";
  const res = await fetch(`${base}content.json`, { cache: "no-cache" });
  if (!res.ok) throw new Error("content.json yuklanmadi");
  DB = await res.json();
  Q = new Map(DB.questions.map((q) => [q.id, q]));
}

// ---------- Holat (IndexedDB'da saqlanadi — sahifa yangilanganda ham) ----------

let state = null;

async function load() {
  if (!state) {
    state = (await kvGet("demo_server_state")) || { sessions: {}, attempts: {}, nextAttempt: 1, nonces: {} };
  }
  return state;
}

async function persist() {
  const now = Date.now();
  for (const [n, t] of Object.entries(state.nonces)) if (now - t > MAX_SKEW * 2000) delete state.nonces[n];
  await kvSet("demo_server_state", state);
}

async function sha256(text) {
  const h = await crypto.subtle.digest("SHA-256", enc.encode(text));
  return Array.from(new Uint8Array(h), (b) => b.toString(16).padStart(2, "0")).join("");
}

// ---------- Javob yordamchilari ----------

const json = (status, data) => ({ status, contentType: "application/json", body: enc.encode(JSON.stringify(data)) });

class HttpError extends Error {
  constructor(status, code, extra = {}) {
    super(code);
    this.status = status;
    this.code = code;
    this.extra = extra;
  }
}

// ---------- Login (ochiq JSON — hali kalit yo'q) ----------

async function login(req) {
  const body = JSON.parse(new TextDecoder().decode(req.body || new Uint8Array()));
  const code = String(body.code || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
  const student = STUDENTS.find((s) => s.code === code);
  if (!student || !student.active) return json(401, { error: "invalid_code" });
  if (!/^[A-Za-z0-9_-]{16,64}$/.test(body.device_id || "")) return json(400, { error: "bad_device" });

  const st = await load();
  const now = Date.now();
  const active = Object.entries(st.sessions).filter(
    ([, s]) => s.student === student.id && !s.revoked && s.expires > now,
  );
  for (const [, s] of active) if (s.device === body.device_id) s.revoked = true;
  if (active.filter(([, s]) => s.device !== body.device_id).length >= student.max_devices) {
    return json(403, { error: "device_limit" });
  }

  const sid = crypto.randomUUID().replace(/-/g, "");
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const serverPair = await newKeyPair();
  let key;
  try {
    key = await deriveKey(serverPair, b64d(body.client_pub), salt, sid);
  } catch {
    return json(400, { error: "bad_public_key" });
  }
  const token = b64e(crypto.getRandomValues(new Uint8Array(32))).replace(/[+/=]/g, (c) => ({ "+": "-", "/": "_", "=": "" })[c]);
  const expires = now + SESSION_HOURS * 3600 * 1000;
  // Token faqat xesh ko'rinishida saqlanadi
  st.sessions[await sha256(token)] = { sid, key, student: student.id, device: body.device_id, expires, revoked: false };
  await persist();
  return json(200, {
    token,
    sid,
    server_pub: b64e(await exportPublic(serverPair)),
    salt: b64e(salt),
    expires_at: new Date(expires).toISOString(),
    student: { full_name: student.full_name },
  });
}

async function authenticate(req) {
  const h = req.headers.get("Authorization") || "";
  if (!h.startsWith("Bin ")) throw new HttpError(401, "not_authenticated");
  const st = await load();
  const s = st.sessions[await sha256(h.slice(4))];
  if (!s) throw new HttpError(401, "invalid_token");
  if (s.revoked || s.expires < Date.now()) throw new HttpError(401, "session_expired");
  if (req.headers.get("X-Device-Id") !== s.device) throw new HttpError(401, "device_mismatch");
  return s;
}

async function readBody(req, session) {
  let data;
  try {
    ({ data } = await open(session.key, req.body, { path: req.path, direction: "req" }));
  } catch {
    throw new HttpError(400, "bad_bin");
  }
  const { _ts: ts, _n: nonce, ...rest } = data || {};
  if (typeof ts !== "number" || typeof nonce !== "string") throw new HttpError(400, "bad_bin");
  if (Math.abs(Date.now() - ts) > MAX_SKEW * 1000) throw new HttpError(400, "clock_skew");
  const k = `${session.sid}:${nonce}`;
  if (state.nonces[k]) throw new HttpError(400, "replay");
  state.nonces[k] = Date.now();
  return rest;
}

// ---------- Imtihon mantiqi (apps/exams/views.py nusxasi) ----------

const isOpen = (a) => !a.finished && (a.deadline == null || a.deadline > Date.now());

function resultOf(a) {
  const correct = a.items.filter((i) => i.correct === true).length;
  const mistakes = a.items.length - correct;
  return { total: a.items.length, correct, mistakes, passed: mistakes <= Math.max(2, Math.floor(a.items.length / 10)) };
}

function serializeAttempt(a) {
  const revealAll = a.kind === "study" || !isOpen(a);
  return {
    id: a.id,
    kind: a.kind,
    ref: a.ref,
    finished: !isOpen(a),
    remaining: a.deadline ? Math.max(0, Math.round((a.deadline - Date.now()) / 1000)) : null,
    result: isOpen(a) ? null : resultOf(a),
    questions: a.items.map((it) => {
      const q = Q.get(it.q);
      const show = revealAll || it.chosen != null;
      return {
        id: q.id,
        text: q.text,
        image: q.image || null,
        photo_hint: null,
        audio_hint: null,
        explanation: show ? q.explanation : null,
        answers: q.answers.map((x) => ({ id: x.id, text: x.text })),
        chosen: it.chosen,
        correct: show ? q.answers.find((x) => x.correct).id : null,
      };
    }),
  };
}

function finish(a) {
  if (!a.finished) a.finished = Date.now();
}

function pick(kind, ref, count) {
  if (kind === "study" || kind === "category") {
    if (!DB.categories.some((c) => c.id === ref)) throw new HttpError(404, "not_found");
    return DB.questions.filter((q) => q.category === ref).map((q) => q.id);
  }
  if (kind === "variant") {
    const v = DB.variants.find((x) => x.id === ref);
    if (!v) throw new HttpError(404, "not_found");
    return v.questions;
  }
  const pool = kind === "stage" ? DB.questions.filter((q) => q.stage === ref) : DB.questions;
  if (kind === "stage" && !pool.length) throw new HttpError(404, "not_found");
  const rnd = () => crypto.getRandomValues(new Uint32Array(1))[0] / 2 ** 32;
  return sample(rnd, pool.map((q) => q.id), count);
}

function ownAttempt(session, id) {
  const a = state.attempts[id];
  if (!a || a.student !== session.student) throw new HttpError(404, "not_found");
  return a;
}

// ---------- Marshrutlar ----------

const routes = [
  ["POST", /^\/api\/auth\/logout\/$/, async (s) => {
    s.revoked = true;
    return { ok: true };
  }],
  ["GET", /^\/api\/auth\/me\.bin$/, async (s) => ({
    full_name: STUDENTS.find((x) => x.id === s.student).full_name,
    session_expires_at: new Date(s.expires).toISOString(),
  })],
  ["GET", /^\/api\/catalog\.bin$/, async () => ({
    stages: DB.stages.map((st) => ({
      id: st.id,
      number: st.number,
      title: st.title,
      categories: DB.categories.filter((c) => c.stage === st.id).map((c) => ({
        id: c.id, title: c.title, icon: c.icon || null,
        count: DB.questions.filter((q) => q.category === c.id).length,
      })),
      variants: DB.variants.filter((v) => v.stage === st.id).map((v) => ({ id: v.id, number: v.number })),
    })),
    variants: DB.variants.filter((v) => v.stage == null).map((v) => ({ id: v.id, number: v.number })),
  })],
  ["GET", /^\/api\/categories\/(\d+)\/info\.bin$/, async (s, m) => {
    const c = DB.categories.find((x) => x.id === Number(m[1]));
    if (!c) throw new HttpError(404, "not_found");
    const info = {
      uz: `«${c.title.uz}» bo'limi. Pastdagi raqamlarni bosib savollarga o'ting — Ta'lim rejimida to'g'ri javob yashil rangda ko'rinadi.`,
      kr: `«${c.title.kr}» бўлими. Пастдаги рақамларни босиб саволларга ўтинг.`,
      ru: `Раздел «${c.title.ru}». Нажмите на номера внизу, чтобы перейти к вопросам — в режиме обучения правильный ответ выделен зелёным.`,
    };
    return { id: c.id, title: c.title, info, info_image: c.icon || null };
  }],
  ["POST", /^\/api\/attempts\/start\.bin$/, async (s, m, body) => {
    const kinds = ["study", "category", "stage", "final", "variant"];
    if (!kinds.includes(body.kind)) throw new HttpError(400, "invalid");
    if (body.kind !== "final" && !body.ref) throw new HttpError(400, "invalid", { detail: { ref: "required" } });
    const count = [20, 50].includes(body.count) ? body.count : 20;
    const ids = pick(body.kind, body.ref, count);
    if (!ids.length) throw new HttpError(404, "empty");
    const id = state.nextAttempt++;
    state.attempts[id] = {
      id, student: s.student, kind: body.kind, ref: body.ref ?? null,
      deadline:
        body.kind === "study"
          ? null
          : Date.now() + (ids.length > EXAM_LONG_THRESHOLD ? EXAM_SECONDS_LONG : EXAM_SECONDS) * 1000,
      finished: null,
      items: ids.map((q) => ({ q, chosen: null, correct: null })),
    };
    return [201, serializeAttempt(state.attempts[id])];
  }],
  ["GET", /^\/api\/attempts\/(\d+)\.bin$/, async (s, m) => serializeAttempt(ownAttempt(s, m[1]))],
  ["POST", /^\/api\/attempts\/(\d+)\/answer\.bin$/, async (s, m, body) => {
    const a = ownAttempt(s, m[1]);
    if (a.kind === "study") throw new HttpError(409, "read_only");
    if (!isOpen(a)) {
      finish(a);
      throw new HttpError(409, "finished", { result: resultOf(a) });
    }
    const it = a.items.find((i) => i.q === body.question);
    if (!it) throw new HttpError(404, "not_found");
    if (it.chosen != null) throw new HttpError(409, "already_answered");
    const q = Q.get(it.q);
    const ans = q.answers.find((x) => x.id === body.answer);
    if (!ans) throw new HttpError(404, "not_found");
    it.chosen = ans.id;
    it.correct = ans.correct;
    if (a.kind !== "study" && a.items.every((i) => i.chosen != null)) finish(a);
    return {
      correct: ans.correct,
      correct_answer: q.answers.find((x) => x.correct).id,
      explanation: q.explanation,
      photo_hint: null,
      audio_hint: null,
      finished: !!a.finished,
      result: a.finished ? resultOf(a) : null,
    };
  }],
  ["POST", /^\/api\/attempts\/(\d+)\/finish\.bin$/, async (s, m) => {
    const a = ownAttempt(s, m[1]);
    finish(a);
    return serializeAttempt(a);
  }],
];

export async function handle(req) {
  if (req.path === "/api/auth/login/" && req.method === "POST") return login(req);
  let session;
  try {
    session = await authenticate(req);
  } catch (e) {
    return json(e.status, { error: e.code });
  }
  try {
    await ensureContent();
    for (const [method, re, fn] of routes) {
      const m = re.exec(req.path);
      if (!m || method !== req.method) continue;
      const body = method === "POST" ? await readBody(req, session) : null;
      let out = await fn(session, m, body);
      let status = 200;
      if (Array.isArray(out)) [status, out] = out;
      await persist();
      return { status, contentType: CONTENT_TYPE, body: await seal(session.key, out, { path: req.path, direction: "res" }) };
    }
    throw new HttpError(404, "not_found");
  } catch (e) {
    if (!(e instanceof HttpError)) throw e;
    await persist();
    const payload = { error: e.code, ...e.extra };
    return { status: e.status, contentType: CONTENT_TYPE, body: await seal(session.key, payload, { path: req.path, direction: "res" }) };
  }
}
