from unittest.mock import Mock, call, patch

import pytest

from ecr_cleaner.commands import (DescribeRegistryCommand,
                                  InvalidCommandInputError,
                                  ListRepositoriesCommand,
                                  RemoveAllUntaggedImagesCommand,
                                  print_operation)


@pytest.fixture
def ecr_describe_registry_response() -> dict:
    return {
        "registryId": "123456789012",
        "repositoryCount": 2,
        "imageCount": 3,
        "arn": "arn:aws:ecr:us-east-1:123456789012:registry/my-registry",
        "createdAt": 1234567890.0,
        "repositoryNames": [
            "my-registry/my-repository1",
            "my-registry/my-repository2"
        ]
    }


@pytest.fixture
def ecr_client():
    return Mock()


@patch("builtins.print")
def test_print_operation(mock_print: Mock):
    """Test print_operation decorator"""
    class TestCommand:
        def __init__(self):
            self.name = "TestCommand"

        @print_operation
        def execute(self):
            pass
    # check if the decorator prints the name of the class
    TestCommand().execute()
    mock_print.assert_called_once_with("Executing: ", "TestCommand")


def test_describe_registry_command(ecr_client: Mock, ecr_describe_registry_response: dict):
    """Test DescribeRegistryCommand"""
    # check if the command calls the correct method on the client
    command = DescribeRegistryCommand()
    command.execute(ecr_client)
    ecr_client.describe_registry.assert_called_once()

    # check if the command returns the correct response
    ecr_client.describe_registry.return_value = ecr_describe_registry_response
    response = command.execute(ecr_client)
    assert response == ecr_describe_registry_response


@pytest.fixture
def ecr_describe_repositories_response() -> dict:
    """ mocked boto3 describe_repositories response"""
    return {
        "repositories": [
            {
                "repositoryName": "my-registry/my-repository1",
                "repositoryArn": "arn:aws:ecr:us-east-1:123456789012:repository/my-registry/my-repository1",
                "createdAt": 1234567890.0,
                "registryId": "123456789012",
                "imageTagMutability": "MUTABLE",
                "imageScanningConfiguration": {
                    "scanOnPush": False
                },
                "encryptionConfiguration": {
                    "encryptionType": "AES256"
                }
            },
            {
                "repositoryName": "my-registry/my-repository2",
                "repositoryArn": "arn:aws:ecr:us-east-1:123456789012:repository/my-registry/my-repository2",
                "createdAt": 1234567890.0,
                "registryId": "123456789012",
                "imageTagMutability": "MUTABLE",
                "imageScanningConfiguration": {
                    "scanOnPush": False
                },
                "encryptionConfiguration": {
                    "encryptionType": "AES256"
                }
            }
        ]
    }


@pytest.fixture
def ecr_list_images_response() -> dict:
    return {
        "my-registry/my-repository1": {
            "imageIds": [
                {"imageDigest": "sha256:312", "imageTag": "latest"},
                {"imageDigest": "sha256:654", "imageTag": "1.0.0"},
                {"imageDigest": "sha256:987", "imageTag": "1.0.1"},
            ],
        },
        "my-registry/my-repository2": {
            "imageIds": [
                {"imageDigest": "sha256:123", "imageTag": "latest"},
                {"imageDigest": "sha256:456", "imageTag": "1.0.0"},
                {"imageDigest": "sha256:789", "imageTag": "1.0.1"},
            ],
        }
    }


def test_list_repositories_command(ecr_client: Mock, ecr_describe_registry_response: dict, ecr_describe_repositories_response: dict):
    """Test ListRepositoriesCommand"""
    command = ListRepositoriesCommand()
    ecr_client.describe_repositories.return_value = ecr_describe_repositories_response
    rtn_value = command.execute(ecr_client, ecr_describe_registry_response)
    ecr_client.describe_repositories.assert_called_once_with(
        registryId="123456789012")
    assert rtn_value == ecr_describe_repositories_response


def test_list_repositories_command_invalid_input_error(ecr_client: Mock, ecr_describe_registry_response: dict):
    """Test ListRepositoriesCommand with invalid input"""
    command = ListRepositoriesCommand()
    ecr_describe_registry_response["repositoryNames"] = []
    with pytest.raises(InvalidCommandInputError):
        command.execute(ecr_client, None)


def test_remove_all_untagged_images_command(ecr_client: Mock, ecr_describe_repositories_response: dict, ecr_list_images_response: dict):
    """Test RemoveAllUntaggedImagesCommand"""
    command = RemoveAllUntaggedImagesCommand()
    ecr_client.list_images.side_effect = [
        ecr_list_images_response["my-registry/my-repository1"],
        ecr_list_images_response["my-registry/my-repository2"]
    ]
    command.execute(ecr_client, ecr_describe_repositories_response)
    ecr_client.list_images.assert_has_calls([
        call(repositoryName="my-registry/my-repository1", filter={"tagStatus": "UNTAGGED"}),
        call(repositoryName="my-registry/my-repository2", filter={"tagStatus": "UNTAGGED"})
    ], any_order=True)
    ecr_client.batch_delete_image.assert_has_calls([
        call(repositoryName="my-registry/my-repository1", imageIds=ecr_list_images_response["my-registry/my-repository1"]["imageIds"]),
        call(repositoryName="my-registry/my-repository2", imageIds=ecr_list_images_response["my-registry/my-repository2"]["imageIds"])
    ], any_order=True)

def test_remove_all_untagged_images_command_input_error(ecr_client: Mock):
    """Test RemoveAllUntaggedImagesCommand with error"""
    command = RemoveAllUntaggedImagesCommand()
    with pytest.raises(InvalidCommandInputError):
        command.execute(ecr_client, None)