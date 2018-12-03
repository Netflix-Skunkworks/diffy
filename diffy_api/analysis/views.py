"""
.. module: diffy.analysis.views
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from flask import Blueprint, current_app, request
from flask_restful import reqparse, Api, Resource

from diffy.plugins.base import plugins
from diffy.exceptions import TargetNotFound

from diffy_api.core import async_analysis
from diffy_api.common.util import validate_schema
from diffy_api.schemas import analysis_input_schema, task_output_schema

mod = Blueprint("analysis", __name__)
api = Api(mod)


class AnalysisList(Resource):
    """Defines the 'baselines' endpoints"""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(AnalysisList, self).__init__()

    def get(self):
        """
        .. http:get:: /analysis
          The current list of analysiss

          **Example request**:
          .. sourcecode:: http
             GET /analysis HTTP/1.1
             Host: example.com
             Accept: application/json, text/javascript

          **Example response**:
          .. sourcecode:: http
             HTTP/1.1 200 OK
             Vary: Accept
             Content-Type: text/javascript

             # TODO

          :statuscode 200: no error
          :statuscode 403: unauthenticated
        """
        data = plugins.get(current_app.config["DIFFY_PERSISTENCE_PLUGIN"]).get_all(
            "analysis"
        )
        return data, 200

    @validate_schema(analysis_input_schema, task_output_schema)
    def post(self, data=None):
        """
        .. http:post:: /analysis
          The current list of analysiss

          **Example request**:
          .. sourcecode:: http
             GET /analysis HTTP/1.1
             Host: example.com
             Accept: application/json, text/javascript

          **Example response**:
          .. sourcecode:: http
             HTTP/1.1 200 OK
             Vary: Accept
             Content-Type: text/javascript

             # TODO

          :statuscode 200: no error
          :statuscode 403: unauthenticated
        """
        try:
            return async_analysis.queue(request.json)
        except TargetNotFound as ex:
            return {"message": ex.message}, 404


class Analysis(Resource):
    """Defines the 'baselines' endpoints"""

    def __init__(self):
        super(Analysis, self).__init__()

    def get(self, key):
        """
        .. http:get:: /analysis
          The current list of analysiss

          **Example request**:
          .. sourcecode:: http
             GET /analysis HTTP/1.1
             Host: example.com
             Accept: application/json, text/javascript

          **Example response**:
          .. sourcecode:: http
             HTTP/1.1 200 OK
             Vary: Accept
             Content-Type: text/javascript

             # TODO

          :statuscode 200: no error
          :statuscode 403: unauthenticated
        """
        plugin_slug = current_app.config["DIFFY_PERSISTENCE_PLUGIN"]
        p = plugins.get(plugin_slug)
        return p.get("analysis", key)


api.add_resource(AnalysisList, "/analysis", endpoint="analysisList")
api.add_resource(Analysis, "/analysis/<key>", endpoint="analysis")
