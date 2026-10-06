// Rasm bo'lmaganda ko'rsatiladigan o'rindiq: pravaexpress.uz logotipi.
// Logoni almashtirish uchun faqat public/logo.svg faylini o'zgartiring.
const LOGO = `${import.meta.env.BASE_URL || "/"}logo.svg`;

export default function Placeholder({ className = "" }) {
  return (
    <div className={`placeholder ${className}`}>
      <img className="placeholder-logo" src={LOGO} alt="pravaexpress.uz" draggable={false} />
      <span className="placeholder-note">RASM YO'Q</span>
    </div>
  );
}
