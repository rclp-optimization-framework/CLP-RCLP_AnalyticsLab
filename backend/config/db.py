from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DATABASE_USER", "postgres"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABASE_HOST", "db.rukwkdtcdmltiqgiozzn.supabase.co"),
        port=int(os.getenv("DATABASE_PORT", "5432")),
        database=os.getenv("DATABASE_NAME", "postgres"),
        query={"sslmode": "require"},
    )

def build_engine():
    try:
        postgres_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with postgres_engine.connect():
            pass
        return postgres_engine
    except OperationalError as exc:
        print(f"No se pudo conectar a Supabase/PostgreSQL: {exc}. Usando SQLite local temporal.")
        return create_engine(
            "sqlite:///./rclp_local.db",
            connect_args={"check_same_thread": False},
        )


engine = build_engine()

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
