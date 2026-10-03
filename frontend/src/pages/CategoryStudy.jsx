import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useApp } from "../AppContext";
import { tr } from "../i18n";
import { get, post } from "../lib/api";
import { submitAnswer } from "../lib/attempt";
import TopBar from "../components/TopBar";
import Loading from "../components/Loading";
import QuestionPane from "../components/QuestionPane";
import Pager from "../components/Pager";
import { BinImage } from "../components/BinMedia";
import useStart from "../components/useStart";

/** Ta'lim: «i» — bo'lim ma'lumoti, so'ng savollar (to'g'ri javob ko'rinadi). */
export default function CategoryStudy() {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  const { t, lang } = useApp();
  const [info, setInfo] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [error, setError] = useState(false);
  const [current, setCurrent] = useState(-1); // -1 = ma'lumot
  const started = useRef(null);
  const { start, busy } = useStart();

  useEffect(() => {
    if (started.current === categoryId) return; // StrictMode ikki marta chaqirmasin
    started.current = categoryId;
    setAttempt(null);
    setCurrent(-1);
    Promise.all([
      get(`/categories/${categoryId}/info.bin`),
      post("/attempts/start.bin", { kind: "study", ref: Number(categoryId) }).catch((e) =>
        e.code === "empty" ? { questions: [] } : Promise.reject(e),
      ),
    ])
      .then(([i, a]) => {
        setInfo(i);
        setAttempt(a);
      })
      .catch(() => setError(true));
  }, [categoryId]);

  if (!info || !attempt) {
    return (
      <div className="page">
        <TopBar onBack={() => navigate(-1)} />
        <Loading error={error} />
      </div>
    );
  }

  const title = tr(info.title, lang);
  const onAnswer = async (answerId) => {
    const next = await submitAnswer(attempt, attempt.questions[current].id, answerId);
    setAttempt(next);
  };

  return (
    <div className="page">
      <TopBar
        title={title}
        onBack={() => navigate(-1)}
        right={
          attempt.questions.length > 0 && (
            <button
              className="btn-green"
              disabled={busy}
              onClick={() => start({ kind: "category", ref: Number(categoryId) }, title)}
            >
              {t("partTest")}
            </button>
          )
        }
      />
      <main className="player">
        {current < 0 ? (
          <>
            <div className="q-banner">{t("info")}</div>
            <div className="q-body">
              <div className="q-answers info-text">{tr(info.info, lang)}</div>
              <div className="q-media">
                {info.info_image && <BinImage src={info.info_image} className="q-image white" />}
              </div>
            </div>
          </>
        ) : (
          <QuestionPane question={attempt.questions[current]} onAnswer={onAnswer} showHints />
        )}
        <Pager
          questions={attempt.questions}
          current={current}
          onSelect={setCurrent}
          withInfo
          infoActive={current < 0}
          onInfo={() => setCurrent(-1)}
        />
      </main>
    </div>
  );
}
