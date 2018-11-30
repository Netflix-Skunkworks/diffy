"""
.. module: diffy.factory
    :platform: Unix
    :synopsis: This module contains all the needed functions to allow
    the factory app creation.

    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>

"""
from pprint import pformat

from logging import Formatter, StreamHandler, DEBUG
from logging.handlers import RotatingFileHandler

from flask import Flask

from diffy.config import Config, consume_envvars, DEFAULTS
from diffy.common.utils import install_plugins

from diffy_api.common.health import mod as health
from diffy_api.extensions import sentry, rq


DEFAULT_BLUEPRINTS = (health,)

API_VERSION = 1


def create_app(app_name=None, blueprints=None, config=None):
    """
    Diffy application factory

    :param config:
    :param app_name:
    :param blueprints:
    :return:
    """
    if not blueprints:
        blueprints = DEFAULT_BLUEPRINTS
    else:
        blueprints = blueprints + DEFAULT_BLUEPRINTS

    if not app_name:
        app_name = __name__

    app = Flask(app_name)
    configure_app(app, config)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)

    if app.logger.isEnabledFor(DEBUG):
        p_config = pformat(app.config)
        app.logger.debug(f"Current Configuration: {p_config}")

    return app


def configure_app(app, config=None):
    """
    Different ways of configuration

    :param app:
    :param config:
    :return:
    """
    install_plugins()

    _defaults = consume_envvars(DEFAULTS)
    default_config = Config(defaults=_defaults)

    if config:
        default_config.from_yaml(config)

    app.config.update(default_config)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def configure_extensions(app):
    """
    Attaches and configures any needed flask extensions
    to our app.

    :param app:
    """
    sentry.init_app(app)
    rq.init_app(app)


def configure_blueprints(app, blueprints):
    """
    We prefix our APIs with their given version so that we can support
    multiple concurrent API versions.

    :param app:
    :param blueprints:
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix=f"/api/{API_VERSION}")


def configure_logging(app):
    """
    Sets up application wide logging.

    :param app:
    """
    if app.config.get("LOG_FILE"):
        handler = RotatingFileHandler(
            app.config.get("LOG_FILE"), maxBytes=10_000_000, backupCount=100
        )

        handler.setFormatter(
            Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )

        handler.setLevel(app.config.get("LOG_LEVEL", "DEBUG"))
        app.logger.setLevel(app.config.get("LOG_LEVEL", "DEBUG"))
        app.logger.addHandler(handler)

    stream_handler = StreamHandler()

    stream_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
        )
    )

    stream_handler.setLevel(app.config.get("LOG_LEVEL", "DEBUG"))
    app.logger.addHandler(stream_handler)
