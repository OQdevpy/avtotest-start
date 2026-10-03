// Demo kontent — backend/apps/content/management/commands/seed_demo.py bilan bir xil.

export const STAGES = [
  { number: 1, title: { uz: "1-bosqich", kr: "1-босқич", ru: "1-й этап" } },
  { number: 2, title: { uz: "2-bosqich", kr: "2-босқич", ru: "2-й этап" } },
  { number: 3, title: { uz: "3-bosqich", kr: "3-босқич", ru: "3-й этап" } },
  { number: 4, title: { uz: "4-bosqich", kr: "4-босқич", ru: "4-й этап" } },
];

const C = (uz, kr, ru, icon) => ({ title: { uz, kr, ru }, icon });
export const CATEGORIES = {
  1: [C("Ogohlantiruvchi belgilar", "Огоҳлантирувчи белгилар", "Предупреждающие знаки", "warning"),
      C("Imtiyoz belgilari", "Имтиёз белгилари", "Знаки приоритета", "priority"),
      C("Taqiqlovchi belgilar", "Тақиқловчи белгилар", "Запрещающие знаки", "noparking")],
  2: [C("Buyuruvchi belgilar", "Буюрувчи белгилар", "Предписывающие знаки", "ahead"),
      C("Axborot-ishora belgilari", "Ахборот-ишора белгилари", "Информационно-указательные знаки", "crossing"),
      C("Qo'shimcha axborot-ishora belgilari", "Қўшимча ахборот-ишора белгилари", "Знаки дополнительной информации", "plate")],
  3: [C("Yo'l chiziqlari", "Йўл чизиқлари", "Дорожная разметка", "lines"),
      C("Avtomagistral", "Автомагистрал", "Автомагистраль", "motorway")],
  4: [C("Taniqlilik belgilari", "Таниқлилик белгилари", "Опознавательные знаки", "hazmat"),
      C("Birinchi tibbiy yordam", "Биринчи тиббий ёрдам", "Первая медицинская помощь", "medical")],
};

export const SAMPLES = [
  {
    uz: "Qaysi belgi teng ahamiyatli yo'llar chorrahasiga yaqinlashib kelayotganlik haqida ogohlantiradi?",
    kr: "Қайси белги тенг аҳамиятли йўллар чорраҳасига яқинлашиб келаётганлик ҳақида огоҳлантиради?",
    ru: "Какой знак предупреждает о приближении к перекрёстку равнозначных дорог?",
    answers: ["3", "5", "2", "1", "4"], correct: 1, image: "signs5",
  },
  {
    uz: "Qatnov qismining chetiga chizilgan sariq sidirg'a chiziqni bosishga ruxsat beriladimi?",
    kr: "Қатнов қисмининг четига чизилган сариқ сидирға чизиқни босишга рухсат бериладими?",
    ru: "Разрешается ли наезжать на сплошную жёлтую линию у края проезжей части?",
    answers: ["Ruxsat berilmaydi", "Ruxsat beriladi"], correct: 0,
  },
  {
    uz: "Yo'l transport hodisasiga dahldor haydovchilar birinchi navbatda nima qilishlari kerak?",
    kr: "Йўл транспорт ҳодисасига дахлдор ҳайдовчилар биринчи навбатда нима қилишлари керак?",
    ru: "Что в первую очередь должны сделать водители, причастные к ДТП?",
    answers: [
      "Transport vositasini darhol to'xtatishi, avariya ishoralarini yoqishi va avariya sababli to'xtash belgisini o'rnatishi",
      "Yo'lning harakat qismini bo'shatishlari kerak",
      "Sodir etilgan hodisa xaqida YHXXga xabar berishi kerak",
    ],
    correct: 0,
  },
  {
    uz: "Chorrahada aylanma harakatlanish tashkil qilingan. Chorrahaga kirishda burilish uchun qaysi tasmani egallashingiz lozim?",
    kr: "Чорраҳада айланма ҳаракатланиш ташкил қилинган. Чорраҳага киришда бурилиш учун қайси тасмани эгаллашингиз лозим?",
    ru: "На перекрёстке организовано круговое движение. Какую полосу нужно занять для поворота?",
    answers: ["O'ng yoki chap tasmani", "O'ng tasmani", "Chap tasmani"], correct: 1,
  },
  {
    uz: "Qatnov qismi tomonidan yo'lovchilarning tushishi va chiqishiga qaysi hollarda ruxsat etiladi?",
    kr: "Қатнов қисми томонидан йўловчиларнинг тушиши ва чиқишига қайси ҳолларда рухсат этилади?",
    ru: "В каких случаях разрешается посадка и высадка пассажиров со стороны проезжей части?",
    answers: [
      "Haydovchining xohishiga ko'ra",
      "Transport vositasi majburiy to'xtaganda",
      "Trotuar tomondan iloji bo'lmasa, xavfsiz bo'lsa va boshqalarga halaqit bermasa",
    ],
    correct: 2,
  },
  {
    uz: "Qaysi belgi piyodalar o'tish joyini bildiradi?",
    kr: "Қайси белги пиёдалар ўтиш жойини билдиради?",
    ru: "Какой знак обозначает пешеходный переход?",
    answers: ["А", "В", "Б"], correct: 2, image: "signs3",
  },
];

