"""
.. module: diffy.tasks.views
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from flask import Blueprint
from flask_restful import Api, Resource

from diffy_api.extensions import rq
from diffy_api.common.util import validate_schema
from diffy_api.schemas import task_output_schema, task_list_output_schema


mod = Blueprint("tasks", __name__)
api = Api(mod)


class TaskList(Resource):
    """Defines the 'taskss' endpoints"""

    def __init__(self):
        super(TaskList, self).__init__()

    @validate_schema(None, task_list_output_schema)
    def get(self):
        """
        .. http:get:: /tasks
          The current list of tasks

          **Example request**:
          .. sourcecode:: http
             GET /tasks HTTP/1.1
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
        queue = rq.get_queue()
        data = queue.get_jobs()
        return data, 200


class Task(Resource):
    """Defines the 'taskss' endpoints"""

    def __init__(self):
        super(Task, self).__init__()

    @validate_schema(None, task_output_schema)
    def get(self, task_id):
        """
        .. http:get:: /tasks
          The current list of tasks

          **Example request**:
          .. sourcecode:: http
             GET /tasks HTTP/1.1
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
        queue = rq.get_queue()
        return queue.fetch_job(task_id)


api.add_resource(Task, "/tasks/<task_id>")
api.add_resource(TaskList, "/tasks", endpoint="tasks")
