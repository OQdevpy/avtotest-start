// Sessiya IndexedDB'da saqlanadi: CryptoKey obyekti structured clone orqali
// saqlanadi va eksport qilinmaydigan bo'lib qoladi (localStorage'ga yozib bo'lmaydi).

const DB = "avtostart";
const STORE = "kv";

function db() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
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

export const kvGet = (k) => tx("readonly", (s) => s.get(k));
export const kvSet = (k, v) => tx("readwrite", (s) => s.put(v, k));
export const kvDel = (k) => tx("readwrite", (s) => s.delete(k));

export async function deviceId() {
  let id = await kvGet("device_id");
  if (!id) {
    const b = crypto.getRandomValues(new Uint8Array(24));
    id = Array.from(b, (x) => x.toString(16).padStart(2, "0")).join("");
    await kvSet("device_id", id);
  }
  return id;
}
