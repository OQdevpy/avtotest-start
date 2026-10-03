export default function Placeholder({ className = "" }) {
  return (
    <div className={`placeholder ${className}`}>
      <svg viewBox="0 0 800 520" aria-label="Avtostart">
        <g fill="#8a8a8a">
          <rect x="70" y="40" width="70" height="95" rx="4" />
          <circle cx="62" cy="120" r="18" />
          <rect x="40" y="140" width="45" height="45" rx="10" />
          <circle cx="130" cy="140" r="18" />
          <rect x="108" y="160" width="45" height="25" rx="10" />
          <text x="190" y="160" fontFamily="Lato, Arial" fontWeight="900" fontSize="140">Avtostart</text>
        </g>
        <g>
          <path d="M210 470 Q215 330 300 300 L360 230 Q400 210 440 230 L500 300 Q585 330 590 470 Z" fill="#050505" />
          <path d="M300 300 L360 232 Q400 214 440 232 L500 300" fill="none" stroke="#9aa3b5" strokeWidth="3" />
          <path d="M215 360 Q400 330 585 360" fill="none" stroke="#596173" strokeWidth="2" />
          <circle cx="285" cy="380" r="13" fill="none" stroke="#e5e7eb" strokeWidth="4" />
          <circle cx="306" cy="384" r="8" fill="none" stroke="#e5e7eb" strokeWidth="3" />
          <circle cx="515" cy="380" r="13" fill="none" stroke="#e5e7eb" strokeWidth="4" />
          <circle cx="494" cy="384" r="8" fill="none" stroke="#e5e7eb" strokeWidth="3" />
        </g>
      </svg>
    </div>
  );
}
