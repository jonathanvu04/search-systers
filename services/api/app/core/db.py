from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database URL. Using a local file in the project directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./prompts.db"

# For SQLite, `check_same_thread` should be False when using the connection
# across multiple threads (as FastAPI typically does).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
  """
  FastAPI dependency that provides a database session and
  makes sure it is closed after the request.
  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

