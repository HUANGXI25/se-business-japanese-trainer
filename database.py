import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "trainer.db"
DATABASE_URL = os.getenv("TRAINER_DB_URL", f"sqlite:///{DATABASE_FILE}")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    ensure_schema()


def ensure_schema() -> None:
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info(practice_sessions)")).fetchall()
        }
        if "start_turn" not in columns and columns:
            connection.execute(
                text("ALTER TABLE practice_sessions ADD COLUMN start_turn INTEGER DEFAULT 1")
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
