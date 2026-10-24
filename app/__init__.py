import csv
import io
import os
import re
import secrets
import sqlite3
from functools import wraps
from pathlib import Path
from flask import Flask, jsonify, request, session, render_template, g, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from .db import get_db, close_db, init_db
from .services import DomainError, EventService, RegistrationService, now_local


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    secret_file = Path(app.instance_path) / 'session.key'
    if not secret_file.exists():
        secret_file.write_text(secrets.token_hex(32))
        secret_file.chmod(0o600)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secret_file.read_text(),
                      DATABASE=str(Path(app.instance_path) / 'events.sqlite3'),
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                      SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1',
                      MAX_CONTENT_LENGTH=32768)
    if test_config:
        app.config.update(test_config)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    def require_login(admin=False):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                if g.user is None:
                    raise DomainError('Əvvəlcə sistemə daxil olun.', 401)
                if admin and g.user['role'] != 'admin':
                    raise DomainError('Bu əməliyyat yalnız administrator üçündür.', 403)
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    @app.before_request
    def security():
        g.user = get_db().execute('SELECT id,name,email,role FROM users WHERE id=?', (session.get('user_id'),)).fetchone()
        if request.path.startswith('/api/') and request.method in ('POST', 'PUT', 'DELETE'):
            token = session.get('csrf')
            if not token or not secrets.compare_digest(token, request.headers.get('X-CSRF-Token', '')):
                raise DomainError('Sorğunun təhlükəsizlik açarı etibarsızdır. Səhifəni yeniləyin.', 403)

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(DomainError)
    def domain_error(error):
        return jsonify(error=str(error)), error.status

    @app.errorhandler(Exception)
    def unexpected_error(error):
        if isinstance(error, HTTPException):
            return jsonify(error='Sorğu qəbul edilmədi.'), error.code
        app.logger.exception('Unexpected request error')
        return jsonify(error='Gözlənilməyən xəta baş verdi. Yenidən cəhd edin.'), 500

    def body():
        value = request.get_json(silent=True)
        if not isinstance(value, dict):
            raise DomainError('Düzgün JSON məlumatı göndərin.')
        return value

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/session')
    def current_session():
        session.setdefault('csrf', secrets.token_hex(32))
        return jsonify(user=dict(g.user) if g.user else None, csrf=session['csrf'])

    @app.post('/api/signup')
    def signup():
        data = body()
        name, email, password = data.get('name', ''), data.get('email', ''), data.get('password', '')
        if not all(isinstance(v, str) for v in [name, email, password]):
            raise DomainError('Ad, e-poçt və şifrə mətn olmalıdır.')
        email = email.strip().lower()
        if not 2 <= len(name.strip()) <= 100 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(email) > 254 or not 8 <= len(password) <= 128:
            raise DomainError('Ad ən azı 2, şifrə 8–128 simvol olmalı, e-poçt düzgün yazılmalıdır.')
        db = get_db()
        try:
            with db:
                db.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)', (name.strip(), email, generate_password_hash(password)))
        except sqlite3.IntegrityError:
            raise DomainError('Bu e-poçt artıq istifadə olunur.', 409)
        return jsonify(message='Hesab yaradıldı. Daxil ola bilərsiniz.'), 201

    @app.post('/api/login')
    def login():
        data = body()
        email, password = data.get('email', ''), data.get('password', '')
        if not isinstance(email, str) or not isinstance(password, str) or len(password) > 128:
            raise DomainError('Giriş məlumatları düzgün deyil.')
        user = get_db().execute('SELECT * FROM users WHERE email=?', (email.strip(),)).fetchone()
        if not user or not check_password_hash(user['password_hash'], password):
            raise DomainError('E-poçt və ya şifrə yanlışdır.', 401)
        session.clear()
        session.update(user_id=user['id'], csrf=secrets.token_hex(32))
        return jsonify(message='Sistemə daxil oldunuz.')

    @app.post('/api/logout')
    def logout():
        session.clear()
        return jsonify(message='Hesabdan çıxıldı.')

    @app.get('/api/categories')
    def categories():
        return jsonify([dict(x) for x in get_db().execute('SELECT * FROM categories')])

    @app.get('/api/events')
    def events():
        query = '''SELECT e.*,c.name category,(SELECT COUNT(*) FROM registrations r WHERE r.event_id=e.id) registered,
        EXISTS(SELECT 1 FROM registrations r WHERE r.event_id=e.id AND r.user_id=?) is_registered
        FROM events e JOIN categories c ON c.id=e.category_id WHERE 1=1'''
        params = [session.get('user_id', -1)]
        for arg, column in [('q', 'e.title'), ('location', 'e.location')]:
            if request.args.get(arg):
                query += f' AND {column} LIKE ?'
                params.append('%' + request.args[arg] + '%')
        if request.args.get('category'):
            query += ' AND e.category_id=?'
            params.append(request.args['category'])
        for arg, operation in [('from', '>='), ('to', '<=')]:
            if request.args.get(arg):
                query += f' AND substr(e.starts_at,1,10) {operation} ?'
                params.append(request.args[arg])
        if request.args.get('mine') == '1':
            query += ' AND EXISTS(SELECT 1 FROM registrations r WHERE r.event_id=e.id AND r.user_id=?)'
            params.append(session.get('user_id', -1))
        results = []
        for row in get_db().execute(query + ' ORDER BY e.starts_at', params):
            item = dict(row)
            item['past'] = item['starts_at'] <= now_local().isoformat(timespec='minutes')
            results.append(item)
        return jsonify(results)

    @app.post('/api/events')
    @require_login(admin=True)
    def add_event():
        return jsonify(id=EventService.save(body(), g.user['id'])), 201

    @app.put('/api/events/<int:event_id>')
    @require_login(admin=True)
    def edit_event(event_id):
        return jsonify(id=EventService.save(body(), g.user['id'], event_id))

    @app.delete('/api/events/<int:event_id>')
    @require_login(admin=True)
    def delete_event(event_id):
        db = get_db()
        with db:
            if db.execute('DELETE FROM events WHERE id=?', (event_id,)).rowcount == 0:
                raise DomainError('Tədbir tapılmadı.', 404)
        return jsonify(message='Tədbir və əlaqəli qeydiyyatlar silindi.')

    @app.post('/api/events/<int:event_id>/registration')
    @require_login()
    def register(event_id):
        RegistrationService.register(g.user['id'], event_id)
        return jsonify(message='Qeydiyyat uğurla tamamlandı.'), 201

    @app.delete('/api/events/<int:event_id>/registration')
    @require_login()
    def cancel(event_id):
        db = get_db()
        with db:
            count = db.execute('DELETE FROM registrations WHERE user_id=? AND event_id=?', (g.user['id'], event_id)).rowcount
        if not count:
            raise DomainError('Qeydiyyat tapılmadı.', 404)
        return jsonify(message='Qeydiyyat ləğv edildi.')

    @app.get('/api/stats')
    @require_login(admin=True)
    def stats():
        db = get_db()
        return jsonify(events=db.execute('SELECT COUNT(*) FROM events').fetchone()[0],
                       registrations=db.execute('SELECT COUNT(*) FROM registrations').fetchone()[0],
                       popular=[dict(x) for x in db.execute('SELECT e.title,COUNT(r.id) count FROM events e LEFT JOIN registrations r ON r.event_id=e.id GROUP BY e.id ORDER BY count DESC,e.title LIMIT 5')],
                       categories=[dict(x) for x in db.execute('SELECT c.name,COUNT(e.id) count FROM categories c LEFT JOIN events e ON e.category_id=c.id GROUP BY c.id')])

    @app.get('/api/events/<int:event_id>/participants.csv')
    @require_login(admin=True)
    def export(event_id):
        db = get_db()
        if not db.execute('SELECT id FROM events WHERE id=?', (event_id,)).fetchone():
            raise DomainError('Tədbir tapılmadı.', 404)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ad', 'E-poçt', 'Qeydiyyat vaxtı (UTC)'])
        for row in db.execute('SELECT u.name,u.email,r.created_at FROM registrations r JOIN users u ON u.id=r.user_id WHERE event_id=? ORDER BY r.id', (event_id,)):
            # Prevent spreadsheet formula injection in user-controlled cells.
            writer.writerow(["'" + x if x.lstrip().startswith(('=', '+', '-', '@')) else x for x in row])
        return Response('\ufeff' + output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=event-{event_id}-participants.csv'})

    return app
