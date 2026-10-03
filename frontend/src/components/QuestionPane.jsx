import { useEffect, useState } from "react";
import { useApp } from "../AppContext";
import { tr } from "../i18n";
import { BinAudio, BinImage } from "./BinMedia";
import Modal from "./Modal";

/** Savol + F1..F5 javoblar + rasm. Javob holati serverdan keladi. */
export default function QuestionPane({ question, onAnswer, timer, showHints, locked }) {
  const { t, lang } = useApp();
  const [hint, setHint] = useState(null); // "audio" | "photo"
  const [pending, setPending] = useState(null);

  useEffect(() => {
    setHint(null);
    setPending(null);
  }, [question.id]);

  const answered = question.chosen != null;
  const choose = (a) => {
    if (answered || locked || pending) return;
    setPending(a.id);
    Promise.resolve(onAnswer(a.id)).finally(() => setPending(null));
  };

  // F1..F5 klavishlari (skrinshotdagi kabi)
  useEffect(() => {
    const onKey = (e) => {
      const m = /^F([1-9])$/.exec(e.key);
      if (!m) return;
      e.preventDefault();
      const a = question.answers[Number(m[1]) - 1];
      if (a) choose(a);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const stateOf = (a) => {
    if (question.correct != null && a.id === question.correct && (answered || showHints)) return "right";
    if (answered && a.id === question.chosen && a.id !== question.correct) return "wrong";
    if (pending === a.id) return "pending";
    return "";
  };

  return (
    <>
      <div className="q-banner">{tr(question.text, lang)}</div>
      <div className="q-body">
        <div className="q-answers">
          {question.answers.map((a, i) => (
            <button key={a.id} className={`answer ${stateOf(a)}`} onClick={() => choose(a)} disabled={answered || locked}>
              <span className="fkey">F{i + 1}</span>
              <span className="answer-text">{tr(a.text, lang)}</span>
            </button>
          ))}
          {showHints && (question.audio_hint || question.photo_hint) && (
            <div className="hints">
              <button className="hint-btn" disabled={!question.audio_hint} onClick={() => setHint("audio")}>
                ▶ ◀◀ ▶▶ {t("audioHint")}
              </button>
              <button className="hint-btn" disabled={!question.photo_hint} onClick={() => setHint("photo")}>
                🖼 {t("photoHint")}
              </button>
            </div>
          )}
          {hint === "audio" && <BinAudio src={question.audio_hint} />}
          {(answered || showHints) && tr(question.explanation, lang) && (
            <div className="explanation">{tr(question.explanation, lang)}</div>
          )}
        </div>
        <div className="q-media">
          {timer && <div className="timer">{timer}</div>}
          <BinImage src={question.image} className="q-image" />
        </div>
      </div>
      {hint === "photo" && (
        <Modal title={t("photoHint")} onClose={() => setHint(null)}>
          <BinImage src={question.photo_hint} className="hint-image" fallback={false} />
        </Modal>
      )}
    </>
  );
}
