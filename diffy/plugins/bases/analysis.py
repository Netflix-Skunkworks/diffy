"""
.. module: diffy.plugins.bases.analysis
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from diffy.plugins.base import Plugin
from diffy.schema import PluginOptionSchema


class AnalysisPlugin(Plugin):
    type = "analysis"
    _schema = PluginOptionSchema

    def run(self, items, **kwargs):
        raise NotImplementedError
