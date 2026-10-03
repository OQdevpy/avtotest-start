import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../AppContext";
import TopBar from "../components/TopBar";
import Modal from "../components/Modal";
import CountModal from "../components/CountModal";
import useStart from "../components/useStart";

const Bulb = () => (
  <svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-4 12.7V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.3A7 7 0 0 0 12 2zM9 20h6v1a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1z" /></svg>
);
const Chart = () => (
  <svg viewBox="0 0 24 24"><path d="M3 3h2v16h16v2H3zM8 11h3v6H8zm5-4h3v10h-3zm5 3h3v7h-3z" /></svg>
);
const Checklist = () => (
  <svg viewBox="0 0 24 24"><path d="M3.5 5.5 5 7l3-3 1 1-4 4-2.5-2.5zM3.5 11.5 5 13l3-3 1 1-4 4-2.5-2.5zM11 5h10v2H11zm0 6h10v2H11zm0 6h10v2H11zM5 17.5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z" /></svg>
);
const Layers = () => (
  <svg viewBox="0 0 24 24"><path d="m12 2 10 5-10 5L2 7zm-7.8 8.6L12 14.5l7.8-3.9L22 12l-10 5-10-5zm0 5L12 19.5l7.8-3.9L22 17l-10 5-10-5z" /></svg>
);

export default function Home() {
  const { t, logout } = useApp();
  const navigate = useNavigate();
  const [modal, setModal] = useState(null);
  const { start, busy } = useStart();

  const tiles = [
    { key: "talim", color: "red", icon: <Bulb />, go: () => navigate("/talim") },
    { key: "stageTest", color: "yellow", icon: <Chart />, go: () => navigate("/bosqichli") },
    { key: "finalTest", color: "cyan", icon: <Checklist />, go: () => setModal("final") },
    { key: "variants", color: "green", icon: <Layers />, go: () => navigate("/variantlar") },
    { key: "stageVariants", color: "purple", icon: <Layers />, go: () => navigate("/bolim-variantlar") },
  ];

  return (
    <div className="page">
      <TopBar
        right={
          <button className="link-btn" onClick={() => setModal("logout")}>
            <span aria-hidden="true">⇥</span> {t("logout")}
          </button>
        }
      />
      <main className="tiles">
        {tiles.map((tile) => (
          <button key={tile.key} className={`tile tile-${tile.color}`} onClick={tile.go}>
            <span className="tile-icon">{tile.icon}</span>
            <span className="tile-label">{t(tile.key)}</span>
          </button>
        ))}
      </main>

      {modal === "final" && (
        <CountModal
          title={t("finalTest")}
          busy={busy}
          onClose={() => setModal(null)}
          onStart={(count) => start({ kind: "final", count }, t("finalTest"))}
        />
      )}
      {modal === "logout" && (
        <Modal
          title={t("logout")}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn-grey" onClick={() => setModal(null)}>{t("cancel")}</button>
              <button className="btn-red" onClick={logout}>{t("yes")}</button>
            </>
          }
        >
          <p className="modal-text">{t("logoutConfirm")}</p>
        </Modal>
      )}
    </div>
  );
}
