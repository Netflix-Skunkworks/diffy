"""
.. module: diffy.plugins.bases.target
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from diffy.plugins.base import Plugin
from diffy.schema import PluginOptionSchema


class TargetPlugin(Plugin):
    type = "target"
    _schema = PluginOptionSchema

    def get(self, key, **kwargs):
        raise NotImplementedError
