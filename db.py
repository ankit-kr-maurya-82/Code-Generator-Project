from sqlmodel import SQLModel, create_engine

# SQLite DB in project folder
DATABASE_URL = "sqlite:///./data.db"

# `check_same_thread` required for SQLite + multithreading in dev servers
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
