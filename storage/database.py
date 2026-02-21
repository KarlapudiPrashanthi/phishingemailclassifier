"""Database logic to store processed emails and prediction results."""
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL
from utils.logger import get_logger

logger = get_logger(__name__)
Base = declarative_base()

# Ensure data dir for SQLite
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if db_path:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

_engine = None
_Session = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
    return _engine


def get_session():
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _Session()


def init_db() -> None:
    """Create predictions table if not exists."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_text_preview TEXT,
                label INTEGER,
                probability REAL,
                created_at TEXT
            )
        """))
        conn.commit()
    logger.info("Database initialized")


@contextmanager
def session_scope() -> Generator:
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def store_result(email_preview: str, label: int, probability: float) -> None:
    """Store one classification result."""
    init_db()
    with session_scope() as session:
        session.execute(
            text(
                "INSERT INTO predictions (email_text_preview, label, probability, created_at) VALUES (:preview, :label, :prob, :at)"
            ),
            {
                "preview": email_preview[:500] if email_preview else "",
                "label": label,
                "prob": probability,
                "at": datetime.utcnow().isoformat(),
            },
        )


def get_recent_results(limit: int = 100) -> List[dict]:
    """Return recent predictions as list of dicts."""
    init_db()
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, email_text_preview, label, probability, created_at FROM predictions ORDER BY id DESC LIMIT :n"),
            {"n": limit},
        )
        rows = result.fetchall()
    return [
        {
            "id": r[0],
            "email_text_preview": r[1],
            "label": int(r[2]),
            "probability": float(r[3]),
            "created_at": r[4],
        }
        for r in rows
    ]
