// Rasm bo'lmaganda ko'rsatiladigan o'rindiq: oq fon + pravaexpress.uz logotipi.
// Logoni almashtirish uchun faqat public/logo.webp faylini o'zgartiring.
const LOGO = `${import.meta.env.BASE_URL || "/"}logo.webp`;

export default function Placeholder({ className = "" }) {
  return (
    <div className={`placeholder ${className}`}>
      <img className="placeholder-logo" src={LOGO} alt="pravaexpress.uz" draggable={false} />
    </div>
  );
}
