from app.core.config import Settings

def test_database_url_rewriting():
    # Test typical Render/Heroku postgresql:// URL
    settings_pg = Settings(DATABASE_URL="postgresql://user:pass@host:5432/dbname")
    assert settings_pg.DATABASE_URL == "postgresql+asyncpg://user:pass@host:5432/dbname"

    # Test postgres:// URL
    settings_p = Settings(DATABASE_URL="postgres://user:pass@host:5432/dbname")
    assert settings_p.DATABASE_URL == "postgresql+asyncpg://user:pass@host:5432/dbname"

    # Test already async pg URL
    settings_async = Settings(DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname")
    assert settings_async.DATABASE_URL == "postgresql+asyncpg://user:pass@host:5432/dbname"

    # Test other/default URL
    settings_sqlite = Settings(DATABASE_URL="sqlite+aiosqlite:///test.db")
    assert settings_sqlite.DATABASE_URL == "sqlite+aiosqlite:///test.db"
