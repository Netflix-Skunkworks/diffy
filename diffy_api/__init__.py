"""
.. module: diffy
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>


"""
import time
from flask import g, request

from diffy_api import factory
from diffy_api.baseline.views import mod as baseline_bp
from diffy_api.analysis.views import mod as analysis_bp
from diffy_api.tasks.views import mod as task_bp

DIFFY_BLUEPRINTS = (baseline_bp, analysis_bp, task_bp)


def create_app(config=None):
    app = factory.create_app(
        app_name=__name__, blueprints=DIFFY_BLUEPRINTS, config=config
    )
    configure_hook(app)
    return app


def configure_hook(app):
    """

    :param app:
    :return:
    """
    from flask import jsonify
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code

        app.logger.exception(e)
        return jsonify(error=str(e)), code

    @app.before_request
    def before_request():
        g.request_start_time = time.time()

    @app.after_request
    def after_request(response):
        # Return early if we don't have the start time
        if not hasattr(g, "request_start_time"):
            return response

        # Get elapsed time in milliseconds
        elapsed = time.time() - g.request_start_time
        elapsed = int(round(1000 * elapsed))

        # Collect request/response tags
        # tags = {
        #    'endpoint': request.endpoint,
        #    'request_method': request.method.lower(),
        #    'status_code': response.status_code
        # }

        # Record our response time metric
        app.logger.debug(
            f"Request Info: Elapsed: {elapsed} Status Code: {response.status_code} Endpoint: {request.endpoint} Method: {request.method}"
        )
        return response
