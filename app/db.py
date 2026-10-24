"""Connection lifecycle and parameterized database access."""
import sqlite3
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


def close_db(_error=None):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()


def init_db():
    with current_app.open_resource('schema.sql') as source:
        get_db().executescript(source.read().decode('utf-8'))
    get_db().executemany('INSERT OR IGNORE INTO categories(name) VALUES(?)',
                         [(x,) for x in ['Konfrans', 'Seminar', 'Təlim', 'Müsabiqə', 'Digər']])
    get_db().commit()
