import { useState } from "react";
import Modal from "./Modal";
import { useApp } from "../AppContext";

/** «20 ta / 50 ta test ishlash» tanlovi. */
export default function CountModal({ title, onClose, onStart, busy }) {
  const { t } = useApp();
  const [count, setCount] = useState(20);
  return (
    <Modal
      title={title}
      onClose={onClose}
      footer={
        <button className="btn-white" disabled={busy} onClick={() => onStart(count)}>
          {t("start")}
        </button>
      }
    >
      {[20, 50].map((n) => (
        <button key={n} className={`choice ${count === n ? "selected" : ""}`} onClick={() => setCount(n)}>
          {t(n === 20 ? "do20" : "do50")}
          {count === n && <span className="check">✓</span>}
        </button>
      ))}
    </Modal>
  );
}
