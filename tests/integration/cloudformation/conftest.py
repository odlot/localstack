import uuid
from pathlib import Path
from typing import Literal

import pytest

from localstack.services.cloudformation.resource_provider import (
    Properties,
    ResourceProviderExecutor,
    ResourceProviderPayload,
)
from localstack.utils.strings import short_uid


@pytest.fixture
def perform_cfn_operation(aws_client, aws_client_factory):
    """
    Deploys a resource, then deletes it
    """
    stack_name = f"stack-{short_uid()}"
    stack_id = f"arn:aws:::cloudformation/{stack_name}"

    executor = ResourceProviderExecutor(stack_name=stack_name, stack_id=stack_id)

    def run(
        logical_resource_id: str,
        resource_type: str,
        action: Literal["Add", "Remove"],
        resource_props: Properties,
    ):
        creds = {
            "accessKeyId": "test",
            "secretAccessKey": "test",
            "sessionToken": "",
        }
        resource_provider_payload: ResourceProviderPayload = {
            "awsAccountId": "000000000000",
            "callbackContext": {},
            "stackId": stack_name,
            "resourceType": resource_type,
            "resourceTypeVersion": "000000",
            # TODO: not actually a UUID
            "bearerToken": str(uuid.uuid4()),
            "region": "us-east-1",
            "action": action,
            "requestData": {
                "logicalResourceId": logical_resource_id,
                "resourceProperties": resource_props,
                "previousResourceProperties": None,
                "callerCredentials": creds,
                "providerCredentials": creds,
                "systemTags": {},
                "previousSystemTags": {},
                "stackTags": {},
                "previousStackTags": {},
            },
        }

        return executor.deploy_loop(resource_provider_payload)

    return run


@pytest.fixture
def template_root() -> Path:
    return Path(__file__).parent.joinpath("..", "templates")