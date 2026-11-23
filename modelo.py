import os

import pymysql.cursors

# Credenciales por variable de entorno — nunca hardcodeadas en el repo.
# Ver .env.example. La contraseña es obligatoria: si falta, falla ruidosamente
# al arrancar en vez de intentar conectar con un valor por defecto silencioso.
DB_HOST = os.environ.get("FORUM_DB_HOST", "localhost")
DB_NAME = os.environ.get("FORUM_DB_NAME", "forum")
DB_USER = os.environ.get("FORUM_DB_USER", "forum")
DB_PASSWORD = os.environ["FORUM_DB_PASSWORD"]


def _conectar():
    return pymysql.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
        # Modo estricto: MySQL rechaza datos que no caben o son inválidos en vez
        # de truncarlos en silencio (lo que permitía differenciales de parser,
        # p. ej. 'webmaster'+emoji truncado a 'webmaster'). Fallar ruidoso.
        init_command="SET sql_mode='STRICT_TRANS_TABLES'",
        cursorclass=pymysql.cursors.DictCursor,
    )


def get_all(cons, dat):
    con = _conectar()
    try:
        cur = con.cursor()
        cur.execute(cons, dat)
        return cur.fetchall()
    finally:
        con.close()


def get_one(cons, dat):
    con = _conectar()
    try:
        cur = con.cursor()
        cur.execute(cons, dat)
        return cur.fetchone()
    finally:
        con.close()


def set_dat(cons, dat):
    con = _conectar()
    try:
        cur = con.cursor()
        cur.execute(cons, dat)
        con.commit()
    finally:
        con.close()
