Я шёл домой после пар и сделал это фото. Найди место съёмки

![[dome.jpg]]

Флаг - `RCPISS{xx.xxx_yy.yyy}`

---
## Шаг 1 - ищем храм / собор / церковь

Начнём с простейшего - закинем фотографию в поиск по фото.

![[rawsearch_yandex.png]]

![[rawsearch_google.png]]

Если просто искать по фото, без уточняющих запросов, то выбор слишком велик, ибо религиозные постройки выглядят +- похоже. Попробуем найти уточнения.

---

## Шаг 2 - смотрим метаданные

Метаданные тоже считаются открытым источником, поэтому смотрим
```exiftool
exiftool dome.jpg
File Name                       : dome.jpg
Directory                       : .
File Size                       : 3.1 MB
File Modification Date/Time     : 2026:06:14 10:42:18+03:00
File Access Date/Time           : 2026:06:14 10:44:32+03:00
File Creation Date/Time         : 2026:06:14 10:42:18+03:00
File Permissions                : -rw-rw-rw-
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : None
X Resolution                    : 1
Y Resolution                    : 1
Exif Byte Order                 : Big-endian (Motorola, MM)
Image Description               : Krasnodar
Software                        : Shot in Krasnodar, Russia
Artist                          : Krasnodar, Russia
Copyright                       : Krasnodar, Russia
XP Keywords                     : Krasnodar;Russia;╨Ъ╤А╨░╤Б╨╜╨╛╨┤╨░╤А
XP Subject                      : Krasnodar
User Comment                    : Shot in Krasnodar, Russia
GPS Latitude Ref                : North
GPS Longitude Ref               : East
Image Width                     : 6000
Image Height                    : 8000
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 6000x8000
Megapixels                      : 48.0
GPS Latitude                    : 45 deg 2' 7.80" N
GPS Longitude                   : 38 deg 58' 31.08" E
GPS Position                    : 45 deg 2' 7.80" N, 38 deg 58' 31.08" E
```

Ага, написано, что это Краснодар. Проверяем в том же поиске по фото.

![[exactsearch_google.png]]

![[exactsearch_yandex.png]]

---

## Шаг 3 - панорамы

Отлично, нам даже указали точный адрес. Идём проверять

![[church_strview.png]]

А вот и искомый храм.
Теперь ищем точку, откуда было сделано фото. Данная позиция на панораме является искомой для установления точки съёмки. Сначала мы учитываем сдвиг, потому что точка с панорамой не совсем точная. После мы проводим прямую линию и получаем точку съёмки фото.

![[measurments.png]]

---
Флаг - `RCPISS{45.051_38.985}`
