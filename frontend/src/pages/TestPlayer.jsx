import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useApp } from "../AppContext";
import { get, post } from "../lib/api";
import { submitAnswer } from "../lib/attempt";
import useCountdown, { fmt } from "../lib/useCountdown";
import TopBar from "../components/TopBar";
import Loading from "../components/Loading";
import QuestionPane from "../components/QuestionPane";
import Pager from "../components/Pager";
import Modal from "../components/Modal";
import ResultModal from "../components/ResultModal";

export default function TestPlayer() {
  const { attemptId } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();
  const { t } = useApp();
  const [attempt, setAttempt] = useState(state?.attempt || null);
  const [error, setError] = useState(false);
  const [current, setCurrent] = useState(0);
  const [confirmBack, setConfirmBack] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [timeUp, setTimeUp] = useState(false);
  const attemptRef = useRef(attempt);
  attemptRef.current = attempt;

  useEffect(() => {
    if (attempt && String(attempt.id) === attemptId) return;
    get(`/attempts/${attemptId}.bin`)
      .then((a) => {
        setAttempt(a);
        const firstOpen = a.questions.findIndex((q) => q.chosen == null);
        setCurrent(firstOpen < 0 ? 0 : firstOpen);
      })
      .catch(() => setError(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attemptId]);

  const finish = useCallback(async () => {
    const a = attemptRef.current;
    if (!a || a.finished) return a;
    const done = await post(`/attempts/${a.id}/finish.bin`, {});
    setAttempt(done);
    return done;
  }, []);

  const left = useCountdown(attempt && !attempt.finished ? attempt.remaining : null, async () => {
    setTimeUp(true);
    await finish().catch(() => {});
    setShowResult(true);
  });

  const onAnswer = async (answerId) => {
    const q = attempt.questions[current];
    try {
      const next = await submitAnswer(attempt, q.id, answerId);
      setAttempt(next);
      if (next.finished) {
        setTimeout(() => setShowResult(true), 700);
        return;
      }
      // Keyingi javobsiz savolga o'tish
      const after = next.questions.findIndex((x, i) => i > current && x.chosen == null);
      const any = next.questions.findIndex((x) => x.chosen == null);
      const target = after >= 0 ? after : any;
      if (target >= 0) setTimeout(() => setCurrent(target), 700);
    } catch (e) {
      if (e.code === "finished") {
        await finish().catch(() => {});
        setShowResult(true);
      }
    }
  };

  useEffect(() => {
    const onKey = (e) => {
      if (!attempt) return;
      if (e.key === "ArrowRight") setCurrent((c) => Math.min(c + 1, attempt.questions.length - 1));
      if (e.key === "ArrowLeft") setCurrent((c) => Math.max(c - 1, 0));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [attempt]);

  const leave = async () => {
    await finish().catch(() => {});
    navigate(-1);
  };

  if (!attempt) {
    return (
      <div className="page">
        <TopBar onBack={() => navigate("/")} />
        <Loading error={error} />
      </div>
    );
  }

  const q = attempt.questions[current];
  return (
    <div className="page no-select" onContextMenu={(e) => e.preventDefault()}>
      <TopBar
        title={state?.title || ""}
        onBack={() => (attempt.finished ? navigate(-1) : setConfirmBack(true))}
      />
      <main className="player">
        <QuestionPane
          question={q}
          onAnswer={onAnswer}
          locked={attempt.finished}
          showHints={attempt.finished}
          timer={attempt.finished ? null : fmt(left)}
        />
        <Pager questions={attempt.questions} current={current} onSelect={setCurrent} />
      </main>

      {confirmBack && (
        <Modal variant="white" onClose={() => setConfirmBack(false)}>
          <p className="modal-text center">{t("leaveTest")}</p>
          <div className="modal-actions">
            <button className="btn-blue" onClick={leave}>{t("yes")}</button>
            <button className="btn-grey" onClick={() => setConfirmBack(false)}>{t("no")}</button>
          </div>
        </Modal>
      )}
      {showResult && attempt.result && (
        <ResultModal
          result={attempt.result}
          timeUp={timeUp}
          onReview={() => setShowResult(false)}
          onClose={() => navigate(-1)}
        />
      )}
    </div>
  );
}
