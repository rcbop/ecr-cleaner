"""Commands"""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional

from mypy_boto3_ecr import ECRClient


class InvalidCommandInputError(Exception):
    """Error raised when command input is invalid or missing."""


def print_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Executing: ", args[0].__class__.__name__)
        return func(*args, *kwargs)
    return wrapper


class ECRCommand(ABC):
    """generic ECR SDK command"""
    @abstractmethod
    def execute(self, ecr_client: ECRClient, input: Optional[dict] = None) -> Optional[dict]:
        ...


class DescribeRegistryCommand(ECRCommand):
    @print_operation
    def execute(self, ecr_client: ECRClient, _: Optional[dict] = None) -> Optional[dict]:
        return ecr_client.describe_registry()


class ListRepositoriesCommand(ECRCommand):
    @print_operation
    def execute(self, ecr_client: ECRClient, input: Optional[dict] = None) -> Optional[dict]:
        if not input:
            raise InvalidCommandInputError(
                "must provide describe_registry response")

        describe_registry_response = input
        registry_id = describe_registry_response["registryId"]
        return ecr_client.describe_repositories(registryId=registry_id)


class RemoveAllUntaggedImagesCommand(ECRCommand):
    def __batch_remove_untagged_images(self, ecr_client: ECRClient, repository: dict) -> None:
        repository_name = repository["repositoryName"]
        untagged_images_list = ecr_client.list_images(repositoryName=repository_name, filter={
            "tagStatus": "UNTAGGED"
        })
        image_ids = untagged_images_list["imageIds"]
        ecr_client.batch_delete_image(
            repositoryName=repository_name, imageIds=image_ids)

    @print_operation
    def execute(self, ecr_client: ECRClient, input: Optional[dict] = None) -> Optional[dict]:
        if not input:
            raise InvalidCommandInputError(
                "must provide describe repository response")

        describe_repositories_response = input
        for repository in describe_repositories_response["repositories"]:
            self.__batch_remove_untagged_images(ecr_client, repository)
        return None
