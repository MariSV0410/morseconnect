import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('morse.db')


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id_mensaje INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                codigo_morse TEXT NOT NULL,
                direccion TEXT NOT NULL,
                fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
                medio TEXT DEFAULT 'Web',
                estado_envio TEXT DEFAULT 'Local'
            )
        ''')


def save_message(texto, morse, direccion, medio='Web', estado='Local'):
    with connect() as db:
        cursor = db.execute('''
            INSERT INTO mensajes (texto, codigo_morse, direccion, medio, estado_envio)
            VALUES (?, ?, ?, ?, ?)
        ''', (texto, morse, direccion, medio, estado))
        return cursor.lastrowid


def get_messages(limit=50):
    with connect() as db:
        rows = db.execute(
            'SELECT * FROM mensajes ORDER BY id_mensaje DESC LIMIT ?', (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def clear_messages():
    with connect() as db:
        db.execute('DELETE FROM mensajes')
