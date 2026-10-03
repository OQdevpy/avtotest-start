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

/** Shifrlangan .bin rasm. Rasm bo'lmasa — «Avtostart» logotipi. */
export function BinImage({ src, alt = "", className = "", fallback = true }) {
  const url = useBinUrl(src);
  if (!src || !url) return fallback ? <Placeholder className={className} /> : null;
  return <img className={className} src={url} alt={alt} draggable={false} onContextMenu={(e) => e.preventDefault()} />;
}

export function BinAudio({ src }) {
  const url = useBinUrl(src);
  if (!url) return null;
  return <audio src={url} controls autoPlay controlsList="nodownload" />;
}
