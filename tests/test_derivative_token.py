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



@given(
collateral_tokens=collateral_token_list_strategy(),
)
def test_GIVEN_list_of_collateral_tokens_WHEN_derivative_token_is_deployed_THEN_deployment_is_successful(collateral_tokens: st.SearchStrategy[list[tuple]]):
    # GIVEN
    deployer_account: Account = accounts[0]
    derivative_token_name: str = "Derivative Token"
    derivative_token_symbol: str = "DERIV"

    # WHEN
    derivative_token: ProjectContract = DeFiDeTo.deploy(
        collateral_tokens,
        {"from": deployer_account},
    )
