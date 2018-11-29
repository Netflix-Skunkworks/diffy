"""
.. module: diffy.plugins.bases.persistence
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from diffy.plugins.base import Plugin
from diffy.schema import PluginOptionSchema


class PersistencePlugin(Plugin):
    type = "persistence"
    _schema = PluginOptionSchema

    def get(self, file_type, key, **kwargs):
        raise NotImplementedError

    def get_all(self, **kwargs):
        raise NotImplementedError

    def save(self, file_type, key, item, **kwargs):
        raise NotImplementedError
