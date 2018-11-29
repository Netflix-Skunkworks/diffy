"""
.. module: diffy.plugins.bases.collection
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from diffy.plugins.base import Plugin
from diffy.schema import PluginOptionSchema


class CollectionPlugin(Plugin):
    type = "collection"
    _schema = PluginOptionSchema

    def get(self, targets, incident, commands, **kwargs):
        raise NotImplementedError
