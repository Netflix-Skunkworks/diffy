"""
.. module: diffy.schemas
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from marshmallow import fields

from diffy.schema import (
    TargetPluginSchema,
    PersistencePluginSchema,
    CollectionPluginSchema,
    PayloadPluginSchema,
    AnalysisPluginSchema
)
from diffy_api.common.schema import DiffyInputSchema


class BaselineSchema(DiffyInputSchema):
    target_key = fields.String(required=True)
    incident_id = fields.String(required=True)
    target_plugin = fields.Nested(TargetPluginSchema, missing={})
    persistence_plugin = fields.Nested(PersistencePluginSchema, missing={})
    collection_plugin = fields.Nested(CollectionPluginSchema, missing={})
    payload_plugin = fields.Nested(PayloadPluginSchema, missing={})


class AnalysisSchema(BaselineSchema):
    analysis_plugin = fields.Nested(AnalysisPluginSchema, missing={})


baseline_input_schema = BaselineSchema()
baseline_output_schema = BaselineSchema()
analysis_input_schema = AnalysisSchema()
analysis_output_schema = AnalysisSchema()

