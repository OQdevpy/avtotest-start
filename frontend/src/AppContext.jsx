import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "./lib/api";
import { t as translate } from "./i18n";

const Ctx = createContext(null);

function initialLang() {
  try {
    return localStorage.getItem("lang") || "uz";
  } catch {
    return "uz";
  }
}

export function AppProvider({ children }) {
  const [lang, setLangState] = useState(initialLang);
  const [user, setUser] = useState(undefined); // undefined = tekshirilmoqda
  const [catalog, setCatalog] = useState(null);
  const navigate = useNavigate();

  const setLang = (l) => {
    setLangState(l);
    try {
      localStorage.setItem("lang", l);
    } catch {
      /* private rejim */
    }
  };

  useEffect(() => {
    document.documentElement.lang = lang === "ru" ? "ru" : "uz";
  }, [lang]);

  useEffect(() => {
    api.setLogoutHandler(() => {
      setUser(null);
      setCatalog(null);
      navigate("/login", { replace: true });
    });
    api.restoreSession().then((s) => setUser(s ? { name: s.name } : null)).catch(() => setUser(null));
  }, [navigate]);

  const loadCatalog = useCallback(async () => {
    if (catalog) return catalog;
    const c = await api.get("/catalog.bin");
    setCatalog(c);
    return c;
  }, [catalog]);

  const login = async (code) => {
    const s = await api.login(code);
    setUser({ name: s.name });
  };

  const logout = async () => {
    await api.logout();
    setUser(null);
    setCatalog(null);
    navigate("/login", { replace: true });
  };

  const t = useCallback((key) => translate(key, lang), [lang]);

  return (
    <Ctx.Provider value={{ lang, setLang, t, user, login, logout, catalog, loadCatalog }}>
      {children}
    </Ctx.Provider>
  );
}

export const useApp = () => useContext(Ctx);
