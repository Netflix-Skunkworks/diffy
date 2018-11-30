"""
.. module: diffy.plugins.diffy_s3.plugin
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from typing import List

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from marshmallow import fields

from diffy.config import CONFIG
from diffy.exceptions import TargetNotFound
from diffy.schema import DiffyInputSchema
from diffy.plugins import diffy_aws as aws
from diffy.plugins.bases import PersistencePlugin, TargetPlugin, CollectionPlugin

from .s3 import save_file, load_file
from .ssm import process
from .auto_scaling import describe_auto_scaling_group


logger = logging.getLogger(__name__)


def get_default_aws_account_number() -> dict:
    """Retrieves current account number"""
    sts = boto3.client('sts')
    accountId = '1234'
    try:
        accountId = sts.get_caller_identity()['Account']
    except (ClientError, NoCredentialsError) as e:
        logger.debug(f'Failed to get AWS AccountID, using Prod: {e}')
    return accountId



class AWSSchema(DiffyInputSchema):
    account_number = fields.String(
        default=get_default_aws_account_number, missing=get_default_aws_account_number
    )
    region = fields.String(
        default=CONFIG["DIFFY_DEFAULT_REGION"], missing=CONFIG["DIFFY_DEFAULT_REGION"]
    )


class S3PersistencePlugin(PersistencePlugin):
    title = "s3"
    slug = "s3-persistence"
    description = "Persist diffy collection results to S3."
    version = aws.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/diffy.git"

    def get(self, key: str, **kwargs) -> dict:
        """Fetches a result from S3."""
        logger.debug(f"Retrieving file from S3. Bucket: {self.bucket_name} Key: {key}")
        return load_file(key)

    # TODO
    def get_all(self, **kwargs):
        """Fetches all results from S3."""
        pass

    def save(self, key: str, item: str, **kwargs) -> dict:
        """Saves a result to S3."""
        logger.debug(f"Saving file to S3. Bucket: {self.bucket_name} Item: {item}")
        return save_file(key, item)


class AutoScalingTargetPlugin(TargetPlugin):
    title = "auto scaling"
    slug = "auto-scaling-target"
    description = (
        "Uses Auto Scaling Groups to determine which instances to target for analysis"
    )
    version = aws.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/diffy.git"

    _schema = AWSSchema

    def get(self, key: str, **kwargs) -> List[str]:
        """Fetches instances to target for collection."""
        logger.debug(f"Fetching instances for Auto Scaling Group. GroupName: {key}")
        groups = describe_auto_scaling_group(
            key, account_number=kwargs["account_number"], region=kwargs["region"]
        )
        logger.debug(groups)

        if not groups:
            raise TargetNotFound(target_key=key, plugin_slug=self.slug, **kwargs)

        return [x["InstanceId"] for x in groups[0]["Instances"]]


class SSMCollectionPlugin(CollectionPlugin):
    title = "ssm"
    slug = "ssm-collection"
    description = "Uses SSM to collection information for analysis."
    version = aws.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/diffy.git"

    _schema = AWSSchema

    def get(self, targets: List[str], commands: List[str], **kwargs) -> dict:
        """Queries an target via SSM."""
        logger.debug(f"Querying instances. Instances: {targets}")
        return process(
            targets,
            commands,
            incident_id=kwargs["incident_id"],
            account_number=kwargs["account_number"],
            region=kwargs["region"],
        )
