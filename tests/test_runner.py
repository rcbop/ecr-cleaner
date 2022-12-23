from unittest.mock import MagicMock, Mock, call, patch

import pytest

from ecr_cleaner.commands import ECRCommand
from ecr_cleaner.runner import ChainCommandRunner


@pytest.fixture
def fix_command_1() -> Mock:
    return Mock(spec=ECRCommand)


@pytest.fixture
def fix_command_2() -> Mock:
    return Mock(spec=ECRCommand)


@pytest.fixture
def fix_command_3() -> Mock:
    return Mock(spec=ECRCommand)


def test_chain_command_runner_default(fix_command_1: Mock, fix_command_2: Mock):
    ecr_client = MagicMock()
    fix_command_1.execute = Mock()
    fix_command_1.execute.return_value = {"wow": "wow"}
    fix_command_2.execute = Mock()
    ChainCommandRunner(ecr_client).run_commands([fix_command_1, fix_command_2])
    fix_command_1.execute.assert_called_once_with(ecr_client)
    fix_command_2.execute.assert_called_once_with(
        ecr_client, fix_command_1.execute.return_value)


def test_chain_command_runner_three_commands(fix_command_1: Mock, fix_command_2: Mock, fix_command_3: Mock):
    ecr_client = Mock()
    fix_command_1.execute = Mock()
    fix_command_1.execute.return_value = {"much": "wow"}
    fix_command_2.execute = Mock()
    fix_command_2.execute.return_value = {"such": "wow"}
    fix_command_3.execute = Mock()
    fix_command_3.execute.return_value = {"very": "wow"}
    ChainCommandRunner(ecr_client).run_commands([fix_command_1, fix_command_2, fix_command_3])
