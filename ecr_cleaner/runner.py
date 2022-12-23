"""run commands"""
import functools
from typing import Optional, Union

from mypy_boto3_ecr import ECRClient

from ecr_cleaner.commands import ECRCommand


class ChainCommandRunner():
    def __init__(self, ecr_client: ECRClient):
        self.__ecr_client = ecr_client

    def run_commands(self, commands: list[ECRCommand]):
        """Run commands in a chain where the output from a prevous command becomes the input of the next command."""

        def chain_reduce(current: Union[Optional[dict], ECRCommand], next: Union[Optional[dict], ECRCommand]):
            if isinstance(current, ECRCommand) and isinstance(next, ECRCommand):
                return next.execute(self.__ecr_client, current.execute(self.__ecr_client))
            if isinstance(next, ECRCommand):
                return next.execute(self.__ecr_client, current)

        functools.reduce(chain_reduce, commands)
