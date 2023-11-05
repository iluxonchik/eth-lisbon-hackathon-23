import pytest
from brownie import DeFiDe, DeFiDeTo, MyERC20
from brownie import accounts, config
from brownie.convert.datatypes import ReturnValue
from brownie.exceptions import VirtualMachineError
from brownie.network.account import Account
from brownie.network.contract import ProjectContract, ContractContainer
from brownie.network.transaction import TransactionReceipt, Status
from brownie.test import given
from hypothesis import settings, assume, example, HealthCheck
from hypothesis import strategies as st

from scripts.contracts import ContractBuilder
from tests.strategies import collateral_token_list_strategy, deploy_erc_20_tokens, UINT256_POSITIVE_STRATEGY, \
    UINT256_POSITIVE_STRATEGY_SMALLER
from hypothesis import settings as hypothesis_settings

MyERC20: ContractContainer

def get_sorted_token_from_collateral_token_list(collateral_tokens: list[tuple[str, int]]):
    """
    For each value in collateral_tokens, sort them in ascending order. Compare by the second value in the tuple.
    If the second value is the same, compare by the first value in the tuple.
    :param collateral_tokens:
    :return:
    """
    return sorted(collateral_tokens, key=lambda x: (x[1], int(x[0], 16)))

def build_expected_token_multiplier_for_base_token_amount(base_token_amount: int, collateral_tokens: list[tuple[str, int]]) -> dict[str, int]:
    """
    For each value in collateral_tokens, calculate the expected amount of tokens to be minted for the given base token amount.
    :param base_token_amount:
    :param collateral_tokens:
    :return:
    """

    sorted_tokens: list[tuple[str, int]] = get_sorted_token_from_collateral_token_list(collateral_tokens)
    base_token_amount: int = sorted_tokens[0][1]

    res: dict[str, int] = {
        token[0]: token[1] // base_token_amount
        for token in sorted_tokens
    }
    return res


@given(
collateral_tokens=collateral_token_list_strategy(),
)
def test_GIVEN_list_of_collateral_tokens_WHEN_derivative_token_is_deployed_THEN_deployment_is_successful_and_base_state_is_correct(collateral_tokens: [list[tuple[Account, int]]]):
    # GIVEN
    deployer_account: Account = accounts[0]
    collateral_tokens_str: list[tuple[str, int]] = [(token.address, amount) for token, amount in collateral_tokens]
    sorted_collateral_token_list: list[tuple[str, int]] = get_sorted_token_from_collateral_token_list(collateral_tokens_str)


    # WHEN
    derivative_token: ProjectContract = DeFiDeTo.deploy(
        collateral_tokens,
        {"from": deployer_account},
    )

    # THEN
    assert derivative_token.owner() == deployer_account
    assert derivative_token.getCollateralTokensCount() == len(sorted_collateral_token_list)

    for i in range(len(sorted_collateral_token_list)):
        assert derivative_token.collateralTokens(i) == sorted_collateral_token_list[i][0]


@hypothesis_settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    data=st.data(),
    num_tokens=st.integers(min_value=2, max_value=10),
    mint_token_amount=st.integers(min_value=1, max_value=999999999),
)
def test_GIVEN_token_derivative_contract_WHEN_mint_is_performed_THEN_correct_amount_of_tokens_are_minted(data, num_tokens: int, mint_token_amount: int):
    # GIVEN
    deployer_account: Account = accounts[0]
    deployed_tokens: list[ProjectContract] = data.draw(deploy_erc_20_tokens(account=st.just(deployer_account)))
    amounts_list: list[int] = data.draw(st.lists(UINT256_POSITIVE_STRATEGY_SMALLER, min_size=num_tokens, max_size=num_tokens))

    collateral_tokens: list[tuple[str, int]] = list(zip([token.address for token in deployed_tokens], amounts_list))
    derivative_token: ProjectContract = DeFiDeTo.deploy(
        collateral_tokens,
        {"from": deployer_account},
    )

    expected_token_amount_multiplier: dict[str, int] = build_expected_token_multiplier_for_base_token_amount(1, collateral_tokens)

    for token_addr, amount_multiplier in expected_token_amount_multiplier.items():
        token: ProjectContract = MyERC20.at(token_addr)
        token.approve(
            derivative_token,
            mint_token_amount * amount_multiplier,
            {"from": deployer_account},
        )

    # WHEN
    mint_transaction: TransactionReceipt = derivative_token.mint(mint_token_amount, {"from": deployer_account})

    # THEN
    assert mint_transaction.status == Status.Confirmed
    assert derivative_token.totalSupply() == mint_token_amount
    assert derivative_token.balanceOf(deployer_account) == mint_token_amount
    for token_addr, amount_multiplier in expected_token_amount_multiplier.items():
        token: ProjectContract = MyERC20.at(token_addr)
        assert token.balanceOf(derivative_token) == mint_token_amount * amount_multiplier


