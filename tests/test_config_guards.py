import pytest

from app.core.config import Settings, assert_production_ready


def test_assert_production_ready_allows_development():
    config = Settings(environment="development")
    assert_production_ready(config)


def test_assert_production_ready_allows_test():
    config = Settings(environment="test")
    assert_production_ready(config)


def test_assert_production_ready_rejects_placeholder_jwt_secret_in_production():
    config = Settings(environment="production", jwt_secret="change-me-in-production")
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        assert_production_ready(config)


def test_assert_production_ready_rejects_dev_only_jwt_secret_in_production():
    config = Settings(environment="production", jwt_secret="dev-only-secret-change-me")
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        assert_production_ready(config)


def test_assert_production_ready_rejects_default_db_creds_in_production():
    config = Settings(
        environment="production",
        jwt_secret="my-real-secret-12345678901234567890",
        database_url="postgresql+psycopg://pocketledger:pocketledger@db:5432/pocketledger",
    )
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        assert_production_ready(config)


def test_assert_production_ready_allows_production_with_real_secrets():
    config = Settings(
        environment="production",
        jwt_secret="my-real-secret-12345678901234567890",
        database_url="postgresql+psycopg://produser:prodpass@db:5432/proddb",
    )
    assert_production_ready(config)


def test_docs_enabled_in_development():
    config = Settings(environment="development")
    docs_enabled = config.environment != "production"
    assert docs_enabled is True


def test_docs_disabled_in_production():
    config = Settings(environment="production")
    docs_enabled = config.environment != "production"
    assert docs_enabled is False
