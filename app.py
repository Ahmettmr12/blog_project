# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
from utils.email_helper import generate_code, send_email_code


app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

@app.route('/blog')
def blog():
    if 'user_id' not in session:
        return redirect(url_for('login'))  

    with sqlite3.connect("users.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
        posts = cursor.fetchall()
    return render_template("blog.html", posts=posts)




@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('blog'))
    else:
        return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Bu e-posta zaten kayıtlı."
    return render_template('register.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    with sqlite3.connect("users.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()

    if post:
        return render_template("post_detail.html", post=post)
    else:
        return "Yazı bulunamadı", 404

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'pending_user' not in session:
        return redirect(url_for('login'))  # yetkisiz erişim varsa login'e yönlendir

    if request.method == 'POST':
        code_input = request.form['code']
        if code_input == session.get('code'):
            session['user_id'] = session.pop('pending_user')
            session.pop('code', None)
            return redirect(url_for('dashboard'))
        else:
            return "Kod hatalı. Lütfen tekrar deneyin."
    return render_template('verify.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = cursor.fetchone()
            if user:
                session['pending_user'] = user[0]  # kullanıcı ID
                session['email'] = email
                code = generate_code()
                session['code'] = code
                send_email_code(email, code)
                return redirect(url_for('verify'))  # Yönlendirme burada olmalı
            else:
                return "Giriş başarısız."
    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

def create_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        # Kullanıcı tablosu
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")

        # Blog yazıları tablosu
        cursor.execute("""CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def add_sample_posts():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
                       ("İlk Yazı", "Bu benim ilk blog yazım!", "admin"))
        cursor.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
                       ("Python ile Web", "Flask kullanarak web uygulaması yapmak çok kolay!", "ahmet"))
        cursor.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
                       ("Güvenli Giriş", "2 Aşamalı doğrulama ile kullanıcı güvenliği artırılır.", "admin"))
        conn.commit()

if __name__ == '__main__':
    create_db()

    
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posts")
        count = cursor.fetchone()[0]
        if count == 0:
            add_sample_posts()

    app.run(debug=True)
