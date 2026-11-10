
import os
from pathlib import Path

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import SQLAlchemyError


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

# Project root: EcoPackAI_Project/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env before reading database credentials.
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE)


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

def create_database_engine():

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "ecopackai_db")

    if db_user and db_password is not None:

        database_url = URL.create(
            drivername="postgresql+psycopg",
            username=db_user,
            password=db_password,
            host=db_host,
            port=int(db_port),
            database=db_name
        )

    else:

        database_url = os.getenv("DATABASE_URL")

        if not database_url:

            raise RuntimeError(
                "Database configuration is missing. "
                "Check DB_USER and DB_PASSWORD or DATABASE_URL "
                "in your project root .env file."
            )

        database_url = make_url(database_url)

        # Ensure PostgreSQL uses Psycopg 3.
        if database_url.drivername in (
            "postgres",
            "postgresql"
        ):

            database_url = database_url.set(
                drivername="postgresql+psycopg"
            )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=1800
    )


# ==================================================
# INITIALIZE DATABASE ENGINE
# ==================================================

engine = create_database_engine()


# ==================================================
# GET DATABASE CONNECTION
# ==================================================

def get_db_connection():
    """Return a PostgreSQL database connection."""

    return engine.connect()


# ==================================================
# TEST DATABASE CONNECTION
# ==================================================

def test_database_connection():

    try:

        with get_db_connection() as connection:

            result = connection.execute(
                text("SELECT version();")
            )

            print("\nPostgreSQL connection successful!")

            print(result.scalar())

            print("\nDatabase table verification:")

            for table in [
                "materials",
                "products",
                "training_data"
            ]:

                count = connection.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar()

                print(f"{table}: {count} rows")

    except (SQLAlchemyError, RuntimeError, ValueError):

        print("\nDatabase connection failed.")
        raise


# ==================================================
# DIRECT EXECUTION
# ==================================================

if __name__ == "__main__":

    test_database_connection()
