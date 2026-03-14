import os
import tempfile
from pathlib import Path

import pytest


def pytest_configure() -> None:
    test_db_file = Path(tempfile.gettempdir()) / "nihonngo-pytest.db"
    if test_db_file.exists():
        test_db_file.unlink()
    os.environ["TRAINER_DB_URL"] = f"sqlite:///{test_db_file}"


@pytest.fixture(autouse=True)
def reset_test_db():
    from database import SessionLocal, init_db
    from models import MistakeNote, PracticeSession, PracticeTurn, Setting

    init_db()
    db = SessionLocal()
    try:
        db.query(MistakeNote).delete()
        db.query(PracticeTurn).delete()
        db.query(PracticeSession).delete()
        db.query(Setting).delete()
        db.commit()
        yield
    finally:
        db.close()
