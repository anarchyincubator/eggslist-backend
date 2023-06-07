import environ

env = environ.Env()
APP_DIR = environ.Path(__file__) - 3
env.read_env(str(APP_DIR.path(".env")))


if env("ENVIRONMENT") == "development":
    from .development import *  # noqa
elif env("ENVIRONMENT") == "local":
    try:
        from .local import *  # noqa
    except ImportError:
        from .development import *  # noqa
else:
    from .production import *  # noqa
