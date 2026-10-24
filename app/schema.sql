PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student','admin'))
);
CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
 category_id INTEGER NOT NULL REFERENCES categories(id), starts_at TEXT NOT NULL,
 location TEXT NOT NULL, capacity INTEGER NOT NULL CHECK(capacity > 0),
 created_by INTEGER NOT NULL REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS registrations (
 id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id,event_id)
);
CREATE INDEX IF NOT EXISTS idx_registration_event ON registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_event_date ON events(starts_at);
CREATE TRIGGER IF NOT EXISTS registration_capacity BEFORE INSERT ON registrations
WHEN (SELECT COUNT(*) FROM registrations WHERE event_id=NEW.event_id) >=
 (SELECT capacity FROM events WHERE id=NEW.event_id)
BEGIN SELECT RAISE(ABORT,'capacity_exceeded'); END;
CREATE TRIGGER IF NOT EXISTS capacity_floor BEFORE UPDATE OF capacity ON events
WHEN NEW.capacity < (SELECT COUNT(*) FROM registrations WHERE event_id=NEW.id)
BEGIN SELECT RAISE(ABORT,'capacity_below_registrations'); END;
