import { LANGS } from "../i18n";
import { useApp } from "../AppContext";

export default function TopBar({ title, onBack, right }) {
  const { lang, setLang, t } = useApp();
  return (
    <header className="topbar">
      <div className="langs">
        {LANGS.map((l) => (
          <button key={l.code} className={`lang ${lang === l.code ? "active" : ""}`} onClick={() => setLang(l.code)}>
            {l.label}
          </button>
        ))}
      </div>
      <div className="topbar-title">{title}</div>
      <div className="topbar-right">
        {right}
        {onBack && (
          <button className="link-btn" onClick={onBack}>
            <span aria-hidden="true">←</span> {t("back")}
          </button>
        )}
      </div>
    </header>
  );
}
