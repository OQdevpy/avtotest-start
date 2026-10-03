import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useApp } from "../AppContext";
import { tr } from "../i18n";
import TopBar from "../components/TopBar";
import Loading from "../components/Loading";
import { BinImage } from "../components/BinMedia";

export default function CategoryGrid() {
  const { stageId } = useParams();
  const { t, lang, loadCatalog } = useApp();
  const navigate = useNavigate();
  const [stage, setStage] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    loadCatalog()
      .then((c) => setStage(c.stages.find((s) => String(s.id) === stageId) || null))
      .catch(() => setError(true));
  }, [loadCatalog, stageId]);

  return (
    <div className="page">
      <TopBar title={stage ? `${stage.number} - ${t("stage")}` : ""} onBack={() => navigate("/talim")} />
      {!stage ? (
        <Loading error={error} />
      ) : (
        <main className="cat-grid">
          {stage.categories.map((c) => (
            <button key={c.id} className="cat-card" onClick={() => navigate(`/bolim/${c.id}`)}>
              <div className="cat-icon">
                <BinImage src={c.icon} alt="" />
              </div>
              <div className="cat-label">
                <strong>{tr(c.title, lang)}</strong>
                <small>
                  {t("questionsCount")}: {c.count}
                </small>
              </div>
            </button>
          ))}
        </main>
      )}
    </div>
  );
}
