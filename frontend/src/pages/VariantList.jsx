import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../AppContext";
import TopBar from "../components/TopBar";
import Loading from "../components/Loading";
import useStart from "../components/useStart";

export default function VariantList() {
  const { t, loadCatalog } = useApp();
  const navigate = useNavigate();
  const [variants, setVariants] = useState(null);
  const [error, setError] = useState(false);
  const { start, busy } = useStart();

  useEffect(() => {
    loadCatalog().then((c) => setVariants(c.variants)).catch(() => setError(true));
  }, [loadCatalog]);

  return (
    <div className="page">
      <TopBar onBack={() => navigate("/")} />
      {!variants ? (
        <Loading error={error} />
      ) : (
        <main className="variant-grid">
          {variants.map((v) => (
            <button
              key={v.id}
              className="variant-btn"
              disabled={busy}
              onClick={() => start({ kind: "variant", ref: v.id }, `${v.number}-${t("variant")}`)}
            >
              {v.number}-{t("variant")}
            </button>
          ))}
        </main>
      )}
    </div>
  );
}
