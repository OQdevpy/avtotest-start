import { useEffect, useState } from "react";
import { media } from "../lib/api";
import Placeholder from "./Placeholder";

function useBinUrl(ref) {
  const [url, setUrl] = useState(null);
  useEffect(() => {
    if (!ref) {
      setUrl(null);
      return undefined;
    }
    let alive = true;
    let created = null;
    media(ref)
      .then((u) => {
        created = u;
        if (alive) setUrl(u);
        else URL.revokeObjectURL(u);
      })
      .catch(() => alive && setUrl(null));
    return () => {
      alive = false;
      if (created) URL.revokeObjectURL(created);
      setUrl(null);
    };
  }, [ref]);
  return url;
}

// Shifrlangan backend uchun havola: "question/5/image" yoki "category/3/icon".
// Aks holda — oddiy fayl nomi (demo), u public/media/ dan to'g'ridan-to'g'ri o'qiladi.
const isEncryptedRef = (src) => /^(question|category)\/\d+\/[a-z_]+$/.test(src);
const directUrl = (src) => `${import.meta.env.BASE_URL || "/"}media/${src}`;

/** Rasm. Shifrlangan backendda — .bin orqali; demoda — media/ dan to'g'ridan-to'g'ri.
 *  Rasm bo'lmasa yoki yuklanmasa — chiroyli «rasm yo'q» o'rindig'i. */
export function BinImage({ src, alt = "", className = "", fallback = true }) {
  const encrypted = src && isEncryptedRef(src);
  const binUrl = useBinUrl(encrypted ? src : null);
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [src]);

  if (!src || failed || (encrypted && !binUrl)) {
    return fallback ? <Placeholder className={className} /> : null;
  }
  const url = encrypted ? binUrl : directUrl(src);
  return (
    <img
      className={className}
      src={url}
      alt={alt}
      draggable={false}
      onContextMenu={(e) => e.preventDefault()}
      onError={() => setFailed(true)}
    />
  );
}

export function BinAudio({ src }) {
  const url = useBinUrl(src);
  if (!url) return null;
  return <audio src={url} controls autoPlay controlsList="nodownload" />;
}
