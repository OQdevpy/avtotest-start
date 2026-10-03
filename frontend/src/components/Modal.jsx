import { useEffect } from "react";

export default function Modal({ title, onClose, children, footer, variant = "blue" }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose?.();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose?.()}>
      <div className={`modal modal-${variant}`} role="dialog" aria-modal="true">
        {title && (
          <div className="modal-head">
            <h3>{title}</h3>
            {onClose && (
              <button className="modal-x" onClick={onClose} aria-label="close">
                ✕
              </button>
            )}
          </div>
        )}
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}
