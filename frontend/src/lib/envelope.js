// .bin konvert formati — backend/binproto/crypto.py bilan aynan bir xil.
//
//   "AVS1" (4) | flags (1) | nonce (12) | AES-256-GCM(ciphertext + tag 16)
//
// flags: 1 — zlib bilan siqilgan JSON, 2 — xom bayt (rasm/audio).
// AAD = magic + flags + yo'nalish ("req"/"res") + "|" + yo'l.

export const MAGIC = new Uint8Array([0x41, 0x56, 0x53, 0x31]); // "AVS1"
export const FLAG_JSON = 1;
export const FLAG_RAW = 2;
export const CONTENT_TYPE = "application/octet-stream";
const NONCE_LEN = 12;
const HEADER_LEN = 4 + 1 + NONCE_LEN;
const enc = new TextEncoder();
const dec = new TextDecoder();

function concat(...parts) {
  const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
  let i = 0;
  for (const p of parts) {
    out.set(p, i);
    i += p.length;
  }
  return out;
}

function aad(flags, direction, path) {
  return concat(MAGIC, new Uint8Array([flags]), enc.encode(`${direction}|${path}`));
}

async function pipe(bytes, stream) {
  const res = new Response(new Blob([bytes]).stream().pipeThrough(stream));
  return new Uint8Array(await res.arrayBuffer());
}

// CompressionStream("deflate") — RFC 1950 (zlib) formati, Python zlib bilan mos.
export const deflate = (b) => pipe(b, new CompressionStream("deflate"));
export const inflate = (b) => pipe(b, new DecompressionStream("deflate"));

export async function seal(key, payload, { path, direction }) {
  const body = await deflate(enc.encode(JSON.stringify(payload)));
  const nonce = crypto.getRandomValues(new Uint8Array(NONCE_LEN));
  const ct = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce, additionalData: aad(FLAG_JSON, direction, path) },
    key,
    body,
  );
  return concat(MAGIC, new Uint8Array([FLAG_JSON]), nonce, new Uint8Array(ct));
}

export async function open(key, buffer, { path, direction }) {
  const blob = new Uint8Array(buffer);
  if (blob.length < HEADER_LEN + 16 || MAGIC.some((b, i) => blob[i] !== b)) {
    throw new Error("bad_envelope");
  }
  const flags = blob[4];
  const nonce = blob.slice(5, HEADER_LEN);
  const plain = new Uint8Array(
    await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: nonce, additionalData: aad(flags, direction, path) },
      key,
      blob.slice(HEADER_LEN),
    ),
  );
  if (flags === FLAG_JSON) return { flags, data: JSON.parse(dec.decode(await inflate(plain))) };
  if (flags === FLAG_RAW) {
    const mlen = plain[0];
    return { flags, mime: dec.decode(plain.slice(1, 1 + mlen)), data: plain.slice(1 + mlen) };
  }
  throw new Error("bad_flags");
}

// --- ECDH P-256 + HKDF-SHA256 → AES-256-GCM (eksport qilinmaydigan) ---

const HKDF_INFO = "avtostart-bin-v1:";

export const b64e = (u8) => btoa(String.fromCharCode(...u8));
export const b64d = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

export async function newKeyPair() {
  // Maxfiy kalit extractable=false: JS ham uni o'qiy olmaydi.
  return crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, false, ["deriveBits"]);
}

export async function exportPublic(pair) {
  return new Uint8Array(await crypto.subtle.exportKey("raw", pair.publicKey));
}

export async function deriveKey(pair, serverPubRaw, salt, sid) {
  const serverPub = await crypto.subtle.importKey(
    "raw", serverPubRaw, { name: "ECDH", namedCurve: "P-256" }, false, [],
  );
  const shared = await crypto.subtle.deriveBits({ name: "ECDH", public: serverPub }, pair.privateKey, 256);
  const ikm = await crypto.subtle.importKey("raw", shared, "HKDF", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "HKDF", hash: "SHA-256", salt, info: enc.encode(HKDF_INFO + sid) },
    ikm,
    { name: "AES-GCM", length: 256 },
    false, // AES kaliti ham eksport qilinmaydi
    ["encrypt", "decrypt"],
  );
}

/** Xom baytni (rasm/audio) muhrlash — FLAG_RAW, ichida [mime uzunligi][mime][bayt]. */
export async function sealRaw(key, mime, bytes, { path, direction }) {
  const m = enc.encode(mime).slice(0, 255);
  const body = concat(new Uint8Array([m.length]), m, bytes);
  const nonce = crypto.getRandomValues(new Uint8Array(NONCE_LEN));
  const ct = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce, additionalData: aad(FLAG_RAW, direction, path) },
    key,
    body,
  );
  return concat(MAGIC, new Uint8Array([FLAG_RAW]), nonce, new Uint8Array(ct));
}
