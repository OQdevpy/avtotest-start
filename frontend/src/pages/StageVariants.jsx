import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../AppContext";
import TopBar from "../components/TopBar";
import Loading from "../components/Loading";
import useStart from "../components/useStart";

export default function StageVariants() {
  const { t, loadCatalog } = useApp();
  const navigate = useNavigate();
  const [stages, setStages] = useState(null);
  const [error, setError] = useState(false);
  const { start, busy } = useStart();

  useEffect(() => {
    loadCatalog().then((c) => setStages(c.stages)).catch(() => setError(true));
  }, [loadCatalog]);

  return (
    <div className="page">
      <TopBar onBack={() => navigate("/")} />
      {!stages ? (
        <Loading error={error} />
      ) : (
        <main className="stage-variants">
          {stages.map((s) => (
            <section key={s.id}>
              <h2>
                {s.number} - {t("stage")}
              </h2>
              <div className="variant-grid five">
                {s.variants.map((v) => (
                  <button
                    key={v.id}
                    className="variant-btn"
                    disabled={busy}
                    onClick={() =>
                      start({ kind: "variant", ref: v.id }, `${s.number} - ${t("stage")} · ${v.number} ${t("variant")}`)
                    }
                  >
                    {v.number} {t("variant")}
                  </button>
                ))}
              </div>
            </section>
          ))}
        </main>
      )}
    </div>
  );
}
