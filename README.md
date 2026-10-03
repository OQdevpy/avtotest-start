# AvtoStart

Haydovchilik imtihoniga tayyorlov platformasi: **React (Vite)** frontend va **Django + DRF** backend.
Mijoz bilan server o'rtasidagi barcha ma'lumot (savollar, javoblar, rasmlar, audio) **shifrlangan `.bin`
fayllar** ko'rinishida almashadi.

## Imkoniyatlar (skrinshotlar asosida)

| Bo'lim | Tavsif |
|---|---|
| **Ta'lim** | Bosqich → bo'limlar (belgi rasmi, savollar soni) → «i» ma'lumot sahifasi + savollar. To'g'ri javob ko'rinadi, audio/foto izoh bor. «Qisim bo'yicha test» tugmasi |
| **Bosqichli test** | 1–4 bosqich, 20 yoki 50 ta savol tanlanadi |
| **Yakuniy test** | Barcha bo'limlardan tasodifiy 20 yoki 50 savol |
| **Test variantlari** | 1–60 variant |
| **Bo'lim bo'yicha test variantlari** | Har bir bosqich uchun 1–18 variant |

Test oynasi: savol banneri, `F1…F5` javob tugmalari (klaviaturadan ham ishlaydi), o'ngda rasm va
`0 : 25 : 00` taymer, pastda raqamli navigatsiya (yashil — to'g'ri, qizil — xato). «Ortga» bosilganda
tasdiqlash oynasi chiqadi. Uch til: O'zbek (lotin), Ўзбек (кирилл), Русский. Til almashtirilganda serverga
qayta murojaat qilinmaydi, chunki har bir matn uchala tilda keladi.

## Arxitektura

```
backend/
  binproto/         .bin protokoli: shifrlash, DRF parser/renderer, autentifikatsiya, xavfsizlik middleware
  apps/accounts/    O'quvchi (kirish kodi), DeviceSession, login (ECDH handshake)
  apps/content/     Bosqich, Bo'lim, Savol, Javob, Variant; katalog va shifrlangan media
  apps/exams/       Urinish (Attempt): boshlash, javob berish, yakunlash — baholash faqat serverda
  tests/            pytest (22 ta test)
frontend/
  src/lib/envelope.js   .bin formati + WebCrypto (ECDH/HKDF/AES-GCM)
  src/lib/api.js        shifrlangan so'rov/javob, media → Blob URL
  src/pages/            sahifalar
  nginx.conf            SPA + /api proksi, CSP, rate-limit
```

## `.bin` protokoli

```
+-------+-------+----------+------------------------------+
| AVS1  | flags | nonce    | AES-256-GCM(shifrmatn + tag) |
| 4 B   | 1 B   | 12 B     | N + 16 B                     |
+-------+-------+----------+------------------------------+
flags = 1 → ichida zlib bilan siqilgan JSON;  flags = 2 → xom bayt (rasm/audio + MIME)
AAD   = magic + flags + yo'nalish(req|res) + so'rov yo'li
```

1. **Login**: brauzer eksport qilinmaydigan ECDH P-256 kalit juftini yaratadi va kirish kodi bilan birga
   faqat **ochiq kalitini** yuboradi. Server o'zining bir martalik juftini yaratadi va HKDF-SHA256 orqali
   AES-256 kalitini chiqaradi. Javobda serverning ochiq kaliti, salt va token bor. **AES kalitining o'zi
   tarmoqdan hech qachon o'tmaydi.**
2. Brauzer xuddi shu kalitni hisoblaydi (`extractable: false`, ya'ni JS ham uni o'qiy olmaydi) va uni
   `CryptoKey` obyekti holida IndexedDB'da saqlaydi.
3. Login'dan keyingi har bir so'rov va javob `.bin` konvertda keladi. Media fayllar ham `.bin` bo'lib keladi,
   brauzerda ochiladi va faqat `blob:` URL sifatida ko'rsatiladi.

## Xavfsizlik

**Kalit va shifrlash**
- **Kalit tarmoqdan o'tmaydi**: kalit ECDH bilan kelishiladi. Bazada u `BIN_STORAGE_KEY` bilan AES-GCM'da
  o'ralgan holda saqlanadi.
- **AAD so'rov yo'liga bog'langan**: bir endpointning `.bin` javobini boshqa endpointga yoki so'rov
  sifatida qayta yuborib bo'lmaydi. Konvertdagi 1 bit o'zgarsa ham rad etiladi.
- **Replay himoyasi**: har bir POST ichida `_ts` va `_n` (nonce) bor. ±120 soniyadan eski yoki takroriy
  so'rov rad etiladi (Redis kesh).

**Kirish va sessiya**
- **Token + qurilma bog'lanishi**: `Authorization: Bin <token>` va `X-Device-Id` mos kelishi shart. Token
  o'g'irlansa ham, sessiya kalitisiz uning so'rov tanasini shifrlab bo'lmaydi.
- **Qurilma limiti**: standart bo'yicha har bir kodga 1 ta qurilma. Shu qurilmadan qayta kirilsa, eski
  sessiya bekor bo'ladi. Sessiya muddati 12 soat.
- **Kodlar va tokenlar** bazada faqat HMAC-SHA256 ko'rinishida saqlanadi. Kod 12 belgidan iborat
  (≈60 bit) va admin panelda faqat bir marta ko'rsatiladi.
- **Brute-force himoyasi**: nginx `limit_req`, DRF throttle (`5/min`) va IP bo'yicha bloklash
  (15 daqiqada 10 ta xato). Xato xabari bitta: kod mavjudmi yoki yo'qligi oshkor qilinmaydi.

