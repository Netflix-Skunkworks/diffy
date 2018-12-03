"""
.. module: diffy.exceptions
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""


class DiffyException(Exception):
    """Base Diffy exception. Catch this to catch all Diffy related errors."""

    def __init__(self, *args, **kwargs):
        self.message = kwargs.pop("message", None)
        super().__init__(self.message)

    def __repr__(self):
        return f"<DiffyError: {self.message}>"


class InvalidConfiguration(DiffyException):
    """Raised on configuration issues."""

    def __init__(self, *args, **kwargs):
        """
        :param args: Exception arguments
        :param kwargs: Exception kwargs
        """
        self.message = kwargs.pop("message", None)
        super().__init__(self.message)

    def __repr__(self):
        return f"<CofigurationError: {self.message}>"


class PendingException(DiffyException):
    """Raised when an action is still pending."""

    def __init__(self, *args, **kwargs):
        """
        :param args: Exception arguments
        :param kwargs: Exception kwargs
        """
        self.message = kwargs.pop("message", None)
        super().__init__(self.message)

    def __repr__(self):
        return f"<PendingError: {self.message}>"


class SchemaError(DiffyException):
    """
       Raised on schema issues, relevant probably when creating or changing a plugin schema
       :param schema_error: The schema error that was raised
       :param args: Exception arguments
       :param kwargs: Exception kwargs
    """

    def __init__(self, schema_error, *args, **kwargs):
        kwargs["message"] = f"Schema error: {schema_error}"
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<SchemaError: {self.message}>"


class BadArguments(DiffyException):
    """
       Raised on schema data validation issues
       :param validation_error: The validation error message
       :param args: Exception arguments
       :param kwargs: Exception kwargs
    """

    def __init__(self, validation_error, *args, **kwargs):
        kwargs["message"] = f"Error with sent data: {validation_error}"
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<BadArgumentError: {self.message}>"


class TargetNotFound(DiffyException):
    """
       Raised when a target plugin cannot find the target specified.
       :param target_key: Key used for targeting
       :param plugin_slug: Plugin attempting to target
       :param args: Exception arguments
       :param kwargs: Exception kwargs
    """

    def __init__(self, target_key, plugin_slug, *args, **kwargs):
        options = ""
        for k, v in kwargs.items():
            options += f"{k}: {v} "

        kwargs[
            "message"
        ] = f"Could not find target. key: {target_key} slug: {plugin_slug} {options}"
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<TargetNotFoundError: {self.message}>"
