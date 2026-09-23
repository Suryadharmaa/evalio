from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from api.admission_engine.config import get_settings
from api.admission_engine.database import models  # noqa: F401
from api.admission_engine.database.base import Base
from api.admission_engine.database.session import normalize_database_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
if settings.DATABASE_URL is not None:
    config.set_main_option(
        "sqlalchemy.url",
        normalize_database_url(settings.DATABASE_URL.get_secret_value()).replace("%", "%%"),
    )

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
