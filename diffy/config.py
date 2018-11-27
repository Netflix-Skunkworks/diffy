"""
.. module: diffy.config
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import os
import errno
import yaml
import logging
from typing import Union, Any, Dict, Iterable

from pathlib import Path

from swag_client.util import parse_swag_config_options

from diffy.extensions import swag

from distutils.util import strtobool

logger = logging.getLogger(__name__)


AVAILABLE_REGIONS = ['us-east-1', 'us-west-2', 'eu-west-1']


def configure_swag() -> None:
    """Configures SWAG if enabled."""
    if CONFIG['DIFFY_SWAG_ENABLED']:
        swag_config = CONFIG.get_namespace('SWAG_')
        logger.debug(str(swag_config))
        swag_config = {'swag.' + k: v for k, v in swag_config.items()}
        swag.configure(**parse_swag_config_options(swag_config))
        CONFIG['DIFFY_ACCOUNTS'] = swag.get_service_enabled('diffy')


def valid_region(region) -> bool:
    if region in CONFIG['DIFFY_REGIONS']:
        return True
    return False


def consume_envvars(defaults: dict) -> dict:
    for k, v in defaults.items():
        v = os.environ.get(k, v)
        if isinstance(v, str):
            try:
                v = bool(strtobool(v))
            except ValueError:
                pass
        defaults[k] = v
    return defaults


class ConfigAttribute(object):
    """Makes an attribute forward to the config"""

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj.config[self.__name__] = value


class Config(dict):
    def __init__(self, root_path: str = None, defaults: dict = None) -> None:
        dict.__init__(self, defaults or {})
        self.root_path = root_path or os.getcwd()
        super().__init__()

    def from_envvar(self, variable_name: str, silent: bool = False) -> bool:
        """Loads a configuration from an environment variable pointing to
        a configuration file.  This is basically just a shortcut with nicer
        error messages for this line of code::

            config.from_yaml(os.environ['YOURAPPLICATION_SETTINGS'])

        :param variable_name: name of the environment variable
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        :return: bool. ``True`` if able to load config, ``False`` otherwise.
        """
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                return False
            raise RuntimeError(f'The environment variable {variable_name} is not set '
                               'and as such configuration could not be '
                               'loaded.  Set this variable and make it '
                               'point to a configuration file')
        return self.from_yaml(rv, silent=silent)

    def from_yaml(self, filename: str, silent: bool = False) -> bool:
        """Updates the values in the config from a YAML file. This function
        behaves as if the YAML object was a dictionary and passed to the
        :meth:`from_mapping` function.

        :param filename: the filename of the YAML file.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        """
        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename) as yaml_file:
                obj = yaml.safe_load(yaml_file.read())
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = f'Unable to load configuration file ({e})'
            raise e
        return self.from_mapping(obj)

    def from_mapping(self, *mapping, **kwargs) -> bool:
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys."""
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                f'expected at most 1 positional argument, got {len(mapping)}'
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self[key] = value
        return True

    def get_namespace(self, namespace: str, lowercase: bool = True, trim_namespace: bool = True) -> dict:
        """Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage::

            config['IMAGE_STORE_TYPE'] = 'fs'
            config['IMAGE_STORE_PATH'] = '/var/app/images'
            config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = config.get_namespace('IMAGE_STORE_')

        The resulting dictionary `image_store_config` would look like::

            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }

        This is often useful when configuration options map directly to
        keyword arguments in functions or class constructors.

        :param namespace: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
                          dictionary should be lowercase
        :param trim_namespace: a flag indicating if the keys of the resulting
                          dictionary should not include the namespace

        """
        rv = {}
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self):
        return f'<{self.__class__.__name__} {dict.__repr__(self)}>'


DEFAULTS: Dict[str, Union[Iterable[Any], Path, str, bool, None]] = {
    'DIFFY_ACCOUNTS': [],
    'DIFFY_REGIONS': AVAILABLE_REGIONS,
    'DIFFY_DEFAULT_REGION': 'us-west-2',
    'DIFFY_SWAG_ENABLED': False,
    'DIFFY_LOCAL_FILE_DIRECTORY': Path(__file__).resolve().parent.parent.absolute(),
    'DIFFY_AWS_PERSISTENCE_BUCKET': 'mybucket',
    'DIFFY_AWS_ASSUME_ROLE': 'Diffy',
    'DIFFY_PAYLOAD_LOCAL_COMMANDS': [
        'echo "{\\"Hello\\": \\"world\\"}"'
    ],
    'DIFFY_PAYLOAD_OSQUERY_KEY': '',
    'DIFFY_PAYLOAD_OSQUERY_REGION': 'us-west-2',
    'DIFFY_PAYLOAD_OSQUERY_COMMANDS': [
        './usr/bin/osqueryi --json "SELECT * FROM crontab"',
        "SELECT address, port, name, pid, cmdline FROM listening_ports, processes USING (pid) WHERE protocol = '6' and family = '2' AND address NOT LIKE '127.0.0.%'"
    ],
    'DIFFY_PERSISTENCE_PLUGIN': 'local-file',
    'DIFFY_TARGET_PLUGIN': 'auto-scaling-target',
    'DIFFY_PAYLOAD_PLUGIN': 'local-command',
    'DIFFY_COLLECTION_PLUGIN': 'ssm-collection',
    'DIFFY_ANALYSIS_PLUGIN': 'local-simple',
    'SWAG_TYPE': 's3',
    'SWAG_BUCKET_NAME': None,
    'SWAG_DATA_FILE': 'v2/accounts.json',
    'RQ_REDIS_URL': None,
    'LOG_FILE': None,
}


# os environ takes precedence over default
_defaults = consume_envvars(DEFAULTS)

CONFIG = Config(defaults=_defaults)
