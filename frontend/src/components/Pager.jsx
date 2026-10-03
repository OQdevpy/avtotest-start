/** Raqamli navigatsiya: yashil — to'g'ri, qizil — xato, ramka — joriy. */
export default function Pager({ questions, current, onSelect, withInfo, infoActive, onInfo }) {
  return (
    <nav className="pager">
      {withInfo && (
        <button className={`page-num info ${infoActive ? "current" : ""}`} onClick={onInfo}>
          i
        </button>
      )}
      {questions.map((q, i) => {
        const cls = q.chosen == null ? "" : q.chosen === q.correct ? "ok" : "bad";
        return (
          <button
            key={q.id}
            className={`page-num ${cls} ${!infoActive && i === current ? "current" : ""}`}
            onClick={() => onSelect(i)}
          >
            {i + 1}
          </button>
        );
      })}
    </nav>
  );
}
