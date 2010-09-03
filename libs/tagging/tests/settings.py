import os
DIRNAME = os.path.dirname(__file__)

DEFAULT_CHARSET = 'utf-8'

test_engine = os.environ.get("TAGGING_TEST_ENGINE", "sqlite3")

DATABASE_ENGINE = test_engine
DATABASE_NAME = os.environ.get("TAGGING_DATABASE_NAME", "tagging_test")
DATABASE_USER = os.environ.get("TAGGING_DATABASE_USER", "")
DATABASE_PASSWORD = os.environ.get("TAGGING_DATABASE_PASSWORD", "")
DATABASE_HOST = os.environ.get("TAGGING_DATABASE_HOST", "localhost")

if test_engine == "sqlite":
    DATABASE_NAME = os.path.join(DIRNAME, 'tagging_test.db')
    DATABASE_HOST = ""
elif test_engine == "mysql":
    DATABASE_PORT = os.environ.get("TAGGING_DATABASE_PORT", 3306)
elif test_engine == "postgresql_psycopg2":
    DATABASE_PORT = os.environ.get("TAGGING_DATABASE_PORT", 5432)


INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'tagging',
    'tagging.tests',
)
