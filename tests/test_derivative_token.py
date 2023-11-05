import pytest
from brownie import DeFiDe, DeFiDeTo
from brownie import accounts, config
from brownie.convert.datatypes import ReturnValue
from brownie.exceptions import VirtualMachineError
from brownie.network.account import Account
from brownie.network.contract import ProjectContract
from brownie.network.transaction import TransactionReceipt, Status
from brownie.test import given
from hypothesis import settings, assume, example
from hypothesis import strategies as st

from tests.strategies import collateral_token_list_strategy


def get_sorted_token_from_collateral_token_list(collateral_tokens: list[tuple[Account, int]]):
    """
    For each value in collateral_tokens, sort them in ascending order. Compare by the second value in the tuple.
    If the second value is the same, compare by the first value in the tuple.
    :param collateral_tokens:
    :return:
    """
    return sorted(collateral_tokens, key=lambda x: (x[1], int(x[0].address, 16)))


@given(
collateral_tokens=collateral_token_list_strategy(),
)
def test_GIVEN_list_of_collateral_tokens_WHEN_derivative_token_is_deployed_THEN_deployment_is_successful_and_base_state_is_correct(collateral_tokens: [list[tuple[Account, int]]]):
    # GIVEN
    deployer_account: Account = accounts[0]
    sorted_collateral_token_list: list[tuple[Account, int]] = get_sorted_token_from_collateral_token_list(collateral_tokens)


    # WHEN
    derivative_token: ProjectContract = DeFiDeTo.deploy(
        collateral_tokens,
        {"from": deployer_account},
    )

    # THEN
    assert derivative_token.owner() == deployer_account
    assert derivative_token.getCollateralTokensCount() == len(sorted_collateral_token_list)

    for i in range(len(sorted_collateral_token_list)):
        assert derivative_token.collateralTokens(i) == sorted_collateral_token_list[i][0].address
