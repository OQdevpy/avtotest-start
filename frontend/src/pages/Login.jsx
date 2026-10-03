import { useState } from "react";
import { useApp } from "../AppContext";
import TopBar from "../components/TopBar";

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
      </form>
    </div>
  );
}
