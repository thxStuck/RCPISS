import os
import sqlite3
import uuid
from flask import Flask, request, render_template, redirect, url_for, session, flash, abort

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        # Таблица пользователей
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )''')
        
        # Таблица документов (защищены UUID)
        db.execute('''CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            owner_id INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY(owner_id) REFERENCES users(id)
        )''')
        
        # Таблица логов активности (уязвима к IDOR)
        db.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            metadata TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')
        
        # Создаем админа и его секретный документ
        try:
            db.execute("INSERT INTO users (username, password, role) VALUES ('admin', ?, 'admin')", (os.urandom(8).hex(),))
            admin_id = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()['id']
            
            secret_uuid = str(uuid.uuid4())
            db.execute("INSERT INTO documents (id, owner_id, title, content) VALUES (?, ?, 'Top Secret Flag', 'RCPISS{ID0R_v14_L0gs_L34k_2026}')", (secret_uuid, admin_id))
            
            # Лог админа, который содержит UUID документа
            db.execute("INSERT INTO activity_logs (user_id, action, metadata) VALUES (?, 'Created document', ?)", (admin_id, f"DocID: {secret_uuid}"))
            
            db.commit()
        except sqlite3.IntegrityError:
            pass

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    docs = db.execute('SELECT * FROM documents WHERE owner_id = ?', (session['user_id'],)).fetchall()
    
    # Показываем только свои логи (но эндпоинт логов уязвим!)
    logs = db.execute('SELECT * FROM activity_logs WHERE user_id = ?', (session['user_id'],)).fetchall()
    
    return render_template('index.html', user=user, docs=docs, logs=logs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            cursor = db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            user_id = cursor.lastrowid
            
            # Создаем приветственный документ
            doc_id = str(uuid.uuid4())
            db.execute("INSERT INTO documents (id, owner_id, title, content) VALUES (?, ?, 'Welcome Note', 'Hello! This is your private space.')", (doc_id, user_id))
            db.execute("INSERT INTO activity_logs (user_id, action, metadata) VALUES (?, 'System Registration', 'New account created')", (user_id,))
            db.execute("INSERT INTO activity_logs (user_id, action, metadata) VALUES (?, 'Document Created', ?)", (user_id, f"DocID: {doc_id}"))
            
            db.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
    return render_template('auth.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('auth.html', title='Login')

@app.route('/document/<doc_id>')
def view_document(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    # Проверка прав на документ (здесь IDOR нет, UUID защищает)
    doc = db.execute('SELECT * FROM documents WHERE id = ? AND owner_id = ?', (doc_id, session['user_id'])).fetchone()
    
    # НО! Мы сделаем "ошибку" — если пользователь админ, он может смотреть всё. 
    # Или просто уберем проверку owner_id, чтобы UUID был единственной защитой.
    doc = db.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    
    if not doc:
        abort(404)
        
    return render_template('document.html', doc=doc)

@app.route('/api/log/<int:log_id>')
def get_log(log_id):
    if 'user_id' not in session:
        return abort(401)
    
    db = get_db()
    # УЯЗВИМОСТЬ: Нет проверки, принадлежит ли лог текущему пользователю!
    log = db.execute('SELECT * FROM activity_logs WHERE id = ?', (log_id,)).fetchone()
    
    if not log:
        return {"error": "Log not found"}, 404
        
    return {
        "id": log['id'],
        "action": log['action'],
        "metadata": log['metadata']
    }

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
