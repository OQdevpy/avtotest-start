export const LANGS = [
  { code: "uz", label: "O'zbek tili" },
  { code: "kr", label: "Ўзбек тили" },
  { code: "ru", label: "Русский язык" },
];

const T = {
  talim: ["Ta'lim", "Таълим", "Обучение"],
  stageTest: ["Bosqichli Test", "Босқичли Тест", "Поэтапный тест"],
  finalTest: ["Yakuniy Test", "Якуний Тест", "Итоговый тест"],
  variants: ["Test Variantlari", "Тест Вариантлари", "Варианты тестов"],
  stageVariants: ["Bo'lim bo'yicha Test Variantlari", "Бўлим бўйича Тест Вариантлари", "Варианты тестов по разделам"],
  logout: ["Chiqish", "Чиқиш", "Выход"],
  logoutConfirm: ["Rostdan ham chiqmoqchimisiz?", "Ростдан ҳам чиқмоқчимисиз?", "Вы действительно хотите выйти?"],
  cancel: ["Bekor qilish", "Бекор қилиш", "Отмена"],
  yes: ["Ha", "Ҳа", "Да"],
  no: ["Yo'q", "Йўқ", "Нет"],
  back: ["Ortga", "Ортга", "Назад"],
  stage: ["bosqich", "босқич", "этап"],
  variant: ["variant", "вариант", "вариант"],
  info: ["Malumot", "Маълумот", "Информация"],
  partTest: ["Qisim bo'yicha test", "Қисм бўйича тест", "Тест по разделу"],
  questionsCount: ["Savollar soni", "Саволлар сони", "Количество вопросов"],
  audioHint: ["Audio izoh", "Аудио изоҳ", "Аудио пояснение"],
  photoHint: ["Photo izoh", "Фото изоҳ", "Фото пояснение"],
  do20: ["20 ta test ishlash", "20 та тест ишлаш", "Решить 20 вопросов"],
  do50: ["50 ta test ishlash", "50 та тест ишлаш", "Решить 50 вопросов"],
  start: ["Boshlash", "Бошлаш", "Начать"],
  leaveTest: [
    "Haqiqatdan ham testni yakunlab ortga qaytmoqchimisiz?",
    "Ҳақиқатдан ҳам тестни якунлаб ортга қайтмоқчимисиз?",
    "Вы действительно хотите завершить тест и вернуться?",
  ],
  result: ["Natija", "Натижа", "Результат"],
  correct: ["To'g'ri", "Тўғри", "Правильно"],
  mistakes: ["Xato", "Хато", "Ошибки"],
  passed: ["Imtihondan o'tdingiz!", "Имтиҳондан ўтдингиз!", "Экзамен сдан!"],
  failed: ["Imtihondan o'ta olmadingiz", "Имтиҳондан ўта олмадингиз", "Экзамен не сдан"],
  timeUp: ["Vaqt tugadi", "Вақт тугади", "Время вышло"],
  loginTitle: ["Tizimga kirish", "Тизимга кириш", "Вход в систему"],
  code: ["Kirish kodi", "Кириш коди", "Код доступа"],
  enter: ["Kirish", "Кириш", "Войти"],
  loading: ["Yuklanmoqda…", "Юкланмоқда…", "Загрузка…"],
  empty: ["Savollar topilmadi", "Саволлар топилмади", "Вопросы не найдены"],
  err_invalid_code: ["Kod noto'g'ri yoki muddati tugagan", "Код нотўғри ёки муддати тугаган", "Неверный или просроченный код"],
  err_device_limit: [
    "Bu kod boshqa qurilmada ishlatilmoqda. Administratorga murojaat qiling.",
    "Бу код бошқа қурилмада ишлатилмоқда. Администраторга мурожаат қилинг.",
    "Код уже используется на другом устройстве. Обратитесь к администратору.",
  ],
  err_too_many_attempts: ["Juda ko'p urinish. 15 daqiqadan so'ng qayta urining.", "Жуда кўп уриниш. 15 дақиқадан сўнг қайта уриниш.", "Слишком много попыток. Повторите через 15 минут."],
  err_throttled: ["Juda ko'p urinish. Birozdan so'ng qayta urining.", "Жуда кўп уриниш. Бироздан сўнг қайта уриниш.", "Слишком много попыток. Повторите позже."],
  err_generic: ["Xatolik yuz berdi", "Хатолик юз берди", "Произошла ошибка"],
  err_crypto: [
    "Brauzeringiz xavfsiz ulanishni qo'llamaydi (HTTPS kerak).",
    "Браузерингиз хавфсиз уланишни қўлламайди (HTTPS керак).",
    "Браузер не поддерживает защищённое соединение (нужен HTTPS).",
  ],
};

const IDX = { uz: 0, kr: 1, ru: 2 };

export function t(key, lang) {
  const row = T[key];
  return row ? row[IDX[lang] ?? 0] : key;
}

/** Serverdan kelgan {uz, kr, ru} matn. */
export function tr(obj, lang) {
  if (!obj) return "";
  return obj[lang] || obj.uz || obj.ru || obj.kr || "";
}
