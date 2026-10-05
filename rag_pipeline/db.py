import psycopg2

from . import config


def connect():
    return psycopg2.connect(config.PG_DSN)


def init_schema(conn):
    with conn.cursor() as cur:
        cur.execute(config.SCHEMA_FILE.read_text())
    conn.commit()


def vec(v) -> str:
    """pgvector text literal, cast with %s::vector (avoids needing the pgvector client lib)."""
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"