**Imtihon qoidalari (serverda)**
- To'g'ri javob test rejimida **yuborilmaydi**. U faqat savolga javob berilgandan keyin keladi, javob esa
  qulflanadi va uni o'zgartirib bo'lmaydi. Ta'lim rejimi bundan mustasno.
- Ball va vaqt faqat serverda hisoblanadi. 25 daqiqa tugagach, `answer` so'rovi `409` qaytaradi.
- O'quvchi boshqa o'quvchining urinishini ko'ra olmaydi (`404`). Nashr etilmagan savol hech qaysi yo'l
  orqali berilmaydi.

**Media**
- Ommaviy `/media/` URL yo'q. Faqat ruxsat etilgan model va maydonlar beriladi, fayl nomlari tasodifiy UUID.

**Server sozlamalari va brauzer**
- **Sarlavhalar**: API uchun CSP `default-src 'none'`. SPA uchun qat'iy CSP (tashqi skript yo'q,
  `img-src blob:`), shuningdek HSTS, `nosniff`, `X-Frame-Options: DENY` va `Cache-Control: no-store`.
- **Sozlamalar xavfsiz holatda yopiladi**: `DEBUG=False` bo'lsa, `SECRET_KEY`, `BIN_STORAGE_KEY` va
  `ALLOWED_HOSTS` majburiy, aks holda ilova ishga tushmaydi. Admin manzili `ADMIN_URL` orqali
  yashiriladi. Backend porti tashqariga ochilmaydi.
- **Nusxa olishni qiyinlashtirish**: test sahifasida matnni belgilash va kontekst menyusi o'chirilgan.

> Eslatma: brauzer kontentni ko'rsatishi uchun uni baribir ochishi kerak. Shuning uchun shifrlash
> ommaviy yig'ib olishni (scraping), tarmoqda kuzatishni va API'ni to'g'ridan-to'g'ri o'qishni
> to'xtatadi. Ammo ekranga chiqqan narsani 100% himoya qilib bo'lmaydi.

## Ishga tushirish (lokal)

```bash
# Backend
cd backend
pip install -r requirements.txt
export DEBUG=1
python manage.py migrate
python manage.py seed_demo                    # demo kontent: 4 bosqich, 120 savol, 132 variant
python manage.py create_student "Ali Valiyev" # → kirish kodi chiqadi
python manage.py createsuperuser              # admin panel uchun
python manage.py runserver                    # http://127.0.0.1:8000

# Frontend (boshqa terminalda)
cd frontend
npm install
npm run dev                                   # http://localhost:5173 (/api → :8000 proksi)
```

Admin panel: `http://127.0.0.1:8000/boshqaruv-7f3a/`. Bu yerda o'quvchilar (kod yaratish, qurilmalardan
chiqarish), bo'limlar, savollar (rasm/audio yuklash), javoblar va variantlar boshqariladi.

> WebCrypto faqat xavfsiz kontekstda ishlaydi: `https://` yoki `localhost`.

## Produksiya (Docker)

```bash
cp .env.example .env     # SECRET_KEY, BIN_STORAGE_KEY, DB_PASSWORD, ALLOWED_HOSTS ni to'ldiring
docker compose up -d --build
docker compose exec backend python manage.py createsuperuser
```

`web` konteyneri 8080-portda ishlaydi. TLS'ni tashqi nginx yoki Caddy'da tugating va
`X-Forwarded-Proto` sarlavhasini uzating.

## Testlar

```bash
cd backend && python -m pytest     # 22 ta test
```

Testlar quyidagilarni tekshiradi:
- konvertni o'zgartirish yoki boshqa yo'lga ko'chirish rad etilishi;
- replay va eskirgan so'rovlar;
- login javobida kalit yo'qligi;
- qurilma limiti va `device_id` mos kelmasligi;
- noto'g'ri kalit bilan yuborilgan so'rov rad etilishi;
- test rejimida javoblar yashirilishi va javobni o'zgartirib bo'lmasligi;
- muddat (deadline);
- begona urinishga kirish;
- media faqat shifrlangan holda berilishi;
- nashr etilmagan savollar ko'rinmasligi;
- xavfsizlik sarlavhalari.

## API

| Metod | Yo'l | Tana |
|---|---|---|
| POST | `/api/auth/login/` | JSON `{code, device_id, client_pub}` |
| POST | `/api/auth/logout/` | .bin |
| GET | `/api/auth/me.bin` | |
| GET | `/api/catalog.bin` | bosqichlar, bo'limlar, variantlar |
| GET | `/api/categories/{id}/info.bin` | |
| GET | `/api/media/{category\|question}/{id}/{field}.bin` | rasm/audio |
| POST | `/api/attempts/start.bin` | `{kind: study\|category\|stage\|final\|variant, ref?, count?: 20\|50}` |
| GET | `/api/attempts/{id}.bin` | holatni tiklash |
| POST | `/api/attempts/{id}/answer.bin` | `{question, answer}` |
| POST | `/api/attempts/{id}/finish.bin` | |
| GET | `/api/attempts/history.bin` | |

## Demo (backendsiz)

```bash
cd frontend && npm run build:demo   # → dist-demo/
```

Demo yig'ilishda `src/lib/transport.js` o'rniga `transport.demo.js` ulanadi. Bu holda so'rovlar Django'ga
emas, brauzer ichidagi serverga (`src/lib/demoServer.js`) boradi. Protokol o'zgarmaydi: ECDH, AES-GCM `.bin`,
replay himoyasi, qurilmaga bog'langan token va baholash "server"da. Demo login sahifasida tayyor
foydalanuvchilar ro'yxati chiqadi. Oddiy `npm run build` natijasiga demo kodi va demo kodlar umuman tushmaydi.
