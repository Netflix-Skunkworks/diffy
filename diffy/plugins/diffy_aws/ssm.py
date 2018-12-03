"""
.. module: diffy.plugins.diffy_aws.ssm
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Forest Monsen <fmonsen@netflix.com>
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import json
import logging
from base64 import urlsafe_b64encode
from typing import List, Tuple

from botocore.exceptions import ClientError

from retrying import retry

from diffy.filters import AWSFilter
from diffy.exceptions import PendingException
from diffy.common.utils import chunk
from .sts import sts_client

logger = logging.getLogger(__name__)
logger.addFilter(AWSFilter())


# TODO process all commands
def encode_command(string: str) -> str:
    """Base64-encode and prepare an SSM command string, to avoid shell interpolation.

    :string: String. A command or commands to be encoded.
    :returns: String. Command(s) prepared for execution.
    """
    encoded = urlsafe_b64encode(string.encode("utf-8"))
    command = f"eval $(echo {encoded} | base64 --decode)"
    return command


@sts_client("ssm")
def send_commands(
    instance_ids: List[str], commands: List[str], **kwargs
) -> Tuple[str, str]:
    """Send SSM command to target instances.

    :client: Object. AWS SSM client.
    :instance_ids: List. InstanceIds to affect.
    :incident: String. Incident name or comment.
    :commands: List(String). Commands to send to instance.
    :returns: Tuple(String, String). GUID uniquely identifying the SSM command and the current status.
    """
    logger.debug("Sending command(s) to instance(s).")

    try:
        response = kwargs["client"].send_command(
            InstanceIds=instance_ids,
            DocumentName="AWS-RunShellScript",
            Comment=kwargs.get("incident_id", ""),
            Parameters={"commands": commands},
        )
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "InvalidInstanceId":
            code = ex.response["Error"]["Code"]
            logger.error(f"AWS doesn't have a record of this instance (got {code}).")
        raise ex

    logger.debug(f"Command Response: {response}")

    return response["Command"]["CommandId"], response["Command"]["Status"]


def process(instances: List[str], commands: List[str], **kwargs) -> dict:
    """Dispatch an SSM command to each instance in a list."""
    # boto limits us to 50 per
    command_ids = {}
    for c in chunk(instances, 50):
        logger.debug(
            f"Sending command. Instances: {c} Command: {json.dumps(commands, indent=2)}"
        )
        command_id, status = send_commands(c, commands, **kwargs)
        command_ids[command_id] = [
            {"instance_id": i, "status": status, "stdout": ""} for i in c
        ]

    return poll(command_ids, **kwargs)


def retry_throttled(exception) -> bool:
    """
    Determines if this exception is due to throttling

    :param exception:
    :return:
    """
    if isinstance(exception, ClientError):
        if exception.response["Error"]["Code"] != "InvocationDoesNotExist":
            return True
    return False


@sts_client("ssm")
@retry(
    retry_on_exception=retry_throttled,
    stop_max_attempt_number=7,
    wait_exponential_multiplier=1000,
)
def get_command_invocation(command_id: str, instance_id: str, **kwargs) -> dict:
    """Uses boto to query for command status."""
    logger.debug(
        f"Getting command status. CommandId: {command_id} InstanceId: {instance_id}"
    )

    return kwargs["client"].get_command_invocation(
        CommandId=command_id, InstanceId=instance_id
    )


def is_completed(status: str) -> bool:
    """Determines if the status is deemed to be completed."""
    if status in ["Success", "TimedOut", "Cancelled", "Failed"]:
        return True
    return False


def retry_pending(exception) -> bool:
    """Determines if exception is due to commands stuck in pending state and retries."""
    return isinstance(exception, PendingException)


# TODO is this the most efficient polling wise?
@retry(retry_on_exception=retry_pending, wait_exponential_multiplier=1000)
def poll(command_ids: dict, **kwargs) -> dict:
    """Query the SSM endpoint to determine whether a command has completed.

    :returns: Dict. Results of command(s)
        command_ids = {
            'command_id': [
                {
                    'instance_id': 'i-123343243',
                    'status': 'success',
                    'collected_at' : 'dtg'
                    'stdout': {}
                }
            ]
        }
    """
    for cid, instances in command_ids.items():
        for i in instances:
            response = get_command_invocation(cid, i["instance_id"], **kwargs)

            if not is_completed(response["Status"]):
                raise PendingException("SSM command is not yet completed.")

            logger.debug(
                f"Command completed. Response: {json.dumps(response, indent=2)}"
            )

            i["status"] = response["Status"]
            i["collected_at"] = response["ExecutionEndDateTime"]

            if i["status"] != "Failed":
                i["stdout"] = json.loads(response["StandardOutputContent"])
            else:
                i["stderr"] = response["StandardErrorContent"]
                logger.error(
                    f'Failed to fetch command output. Instance: {i["instance_id"]} Reason: {response["StandardErrorContent"]}'
                )

    return command_ids