@hypothesis_settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    data=st.data(),
    num_tokens=st.integers(min_value=2, max_value=10),
    mint_token_amount=st.integers(min_value=1, max_value=999999999),
)
def test_GIVEN_token_derivative_contract_WHEN_burn_is_performed_in_full_THEN_correct_amount_of_tokens_are_returned_and_burned(data, num_tokens: int, mint_token_amount: int):
    # GIVEN
    deployer_account: Account = accounts[0]
    deployed_tokens: list[ProjectContract] = data.draw(deploy_erc_20_tokens(account=st.just(deployer_account)))
    amounts_list: list[int] = data.draw(st.lists(UINT256_POSITIVE_STRATEGY_SMALLER, min_size=num_tokens, max_size=num_tokens))

    collateral_tokens: list[tuple[str, int]] = list(zip([token.address for token in deployed_tokens], amounts_list))
    derivative_token: ProjectContract = DeFiDeTo.deploy(
        collateral_tokens,
        {"from": deployer_account},
    )

    expected_token_amount_multiplier: dict[str, int] = build_expected_token_multiplier_for_base_token_amount(1,
                                                                                                             collateral_tokens)

    for token_addr, amount_multiplier in expected_token_amount_multiplier.items():
        token: ProjectContract = MyERC20.at(token_addr)
        token.approve(
            derivative_token,
            mint_token_amount * amount_multiplier,
            {"from": deployer_account},
        )

    mint_transaction: TransactionReceipt = derivative_token.mint(mint_token_amount)
    assert mint_transaction.status == Status.Confirmed

    # WHEN
    burn_transaction: TransactionReceipt = derivative_token.burn(mint_token_amount)
    assert burn_transaction.status == Status.Confirmed

    # THEN
    for token_addr in expected_token_amount_multiplier:
        token: ProjectContract = MyERC20.at(token_addr)
        assert token.balanceOf(derivative_token) == 0




@hypothesis_settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
@given(
    data=st.data(),
    num_tokens=st.integers(min_value=2, max_value=10),
    mint_token_amount=st.integers(min_value=500, max_value=999999999),
    divider_for_burn=st.integers(min_value=1, max_value=500),
)
def test_GIVEN_token_derivative_contract_WHEN_burn_is_performed_in_partial_THEN_correct_amount_of_tokens_are_returned_and_burned(data, num_tokens: int, mint_token_amount: int, divider_for_burn: int):
    # GIVEN
    deployer_account: Account = accounts[0]
    deployed_tokens: list[ProjectContract] = data.draw(deploy_erc_20_tokens(account=st.just(deployer_account)))
    amounts_list: list[int] = data.draw(st.lists(UINT256_POSITIVE_STRATEGY_SMALLER, min_size=num_tokens, max_size=num_tokens))

    collateral_tokens: list[tuple[str, int]] = list(zip([token.address for token in deployed_tokens], amounts_list))
    derivative_token: ProjectContract = DeFiDeTo.deploy(
        collateral_tokens,
        {"from": deployer_account},
    )

    expected_token_amount_multiplier: dict[str, int] = build_expected_token_multiplier_for_base_token_amount(1,
                                                                                                             collateral_tokens)

    for token_addr, amount_multiplier in expected_token_amount_multiplier.items():
        token: ProjectContract = MyERC20.at(token_addr)
        token.approve(
            derivative_token,
            mint_token_amount * amount_multiplier,
            {"from": deployer_account},
        )

    mint_transaction: TransactionReceipt = derivative_token.mint(mint_token_amount, {"from": deployer_account})
    assert mint_transaction.status == Status.Confirmed

    amount_to_burn: int = mint_token_amount // divider_for_burn
    if amount_to_burn == 0:
        amount_to_burn = 1

    # WHEN
    burn_transaction: TransactionReceipt = derivative_token.burn(amount_to_burn, {"from": deployer_account})
    assert burn_transaction.status == Status.Confirmed

    # THEN
    for token_addr, amount_multiplier in expected_token_amount_multiplier.items():
        token: ProjectContract = MyERC20.at(token_addr)
        expected_burned: int = amount_to_burn * amount_multiplier
        expected_minted: int = mint_token_amount * amount_multiplier
        assert token.balanceOf(derivative_token) == expected_minted - expected_burned