// Demo foydalanuvchilar. Haqiqiy tizimda kodlar faqat HMAC ko'rinishida saqlanadi.
export const STUDENTS = [
  { id: 1, full_name: "Ali Valiyev", code: "AVTO2026DEMO", max_devices: 1, active: true },
  { id: 2, full_name: "Malika Karimova", code: "MALIKA7K3Q9P", max_devices: 2, active: true },
  { id: 3, full_name: "Sardor Toshmatov", code: "SARDOR4X8N2M", max_devices: 1, active: true },
  { id: 4, full_name: "Muddati tugagan", code: "EXPIRED9ZZZZ", max_devices: 1, active: false },
];

// --- SVG belgilar (bo'lim ikonkalari va savol rasmlari) ---

const tri = (inner, x = 0, y = 0, s = 1) =>
  `<g transform="translate(${x} ${y}) scale(${s})"><path d="M100 12 L190 172 Q194 182 182 182 L18 182 Q6 182 10 172 Z" fill="#fff" stroke="#e11d1d" stroke-width="16" stroke-linejoin="round"/>${inner}</g>`;

const ICONS = {
  warning: tri(`<circle cx="112" cy="70" r="11" fill="#111"/><path d="M106 84 L92 120 L76 150 M100 104 L124 120 L132 150 M104 92 L128 100" stroke="#111" stroke-width="10" stroke-linecap="round" fill="none"/><path d="M40 160h20M70 160h20M100 160h20M130 160h20" stroke="#111" stroke-width="10"/>`),
  priority: `<rect x="40" y="40" width="120" height="120" transform="rotate(45 100 100)" fill="#fff" stroke="#ddd" stroke-width="4"/><rect x="62" y="62" width="76" height="76" transform="rotate(45 100 100)" fill="#facc15" stroke="#111" stroke-width="3"/>`,
  noparking: `<circle cx="100" cy="100" r="84" fill="#1d4ed8" stroke="#e11d1d" stroke-width="18"/><path d="M42 42 L158 158 M158 42 L42 158" stroke="#e11d1d" stroke-width="16"/>`,
  ahead: `<circle cx="100" cy="100" r="88" fill="#1d4ed8" stroke="#fff" stroke-width="6"/><path d="M100 30 L140 80 H114 V170 H86 V80 H60 Z" fill="#fff"/>`,
  crossing: `<rect x="14" y="14" width="172" height="172" rx="10" fill="#1d4ed8" stroke="#fff" stroke-width="6"/><path d="M100 36 L172 170 H28 Z" fill="#fff"/><circle cx="104" cy="76" r="9" fill="#111"/><path d="M100 88 L88 120 L76 146 M96 108 L118 120 L124 146" stroke="#111" stroke-width="8" stroke-linecap="round" fill="none"/><path d="M50 160h16M76 160h16M102 160h16M128 160h16" stroke="#111" stroke-width="8"/>`,
  plate: `<rect x="10" y="50" width="180" height="100" rx="8" fill="#fff" stroke="#111" stroke-width="5"/><path d="M40 118 L50 92 Q54 84 64 84 H112 Q122 84 130 92 L150 108 H160 V122 H40 Z" fill="#111"/><circle cx="68" cy="124" r="12" fill="#fff" stroke="#111" stroke-width="6"/><circle cx="134" cy="124" r="12" fill="#fff" stroke="#111" stroke-width="6"/>`,
  lines: `<rect x="6" y="56" width="188" height="88" fill="#6b7280"/>${[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => `<rect x="${14 + i * 20}" y="64" width="12" height="72" fill="${i % 2 ? "#facc15" : "#fff"}"/>`).join("")}`,
  motorway: `<rect x="30" y="8" width="140" height="184" rx="8" fill="#15803d" stroke="#fff" stroke-width="6"/><path d="M92 24 L60 176 H84 L98 24 Z M108 24 L116 176 H140 L102 24 Z" fill="#fff"/><path d="M98 120 v20 M98 150 v20" stroke="#15803d" stroke-width="6"/>`,
  hazmat: `<rect x="40" y="40" width="120" height="120" transform="rotate(45 100 100)" fill="#facc15"/><path d="M15 100 L100 15 L185 100 Z" fill="#dc2626"/><path d="M100 40 C120 60 112 74 104 80 C110 66 98 58 96 52 C90 66 78 70 84 84 C70 76 78 54 100 40 Z" fill="#111"/><text x="100" y="168" font-family="Arial" font-weight="700" font-size="22" text-anchor="middle">5.2</text>`,
  medical: `<rect x="14" y="14" width="172" height="172" rx="10" fill="#1d4ed8" stroke="#fff" stroke-width="6"/><rect x="44" y="44" width="112" height="112" fill="#fff"/><path d="M88 60 H112 V88 H140 V112 H112 V140 H88 V112 H60 V88 H88 Z" fill="#dc2626"/>`,
};

