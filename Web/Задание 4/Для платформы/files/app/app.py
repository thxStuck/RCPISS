import os
import requests
from flask import Flask, request, render_template, render_template_string, make_response
import threading

app = Flask(__name__)

# Секретный ключ не важен для SSTI, но нужен для сессий если бы они были
app.config['SECRET_KEY'] = os.urandom(24)

def send_webhook(url, data):
    try:
        # Имитируем отправку вебхука
        requests.post(url, json={"event": "webhook_created", "data": data}, timeout=5)
    except Exception:
        pass

@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    if not request.cookies.get('webhook_config'):
        # Дефолтное значение куки, которое выглядит как обычная настройка
        resp.set_cookie('webhook_config', '{"theme": "dark", "notify": "true"}')
    return resp

@app.route('/create', methods=['POST'])
def create_webhook():
    webhook_url = request.form.get('url')
    if not webhook_url:
        return "URL is required", 400

    # Получаем значение из куки
    config_raw = request.cookies.get('webhook_config', 'default')
    
    try:
        # УЯЗВИМОСТЬ: Рендеринг значения из куки через шаблонизатор
        # Мы "форматируем" данные перед отправкой в вебхук
        # Это выглядит как фича "динамической подстановки данных"
        rendered_data = render_template_string(config_raw)
    except Exception as e:
        rendered_data = f"Error processing config: {str(e)}"

    # Отправляем вебхук в фоновом режиме, чтобы не заставлять пользователя ждать
    thread = threading.Thread(target=send_webhook, args=(webhook_url, rendered_data))
    thread.start()

    return render_template('success.html', url=webhook_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
