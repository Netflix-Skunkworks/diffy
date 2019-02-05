"""
.. module: diffy.plugins.bases.inventory
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Forest Monsen <fmonsen@netflix.com>
"""
from diffy.plugins.base import Plugin
from diffy.schema import PluginOptionSchema


class InventoryPlugin(Plugin):
    type = "inventory"
    _schema = PluginOptionSchema

    def get(self, **kwargs):
        raise NotImplementedError
