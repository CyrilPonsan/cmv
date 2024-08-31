from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys
from dotenv import load_dotenv
from app.settings import models


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

# print(f"Path to .env file: {os.path.join(BASE_DIR, '.env')}")
load_dotenv(os.path.join(BASE_DIR, ".env"))


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# this will overwrite the ini-file sqlalchemy.url path
# with the path given in the config of the main code
# config.set_main_option("sqlalchemy.url", str(DATABASE_URL))
# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


target_metadata = models.Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # target_metadata.drop_all(connectable)
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


DATABASE_URL = os.getenv("AUTH_DATABASE_URL")
URL = str(DATABASE_URL)

# print("url" + DATABASE_URL)

if context.is_offline_mode():
    if DATABASE_URL and DATABASE_URL.strip():
        config.set_section_option("alembic", "sqlalchemy.url", str(URL))
        run_migrations_offline()
    else:
        raise ValueError("DATABASE_URL is empty or not set in the .env file")
else:
    if DATABASE_URL and DATABASE_URL.strip():
        config.set_section_option("alembic", "sqlalchemy.url", str(URL))
        run_migrations_online()
    else:
        raise ValueError("DATABASE_URL is empty or not set in the .env file")
