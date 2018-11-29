"""
.. module: diffy.baseline.views
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from flask import Blueprint, current_app, request
from flask_restful import Api, Resource

from diffy.plugins.base import plugins
from diffy.exceptions import TargetNotFound
from diffy_api.core import async_baseline
from diffy_api.common.util import validate_schema
from diffy_api.schemas import (
    baseline_input_schema,
    baseline_output_schema,
    task_output_schema,
)


mod = Blueprint("baselines", __name__)
api = Api(mod)


class BaselineList(Resource):
    """Defines the 'baselines' endpoints"""

    def __init__(self):
        super(BaselineList, self).__init__()

    @validate_schema(None, baseline_output_schema)
    def get(self):
        """
        .. http:get:: /baselines
          The current list of baselines

          **Example request**:
          .. sourcecode:: http
             GET /baselines HTTP/1.1
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
            "baseline"
        )
        return data, 200

    @validate_schema(baseline_input_schema, task_output_schema)
    def post(self, data=None):
        """
        .. http:post:: /baselines
          The current list of baselines

          **Example request**:
          .. sourcecode:: http
             POST /baselines HTTP/1.1
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
            return async_baseline.queue(request.json)
        except TargetNotFound as ex:
            return {"message": ex.message}, 404


class Baseline(Resource):
    """Defines the 'baselines' endpoints"""

    def __init__(self):
        super(Baseline, self).__init__()

    def get(self, key):
        """
        .. http:get:: /baselines
          The current list of baselines

          **Example request**:
          .. sourcecode:: http
             GET /baselines HTTP/1.1
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
        return plugins.get(current_app.config["DIFFY_PERSISTENCE_PLUGIN"]).get(
            "baseline", key
        )


api.add_resource(Baseline, "/baselines/<key>")
api.add_resource(BaselineList, "/baselines", endpoint="baselines")
