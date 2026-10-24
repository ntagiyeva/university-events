"""Explicit demo data creation. Never runs automatically on server startup."""
from datetime import timedelta
from getpass import getpass
from werkzeug.security import generate_password_hash
from app import create_app
from app.db import get_db
from app.services import now_local

app = create_app()
with app.app_context():
    db = get_db()
    email = input('Admin e-poçtu: ').strip().lower()
    password = getpass('Admin şifrəsi (ən azı 8 simvol): ')
    if len(password) < 8 or '@' not in email:
        raise SystemExit('E-poçt və ya şifrə düzgün deyil.')
    with db:
        # Existing student accounts are never silently promoted.
        db.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',
                   ('Administrator', email, generate_password_hash(password), 'admin'))
        admin_id = db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()[0]
        if db.execute('SELECT COUNT(*) FROM events').fetchone()[0] == 0:
            examples = [('Süni intellekt və gələcəyin peşələri', 1, 7, 'Əsas korpus · Böyük akt zalı', 120),
                        ('Python ilə ilk web tətbiqin', 3, 10, 'İT laboratoriyası · Otaq 204', 30),
                        ('Startap ideyanı təqdim et', 4, 15, 'İnnovasiya mərkəzi', 60),
                        ('Elmi tədqiqatın əsasları', 2, -5, 'Kitabxana · Seminar zalı', 45)]
            for title, category, days, place, capacity in examples:
                date = (now_local() + timedelta(days=days)).replace(hour=14, minute=0).isoformat(timespec='minutes')
                db.execute('INSERT INTO events(title,description,category_id,starts_at,location,capacity,created_by) VALUES(?,?,?,?,?,?,?)',
                           (title, 'Universitet icması üçün bilik, təcrübə və yeni əlaqələr. Tədbirdə təqdimatlar və sual-cavab sessiyası keçiriləcək.', category, date, place, capacity, admin_id))
    print('Admin hesabı və nümunə tədbirlər hazırdır.')
