"""
.. module: diffy.plugins.bases.payload
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from diffy.plugins.base import Plugin
from diffy.schema import PluginOptionSchema


class PayloadPlugin(Plugin):
    type = "payload"
    _schema = PluginOptionSchema

    def generate(self, incident, **kwargs):
        raise NotImplementedError