export function iconSvg(name) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">${ICONS[name] || ""}</svg>`;
}

const num = (n, x, y) => `<text x="${x}" y="${y}" font-family="Arial" font-size="56" text-anchor="middle" fill="#111">${n}</text>`;
const crossT = `<path d="M100 60 V160 M70 120 H130" stroke="#111" stroke-width="16"/>`;
const sideT = `<path d="M100 60 V160 M70 110 H100" stroke="#111" stroke-width="16"/>`;
const yieldSign = `<path d="M10 20 H190 L100 180 Z" fill="#fff" stroke="#e11d1d" stroke-width="16" stroke-linejoin="round"/>`;
const twoWay = `<path d="M80 70 V160 M80 160 l-16-22 M80 160 l16-22 M120 160 V70 M120 70 l-16 22 M120 70 l16 22" stroke="#111" stroke-width="12" fill="none"/>`;
const xCross = `<path d="M70 85 L130 155 M130 85 L70 155" stroke="#111" stroke-width="16"/>`;

const IMAGES = {
  signs5: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 540"><rect width="820" height="540" fill="#fff"/>
    ${tri(crossT, 40, 10, 1)}${num(1, 140, 260)}${tri(sideT, 310, 10, 1)}${num(2, 410, 260)}
    <g transform="translate(580 10)">${yieldSign}</g>${num(3, 680, 260)}
    ${tri(twoWay, 170, 280, 1)}${num(4, 270, 530)}${tri(xCross, 470, 280, 1)}${num(5, 570, 530)}</svg>`,
  signs3: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 540"><rect width="820" height="540" fill="#555"/>
    <g transform="translate(20 20) scale(1.1)">${ICONS.warning}</g>
    <g transform="translate(300 20) scale(1.1)">${ICONS.crossing}</g>
    <g transform="translate(590 20)"><rect width="200" height="320" rx="10" fill="#1d4ed8" stroke="#fff" stroke-width="6"/>
      <circle cx="70" cy="180" r="14" fill="#fff"/><path d="M70 196 L60 240 L48 290 M66 220 L86 250 L92 290" stroke="#fff" stroke-width="10" fill="none"/>
      <rect x="40" y="40" width="70" height="44" rx="10" fill="#fff"/><circle cx="140" cy="270" r="14" fill="#fff"/></g>
    <text x="130" y="500" font-family="Arial" font-weight="700" font-size="90" fill="#fff" text-anchor="middle">А</text>
    <text x="410" y="500" font-family="Arial" font-weight="700" font-size="90" fill="#fff" text-anchor="middle">Б</text>
    <text x="690" y="500" font-family="Arial" font-weight="700" font-size="90" fill="#fff" text-anchor="middle">В</text></svg>`,
};

export function imageSvg(name) {
  return IMAGES[name];
}

/** Bo'lim «Malumot» rasmi: shu bo'lim belgisining bir nechta nusxasi. */
export function infoSvg(icon) {
  const cells = [0, 1, 2, 3, 4, 5].map(
    (i) => `<g transform="translate(${30 + (i % 3) * 260} ${30 + Math.floor(i / 3) * 250}) scale(1.05)">${ICONS[icon]}</g>`,
  );
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 540"><rect width="820" height="540" fill="#fff"/>${cells.join("")}</svg>`;
}
