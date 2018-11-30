"""
.. module: diffy.tests.conftest
    :platform: Unix
    :copyright: (c) 2018 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Kevin Glisson <kglisson@netflix.com>
"""
import os
import pytest

import boto3

from moto import mock_ssm, mock_iam, mock_sts, mock_ec2, mock_s3, mock_autoscaling


from diffy_api import create_app


@pytest.yield_fixture(scope="session")
def app(request):
    """
    Creates a new Flask application for a test duration.
    Uses application factory `create_app`.
    """
    _app = create_app(os.path.dirname(os.path.realpath(__file__)) + "/config.yml")
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope="function")
def client(app, client):
    yield client


@pytest.fixture(scope="function")
def s3():
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture(scope="function")
def ec2():
    with mock_ec2():
        yield boto3.client("ec2", region_name="us-east-1")


@pytest.fixture(scope="function")
def autoscaling():
    with mock_autoscaling():
        yield boto3.client("autoscaling", region_name="us-east-1")


@pytest.fixture(scope="function")
def ssm():
    with mock_ssm():
        yield boto3.client("ssm", region_name="us-east-1")


@pytest.fixture(scope="function")
def sts():
    with mock_sts():
        yield boto3.client("sts", region_name="us-east-1")


@pytest.fixture(scope="function")
def iam():
    with mock_iam():
        yield boto3.client("iam", region_name="us-east-1")


@pytest.fixture(scope="function")
def swag_accounts(s3):
    from swag_client.backend import SWAGManager
    from swag_client.util import parse_swag_config_options

    bucket_name = "SWAG"
    data_file = "accounts.json"
    region = "us-east-1"
    owner = "third-party"

    s3.create_bucket(Bucket=bucket_name)
    os.environ["SWAG_BUCKET"] = bucket_name
    os.environ["SWAG_DATA_FILE"] = data_file
    os.environ["SWAG_REGION"] = region
    os.environ["SWAG_OWNER"] = owner

    swag_opts = {
        "swag.type": "s3",
        "swag.bucket_name": bucket_name,
        "swag.data_file": data_file,
        "swag.region": region,
        "swag.cache_expires": 0,
    }

    swag = SWAGManager(**parse_swag_config_options(swag_opts))

    account = {
        "aliases": ["test"],
        "contacts": ["admins@test.net"],
        "description": "LOL, Test account",
        "email": "testaccount@test.net",
        "environment": "test",
        "id": "012345678910",
        "name": "testaccount",
        "owner": "third-party",
        "provider": "aws",
        "sensitive": False,
        "services": [],
    }

    swag.create(account)


@pytest.fixture(scope="function")
def diffy_s3_bucket(s3):
    bucket_name = "test_bucket"
    os.environ["DIFFY_AWS_PERSISTENCE_BUCKET"] = bucket_name
    yield s3.create_bucket(Bucket=bucket_name)


@pytest.fixture(scope="function")
def diffy_autoscaling_group(ec2, autoscaling):
    vpc = ec2.create_vpc(CidrBlock="10.11.0.0/16")
    subnet1 = ec2.create_subnet(
        VpcId=vpc["Vpc"]["VpcId"],
        CidrBlock="10.11.1.0/24",
        AvailabilityZone="us-east-1a",
    )

    _ = autoscaling.create_launch_configuration(
        LaunchConfigurationName="test_launch_configuration"
    )

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName="test_asg",
        LaunchConfigurationName="test_launch_configuration",
        MinSize=0,
        MaxSize=4,
        DesiredCapacity=2,
        Tags=[
            {
                "ResourceId": "test_asg",
                "ResourceType": "auto-scaling-group",
                "Key": "propogated-tag-key",
                "Value": "propogate-tag-value",
                "PropagateAtLaunch": True,
            }
        ],
        VPCZoneIdentifier=subnet1["Subnet"]["SubnetId"],
    )

    instances_to_add = [
        x["InstanceId"]
        for x in ec2.run_instances(ImageId="", MinCount=1, MaxCount=1)["Instances"]
    ]

    autoscaling.attach_instances(
        AutoScalingGroupName="test_asg", InstanceIds=instances_to_add
    )

    yield ec2, autoscaling


@pytest.fixture(scope="function")
def diffy_role(iam):
    os.environ["DIFFY_ROLE"] = "Diffy"
    yield iam.create_role(RoleName="Diffy", AssumeRolePolicyDocument="{}")
