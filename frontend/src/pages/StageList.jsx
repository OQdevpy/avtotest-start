import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../AppContext";
import TopBar from "../components/TopBar";
import CountModal from "../components/CountModal";
import Loading from "../components/Loading";
import useStart from "../components/useStart";

/** mode="talim" — bo'limlarga o'tadi; mode="test" — 20/50 tanlab bosqich testi. */
export default function StageList({ mode }) {
  const { t, loadCatalog } = useApp();
  const navigate = useNavigate();
  const [catalog, setCatalog] = useState(null);
  const [error, setError] = useState(false);
  const [selected, setSelected] = useState(null);
  const { start, busy } = useStart();

  useEffect(() => {
    loadCatalog().then(setCatalog).catch(() => setError(true));
  }, [loadCatalog]);

  const title = mode === "talim" ? t("talim") : t("stageTest");
  const stageLabel = (s) => `${s.number} - ${t("stage")}`;

  return (
    <div className="page">
      <TopBar title={title} onBack={() => navigate("/")} />
      {!catalog ? (
        <Loading error={error} />
      ) : (
        <main className="stage-row">
          {catalog.stages.map((s) => (
            <button
              key={s.id}
              className="stage-btn"
              onClick={() => (mode === "talim" ? navigate(`/talim/${s.id}`) : setSelected(s))}
            >
              {stageLabel(s)}
            </button>
          ))}
        </main>
      )}
      {selected && (
        <CountModal
          title={t("stageTest")}
          busy={busy}
          onClose={() => setSelected(null)}
          onStart={(count) => start({ kind: "stage", ref: selected.id, count }, stageLabel(selected))}
        />
      )}
    </div>
  );
}
