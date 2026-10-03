import { useMemo } from "react";

// Skrinshotlardagi to'lqinli fon: ko'p ingichka sinus chiziqlar.
export default function Background() {
  const paths = useMemo(() => {
    const out = [];
    for (let i = 0; i < 46; i++) {
      const amp = 90 + i * 2.2;
      const phase = i * 0.045;
      let d = "";
      for (let x = 0; x <= 1600; x += 20) {
        const y = 430 + Math.sin(x / 260 + phase) * amp * Math.cos(x / 900 - phase);
        d += `${x === 0 ? "M" : "L"}${x},${y.toFixed(1)} `;
      }
      out.push(d);
    }
    return out;
  }, []);
  return (
    <svg className="bg-waves" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <linearGradient id="wave" x1="0" x2="1">
          <stop offset="0" stopColor="#1d4ed8" stopOpacity="0.05" />
          <stop offset="0.5" stopColor="#22d3ee" stopOpacity="0.25" />
          <stop offset="1" stopColor="#1d4ed8" stopOpacity="0.08" />
        </linearGradient>
      </defs>
      {paths.map((d, i) => (
        <path key={i} d={d} fill="none" stroke="url(#wave)" strokeWidth="0.6" />
      ))}
    </svg>
  );
}
