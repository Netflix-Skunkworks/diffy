from typing import List

from flask import request, current_app
from functools import wraps
from inflection import camelize

from diffy_api.extensions import sentry


def format_errors(messages: List[str]) -> dict:
    errors = {}
    for k, v in messages.items():
        key = camelize(k, uppercase_first_letter=False)

        if isinstance(v, dict):
            errors[key] = format_errors(v)

        elif isinstance(v, list):
            errors[key] = v[0]

    return errors


def wrap_errors(messages):
    errors = dict(message="Validation Error.")
    if messages.get("_schema"):
        errors["reasons"] = {"Schema": {"rule": messages["_schema"]}}
    else:
        errors["reasons"] = format_errors(messages)
    return errors


def unwrap_pagination(data, output_schema):
    if not output_schema:
        return data

    if isinstance(data, dict):
        if "total" in data.keys():
            if data.get("total") == 0:
                return data

            marshaled_data = {"total": data["total"]}
            marshaled_data["items"] = output_schema.dump(data["items"], many=True).data
            return marshaled_data

        return output_schema.dump(data).data

    elif isinstance(data, list):
        marshaled_data = {"total": len(data)}
        marshaled_data["items"] = output_schema.dump(data, many=True).data
        return marshaled_data

    return output_schema.dump(data).data


def validate_schema(input_schema, output_schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if input_schema:
                if request.get_json():
                    request_data = request.get_json()
                else:
                    request_data = request.args

                data, errors = input_schema.load(request_data)

                if errors:
                    return wrap_errors(errors), 400

                kwargs["data"] = data

            try:
                resp = f(*args, **kwargs)
            except Exception as e:
                sentry.captureException()
                current_app.logger.exception(e)
                return dict(message=str(e)), 500

            if isinstance(resp, tuple):
                return resp[0], resp[1]

            if not resp:
                return dict(message="No data found"), 404

            return unwrap_pagination(resp, output_schema), 200

        return decorated_function

    return decorator
