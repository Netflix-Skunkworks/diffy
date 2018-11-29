"""
.. module: diffy.plugins.diffy_aws.s3
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import json
import logging

from retrying import retry
from botocore.exceptions import ClientError

from .sts import sts_client

from diffy.config import CONFIG

logger = logging.getLogger(__name__)


@retry(
    stop_max_attempt_number=3,
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
)
def _get_from_s3(client, bucket, data_file):
    return client.get_object(Bucket=bucket, Key=data_file)["Body"].read()


@retry(
    stop_max_attempt_number=3,
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
)
def _put_to_s3(client, bucket, data_file, body):
    return client.put_object(
        Bucket=bucket,
        Key=data_file,
        Body=body,
        ContentType="application/json",
        CacheControl="no-cache, no-store, must-revalidate",
    )


@sts_client("s3")
def load_file(key: str, **kwargs) -> dict:
    """Tries to load JSON data from S3."""
    bucket = CONFIG.get("DIFFY_AWS_PERSISTENCE_BUCKET")
    logger.debug(f"Loading item from s3. Bucket: {bucket} Key: {key}")
    try:
        data = _get_from_s3(kwargs["client"], bucket, key)

        data = data.decode("utf-8")

        return json.loads(data)
    except ClientError as e:
        logger.exception(e)
    assert False


@sts_client("s3")
def save_file(key: str, item: str, dry_run=None, **kwargs) -> dict:
    """Tries to write JSON data to data file in S3."""
    bucket = CONFIG.get("DIFFY_AWS_PERSISTENCE_BUCKET")
    logger.debug(f"Writing item to s3. Bucket: {bucket} Key: {key}")

    if not dry_run:
        return _put_to_s3(kwargs["client"], bucket, key, item)
    return {}
