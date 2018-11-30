"""
.. module: diffy.plugins.base.v1
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from threading import local
from typing import List, Tuple, Optional, Any

from marshmallow_jsonschema import JSONSchema


logger = logging.getLogger(__name__)


# stolen from https://github.com/getsentry/sentry/
class PluginMount(type):
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if IPlugin in bases:
            return new_cls
        if new_cls.title is None:
            new_cls.title = new_cls.__name__
        if not new_cls.slug:
            new_cls.slug = new_cls.title.replace(" ", "-").lower()
        return new_cls


class IPlugin(local):
    """
    Plugin interface. Should not be inherited from directly.
    A plugin should be treated as if it were a singleton. The owner does not
    control when or how the plugin gets instantiated, nor is it guaranteed that
    it will happen, or happen more than once.
    >>> from diffy.plugins import Plugin
    >>>
    >>> class MyPlugin(Plugin):
    >>>     def get_title(self):
    >>>         return 'My Plugin'
    As a general rule all inherited methods should allow ``**kwargs`` to ensure
    ease of future compatibility.
    """

    # Generic plugin information
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    author_url: Optional[str] = None
    resource_links = ()

    _schema: Any = None

    # Global enabled state
    enabled: bool = True
    can_disable: bool = True

    def validate_options(self, options: dict) -> Any:
        """
        Validates given options against defined schema.
        >>> plugin.validate_options(options)
        """
        return self._schema(strict=True).load(options).data

    @property
    def json_schema(self):
        """Returns JSON Schema of current plugin schema."""
        return JSONSchema().dump(self._schema()).data

    def is_enabled(self) -> bool:
        """
        Returns a boolean representing if this plugin is enabled.
        If ``project`` is passed, it will limit the scope to that project.
        >>> plugin.is_enabled()
        """
        if not self.enabled:
            return False
        if not self.can_disable:
            return True

        return True

    def get_title(self) -> Optional[str]:
        """
        Returns the general title for this plugin.
        >>> plugin.get_title()
        """
        return self.title

    def get_description(self) -> Optional[str]:
        """
        Returns the description for this plugin. This is shown on the plugin configuration
        page.
        >>> plugin.get_description()
        """
        return self.description

    def get_resource_links(self) -> List[Any]:
        """
        Returns a list of tuples pointing to various resources for this plugin.
        >>> def get_resource_links(self):
        >>>     return [
        >>>         ('Documentation', 'https://diffy.readthedocs.io'),
        >>>         ('Bug Tracker', 'https://github.com/Netflix/diffy/issues'),
        >>>         ('Source', 'https://github.com/Netflix/diffy'),
        >>>     ]
        """
        return self.resource_links


class Plugin(IPlugin):
    """
    A plugin should be treated as if it were a singleton. The owner does not
    control when or how the plugin gets instantiated, nor is it guaranteed that
    it will happen, or happen more than once.
    """

    __version__ = 1
    __metaclass__ = PluginMount
