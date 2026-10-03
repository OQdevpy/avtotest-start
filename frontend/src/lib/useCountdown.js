import { useEffect, useRef, useState } from "react";

/** Server bergan qolgan soniyalardan hisoblaydi (mijoz soatiga bog'liq emas). */
export default function useCountdown(seconds, onExpire) {
  const endRef = useRef(null);
  const [left, setLeft] = useState(seconds);
  const cb = useRef(onExpire);
  cb.current = onExpire;

  useEffect(() => {
    if (seconds == null) return undefined;
    endRef.current = performance.now() + seconds * 1000;
    setLeft(seconds);
    let fired = false;
    const id = setInterval(() => {
      const s = Math.max(0, Math.round((endRef.current - performance.now()) / 1000));
      setLeft(s);
      if (s === 0 && !fired) {
        fired = true;
        clearInterval(id);
        cb.current?.();
      }
    }, 250);
    return () => clearInterval(id);
  }, [seconds]);

  return left;
}

export function fmt(s) {
  if (s == null) return null;
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${h} : ${String(m).padStart(2, "0")} : ${String(sec).padStart(2, "0")}`;
}
