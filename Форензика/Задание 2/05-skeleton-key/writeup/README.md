# Разбор — 05 Скелетный ключ

## Где искать

```
live_response/process/proc/1/environ.txt
```

Дополнительно — исходный код приложения восстановим по контексту: `cmdline.txt` PID 1 показывает `python app.py`, а `environ.txt` раскрывает переменные окружения Flask-процесса, из которых видно, что `SECRET_KEY` там нет. Значит, ключ захардкожен в коде.

## Почему именно этот файл

UAC снимает `/proc/<pid>/environ` — переменные окружения процесса.  
Для PID 1 (Flask) там видны `HOSTNAME`, `FLAG`, `PYTHON_VERSION` — но никакого `SECRET_KEY`.

Это сигнал: секрет не передаётся через окружение. Он в исходном коде.  
Flask-разработчики часто пишут `app.secret_key = hashlib.sha256(b'some-string').hexdigest()` — детерминированный, но полностью предсказуемый ключ.

## Как получить ответ

Запусти в Python 3:

```python
import hashlib
print(hashlib.sha256(b'mindvault-rce-eval-search-filter').hexdigest())
```

Результат — 64-символьная hex-строка. Это флаг.

## Почему это критично

Зная `secret_key`, атакующий может создать подписанную Flask-сессию для любого пользователя, включая `admin@nexionlabs.com`, без знания пароля. Инструмент: `flask-unsign`.

## Ответ

```
RCPISS{f7b37c4090ada2194c2058c3bb589f8f1e11826bd8fc082af31c0b7c217a8232}
```
