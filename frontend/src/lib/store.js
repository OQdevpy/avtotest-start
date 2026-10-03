// Sessiya IndexedDB'da saqlanadi: CryptoKey obyekti structured clone orqali
// saqlanadi va eksport qilinmaydigan bo'lib qoladi (localStorage'ga yozib bo'lmaydi).
// IndexedDB yopiq bo'lsa (private rejim va h.k.) — xotiradagi zaxira.

const DB = "avtostart";
const STORE = "kv";
const memory = new Map();
let dbPromise = null;

function db() {
  if (!dbPromise) {
    dbPromise = new Promise((resolve, reject) => {
      const req = indexedDB.open(DB, 1);
      req.onupgradeneeded = () => req.result.createObjectStore(STORE);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
  return dbPromise;
}

async function tx(mode, fn) {
  const d = await db();
  return new Promise((resolve, reject) => {
    const t = d.transaction(STORE, mode);
    const r = fn(t.objectStore(STORE));
    t.oncomplete = () => resolve(r?.result);
    t.onerror = () => reject(t.error);
  });
}

export async function kvGet(k) {
  try {
    return await tx("readonly", (s) => s.get(k));
  } catch {
    return memory.get(k);
  }
}

export async function kvSet(k, v) {
  try {
    await tx("readwrite", (s) => s.put(v, k));
  } catch {
    memory.set(k, v);
  }
}

export async function kvDel(k) {
  try {
    await tx("readwrite", (s) => s.delete(k));
  } catch {
    memory.delete(k);
  }
}

export async function deviceId() {
  let id = await kvGet("device_id");
  if (!id) {
    const b = crypto.getRandomValues(new Uint8Array(24));
    id = Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
    await kvSet("device_id", id);
  }
  return id;
}
