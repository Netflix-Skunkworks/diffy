"""
.. module: diffy.plugins.diffy_aws.sts
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from functools import wraps

import boto3

from diffy.config import CONFIG

logger = logging.getLogger(__name__)


def sts_client(service, service_type="client"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            sts = boto3.client("sts")

            account_number = kwargs["account_number"]
            role = CONFIG.get("DIFFY_AWS_ASSUME_ROLE", "Diffy")

            arn = f"arn:aws:iam::{account_number}:role/{role}"

            kwargs.pop("account_number")

            # TODO add incident specific information to RoleSessionName
            logger.debug(f"Assuming role. Arn: {arn}")
            role = sts.assume_role(RoleArn=arn, RoleSessionName="diffy")

            if service_type == "client":
                client = boto3.client(
                    service,
                    region_name=kwargs["region"],
                    aws_access_key_id=role["Credentials"]["AccessKeyId"],
                    aws_secret_access_key=role["Credentials"]["SecretAccessKey"],
                    aws_session_token=role["Credentials"]["SessionToken"],
                )
                kwargs["client"] = client
            elif service_type == "resource":
                resource = boto3.resource(
                    service,
                    region_name=kwargs["region"],
                    aws_access_key_id=role["Credentials"]["AccessKeyId"],
                    aws_secret_access_key=role["Credentials"]["SecretAccessKey"],
                    aws_session_token=role["Credentials"]["SessionToken"],
                )
                kwargs["resource"] = resource
            return f(*args, **kwargs)

        return decorated_function

    return decorator
