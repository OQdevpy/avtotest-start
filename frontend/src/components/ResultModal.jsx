import Modal from "./Modal";
import { useApp } from "../AppContext";

export default function ResultModal({ result, timeUp, onClose, onReview }) {
  const { t } = useApp();
  return (
    <Modal
      title={timeUp ? t("timeUp") : t("result")}
      onClose={onReview}
      footer={<button className="btn-white" onClick={onClose}>{t("back")}</button>}
    >
      <div className={`result ${result.passed ? "pass" : "fail"}`}>
        <div className="result-big">
          {result.correct} / {result.total}
        </div>
        <div>
          {t("correct")}: {result.correct} · {t("mistakes")}: {result.mistakes}
        </div>
        <div className="result-verdict">{result.passed ? t("passed") : t("failed")}</div>
      </div>
    </Modal>
  );
}
