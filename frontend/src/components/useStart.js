import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { post } from "../lib/api";

/** Testni serverda boshlaydi va pleyerga o'tadi (ma'lumot state orqali uzatiladi). */
export default function useStart() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const start = async (payload, title) => {
    setBusy(true);
    setError(null);
    try {
      const attempt = await post("/attempts/start.bin", payload);
      navigate(`/test/${attempt.id}`, { state: { attempt, title } });
    } catch (e) {
      setError(e.code || "error");
    } finally {
      setBusy(false);
    }
  };
  return { start, busy, error };
}
