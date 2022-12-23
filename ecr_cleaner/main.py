"""main module."""
import os

import boto3
from mypy_boto3_ecr import ECRClient

from ecr_cleaner.commands import (DescribeRegistryCommand, ECRCommand,
                                  ListRepositoriesCommand,
                                  RemoveAllUntaggedImagesCommand)
from ecr_cleaner.runner import ChainCommandRunner


class ECRCleaner():
    def __init__(self, runner: ChainCommandRunner):
        self.__runner = runner

    def clean(self, commands: list[ECRCommand]) -> None:
        self.__runner.run_commands(commands)


if __name__ == "__main__":
    aws_region = os.getenv("REGION_NAME", "us-east-1")
    aws_endpoint = os.getenv("AWS_ENDPOINT")
    ecr_client: ECRClient = boto3.client(
        "ecr", region_name=aws_region, endpoint_url=aws_endpoint)

    command_chain = [
        DescribeRegistryCommand(),
        ListRepositoriesCommand(),
        RemoveAllUntaggedImagesCommand()
    ]

    ECRCleaner(ChainCommandRunner(ecr_client)).clean(command_chain)
