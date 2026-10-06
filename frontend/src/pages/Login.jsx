import { useState } from "react";
import { useApp } from "../AppContext";
import TopBar from "../components/TopBar";
import { DEMO } from "../lib/transport";
import { STUDENTS } from "../lib/demoUsers";

export default function Login() {
  const { login, t } = useApp();
  const [code, setCode] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!window.crypto?.subtle) {
      setError("err_crypto");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await login(code.trim());
    } catch (err) {
      const key = `err_${err.code}`;
      setError(t(key) !== key ? key : "err_generic");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page">
      <TopBar />
      <form className="login-card" onSubmit={submit} autoComplete="off">
        <img className="login-logo" src={`${import.meta.env.BASE_URL || "/"}logo.webp`} alt="pravaexpress.uz" />
        <h2>{t("loginTitle")}</h2>
        <label htmlFor="code">{t("code")}</label>
        <input
          id="code"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          maxLength={32}
          placeholder="XXXX-XXXX-XXXX"
          spellCheck={false}
          autoFocus
        />
        {error && <div className="form-error">{t(error)}</div>}
        <button className="btn-primary" disabled={busy || code.length < 4}>
          {busy ? t("loading") : t("enter")}
        </button>
        {DEMO && (
          <div className="demo-users">
            <div className="demo-title">Demo foydalanuvchilar — bosing, kod to'ldiriladi</div>
            {STUDENTS.map((s) => (
              <button type="button" key={s.code} className="demo-user" onClick={() => setCode(s.code)}>
                <span>{s.full_name}</span>
                <code>{s.code}</code>
                <small>{s.note}</small>
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  );
}
