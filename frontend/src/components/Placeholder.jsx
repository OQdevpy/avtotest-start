// Rasm bo'lmaganda ko'rsatiladigan chiroyli o'rindiq (AvtoStart brendida).
export default function Placeholder({ className = "" }) {
  return (
    <div className={`placeholder ${className}`}>
      <svg viewBox="0 0 820 540" preserveAspectRatio="xMidYMid slice" aria-label="AvtoStart" role="img">
        <defs>
          <linearGradient id="ph-bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#0b1733" />
            <stop offset="0.55" stopColor="#0a1229" />
            <stop offset="1" stopColor="#060b1c" />
          </linearGradient>
          <linearGradient id="ph-badge" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#2563eb" />
            <stop offset="1" stopColor="#22d3ee" />
          </linearGradient>
          <radialGradient id="ph-glow" cx="0.5" cy="0.42" r="0.5">
            <stop offset="0" stopColor="#1d4ed8" stopOpacity="0.35" />
            <stop offset="1" stopColor="#1d4ed8" stopOpacity="0" />
          </radialGradient>
        </defs>

        <rect width="820" height="540" fill="url(#ph-bg)" />
        <rect width="820" height="540" fill="url(#ph-glow)" />

        {/* yengil to'lqin chiziqlar — sayt foni bilan uyg'un */}
        <g fill="none" stroke="#22d3ee" strokeOpacity="0.1" strokeWidth="1.5">
          <path d="M-20 430 Q 205 360 410 430 T 840 430" />
          <path d="M-20 465 Q 205 395 410 465 T 840 465" />
          <path d="M-20 400 Q 205 330 410 400 T 840 400" />
        </g>

        {/* markaziy nishon: yo'l belgisi (uchburchak) */}
        <g transform="translate(410 215)">
          <circle r="96" fill="url(#ph-badge)" opacity="0.14" />
          <circle r="70" fill="url(#ph-badge)" opacity="0.22" />
          <path
            d="M0 -46 L44 32 Q49 42 38 42 L-38 42 Q-49 42 -44 32 Z"
            fill="none"
            stroke="url(#ph-badge)"
            strokeWidth="9"
            strokeLinejoin="round"
          />
          <rect x="-5" y="-22" width="10" height="34" rx="4" fill="#67e8f9" />
          <circle cx="0" cy="28" r="6" fill="#67e8f9" />
        </g>

        {/* brend nomi */}
        <text
          x="410"
          y="400"
          textAnchor="middle"
          fontFamily="Lato, Arial, sans-serif"
          fontWeight="900"
          fontSize="62"
          letterSpacing="1"
          fill="#e8eefc"
        >
          AvtoStart
        </text>
        <text
          x="410"
          y="446"
          textAnchor="middle"
          fontFamily="Lato, Arial, sans-serif"
          fontWeight="400"
          fontSize="24"
          letterSpacing="6"
          fill="#64748b"
        >
          RASM YO'Q
        </text>
      </svg>
    </div>
  );
}
