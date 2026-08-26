"""db.py — AI GROWTH OS Company Core를 위한 로컬 DB 연결.

정직하게 말하면: 이건 실제 배포용 PostgreSQL이 아니라 **이 저장소 안에서만 도는
SQLite 스켈레톤**이다. 사장님이 확인해준 범위(로컬 DB로 스켈레톤만, 배포 인프라
없음)를 그대로 지킨다. 나중에 실제 서비스로 배포할 때는 `DATABASE_URL` 환경변수만
Postgres 접속 문자열로 바꾸면 되게(SQLAlchemy 추상화) 만들어뒀지만, Redis·Vector DB·
Connector 등 나머지는 이 스켈레톤 범위 밖이다 — `docs/ai-growth-os-architecture.md` 참고.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./growth_os.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(bind_engine=None) -> None:
    """테이블이 없으면 만든다. 스켈레톤 단계라 Alembic 없이 create_all만 쓴다."""

    import db_models  # noqa: F401  — 모델을 등록하기 위해 import만 하면 됨

    Base.metadata.create_all(bind=bind_engine or engine)
