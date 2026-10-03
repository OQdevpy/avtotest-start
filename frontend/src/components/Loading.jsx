import { useApp } from "../AppContext";

export default function Loading({ error }) {
  const { t } = useApp();
  return <div className="center-msg">{error ? t("err_generic") : t("loading")}</div>;
}
