"""
.. module: diffy.plugins.diffy_aws.autoscaling
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Forest Monsen <fmonsen@netflix.com>
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from typing import List

from retrying import retry
from botocore.exceptions import ClientError

from .sts import sts_client

logger = logging.getLogger(__name__)


def retry_throttled(exception):
    """
    Determines if this exception is due to throttling
    :param exception:
    :return:
    """
    logger.debug(exception)
    if isinstance(exception, ClientError):
        if exception.response["Error"]["Code"] == "ThrottlingException":
            return True
    return False


@sts_client("autoscaling")
@retry(
    retry_on_exception=retry_throttled,
    stop_max_attempt_number=7,
    wait_exponential_multiplier=1000,
)
def describe_auto_scaling_group(group_name: str, **kwargs) -> List[str]:
    """Uses boto to query for command status."""
    logger.debug(f"Describing autoscaling group. AutoScalingGroupName: {group_name}")

    return kwargs["client"].describe_auto_scaling_groups(
        AutoScalingGroupNames=[group_name]
    )["AutoScalingGroups"]
