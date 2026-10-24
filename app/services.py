"""Business rules independent of HTTP route handling."""
from datetime import datetime, timezone, timedelta
import sqlite3
from .db import get_db

BAKU = timezone(timedelta(hours=4))


def now_local():
    return datetime.now(BAKU).replace(tzinfo=None)


class DomainError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class EventService:
    @staticmethod
    def validate(data):
        fields = ['title', 'description', 'category_id', 'starts_at', 'location', 'capacity']
        if not isinstance(data, dict) or any(str(data.get(k, '')).strip() == '' or data.get(k) is None for k in fields):
            raise DomainError('Bütün məcburi sahələri doldurun.')
        try:
            start = datetime.fromisoformat(data['starts_at'])
            if start.tzinfo is not None:
                start = start.astimezone(BAKU).replace(tzinfo=None)
            if isinstance(data['capacity'], bool) or str(data['capacity']).strip() != str(int(data['capacity'])):
                raise ValueError()
            capacity = int(data['capacity'])
            category_id = int(data['category_id'])
        except (ValueError, TypeError):
            raise DomainError('Tarix, kateqoriya və ya iştirakçı limiti düzgün deyil.')
        if start <= now_local():
            raise DomainError('Tədbirin tarixi gələcəkdə olmalıdır (Bakı vaxtı).')
        if not 1 <= capacity <= 100000:
            raise DomainError('İştirakçı limiti 1–100000 aralığında olmalıdır.')
        if not get_db().execute('SELECT id FROM categories WHERE id=?', (category_id,)).fetchone():
            raise DomainError('Kateqoriya mövcud deyil.')
        for key, limit in [('title', 150), ('description', 5000), ('location', 200)]:
            if not isinstance(data[key], str) or len(data[key].strip()) > limit:
                raise DomainError(f'{key} sahəsi düzgün deyil və ya çox uzundur.')
        return (data['title'].strip(), data['description'].strip(), category_id,
                start.isoformat(timespec='minutes'), data['location'].strip(), capacity)

    @staticmethod
    def save(data, creator, event_id=None):
        values = EventService.validate(data)
        db = get_db()
        try:
            with db:
                if event_id is None:
                    result = db.execute('INSERT INTO events(title,description,category_id,starts_at,location,capacity,created_by) VALUES(?,?,?,?,?,?,?)', values + (creator,))
                    return result.lastrowid
                if not db.execute('SELECT id FROM events WHERE id=?', (event_id,)).fetchone():
                    raise DomainError('Tədbir tapılmadı.', 404)
                db.execute('UPDATE events SET title=?,description=?,category_id=?,starts_at=?,location=?,capacity=? WHERE id=?', values + (event_id,))
                return event_id
        except sqlite3.IntegrityError:
            raise DomainError('Limit qeydiyyatdan keçmiş iştirakçı sayından az ola bilməz.', 409)


class RegistrationService:
    @staticmethod
    def register(user_id, event_id):
        db = get_db()
        try:
            # Serialize check + insert. Database trigger also enforces capacity.
            db.execute('BEGIN IMMEDIATE')
            event = db.execute('SELECT * FROM events WHERE id=?', (event_id,)).fetchone()
            if not event:
                raise DomainError('Tədbir tapılmadı.', 404)
            if datetime.fromisoformat(event['starts_at']) <= now_local():
                raise DomainError('Keçmiş tədbirə qeydiyyat mümkün deyil.', 409)
            if db.execute('SELECT id FROM registrations WHERE user_id=? AND event_id=?', (user_id, event_id)).fetchone():
                raise DomainError('Bu tədbirə artıq qeydiyyatdan keçmisiniz.', 409)
            db.execute('INSERT INTO registrations(user_id,event_id) VALUES(?,?)', (user_id, event_id))
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            raise DomainError('Tədbirdə boş yer qalmayıb.', 409)
        except Exception:
            db.rollback()
            raise
