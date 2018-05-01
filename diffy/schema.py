"""
.. module: diffy.plugins.schema
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from marshmallow import fields, Schema, post_load
from marshmallow.exceptions import ValidationError

from diffy.config import CONFIG
from diffy.plugins.base import plugins


def resolve_plugin_slug(slug):
    """Attempts to resolve plugin to slug."""
    plugin = plugins.get(slug)

    if not plugin:
        raise ValidationError(f'Could not find plugin. Slug: {slug}')

    return plugin


class PluginOptionSchema(Schema):
    options = fields.Dict(missing={})


class PluginSchema(Schema):
    options = fields.Dict(missing={})

    @post_load
    def post_load(self, data):
        data['plugin'] = resolve_plugin_slug(data['slug'])
        data['options'] = data['plugin'].validate_options(data['options'])
        return data


class TargetPluginSchema(PluginSchema):
    slug = fields.String(missing=CONFIG['DIFFY_TARGET_PLUGIN'], default=CONFIG['DIFFY_TARGET_PLUGIN'], required=True)


class PersistencePluginSchema(PluginSchema):
    slug = fields.String(missing=CONFIG['DIFFY_PERSISTENCE_PLUGIN'], default=CONFIG['DIFFY_PERSISTENCE_PLUGIN'], required=True)


class CollectionPluginSchema(PluginSchema):
    slug = fields.String(missing=CONFIG['DIFFY_COLLECTION_PLUGIN'], default=CONFIG['DIFFY_COLLECTION_PLUGIN'], required=True)


class PayloadPluginSchema(PluginSchema):
    slug = fields.String(missing=CONFIG['DIFFY_PAYLOAD_PLUGIN'], default=CONFIG['DIFFY_PAYLOAD_PLUGIN'], required=True)


class AnalysisPluginSchema(PluginSchema):
    slug = fields.String(missing=CONFIG['DIFFY_ANALYSIS_PLUGIN'], default=CONFIG['DIFFY_ANALYSIS_PLUGIN'], required=True)
