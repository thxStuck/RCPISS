import os
import time
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance INTEGER DEFAULT 10
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')
        db.commit()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    inventory = db.execute('SELECT item_name FROM inventory WHERE user_id = ?', (session['user_id'],)).fetchall()
    owned_items = [row['item_name'] for row in inventory]
    
    flag = None
    if all(item in owned_items for item in ['Key 1', 'Key 2', 'Key 3']):
        flag = "CTF{R4c3_C0nd1t10n_1s_Fun_2026}"
        
    return render_template('index.html', user=user, owned_items=owned_items, flag=flag)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
    return render_template('register.html')

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
    return render_template('login.html')

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    price = 10
    
    db = get_db()
    # Race condition vulnerability:
    # 1. Check balance
    user = db.execute('SELECT balance FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user['balance'] >= price:
        # Artificial delay to make race condition easier to exploit
        time.sleep(0.5)
        
        # 2. Update balance
        new_balance = user['balance'] - price
        db.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
        
        # 3. Add item to inventory
        db.execute('INSERT INTO inventory (user_id, item_name) VALUES (?, ?)', (user_id, item_name))
        db.commit()
        flash(f'Successfully bought {item_name}!')
    else:
        flash('Not enough coins!')
        
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
