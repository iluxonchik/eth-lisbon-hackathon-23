from brownie import accounts
from brownie.test import strategy
from hypothesis import strategies as st
from hypothesis.strategies import composite

MAX_UINT256 = 2**256 - 1
MAX_UINT8 = 2**8 - 1

TOKEN_ID_STRATEGY = strategy("uint256", min_value=1, max_value=MAX_UINT256)
ADDRESS_STRATEGY = strategy("address")
UINT256_STRATEGY = strategy("uint256", min_value=0, max_value=MAX_UINT256)
UINT256_POSITIVE_STRATEGY = strategy("uint256", min_value=1, max_value=MAX_UINT256)
STRING_STRATEGY = strategy("string", max_size=100)

interactor_account_strategy: st.SearchStrategy = st.integers(min_value=1, max_value=9).map(lambda index: accounts[index])

@composite
def collateral_token_list_strategy(draw, num_elements: st.SearchStrategy = st.integers(min_value=2, max_value=10)):
    num_elements: int = draw(num_elements)
    address_list_st: st.SearchStrategy = st.lists(ADDRESS_STRATEGY, min_size=num_elements, max_size=num_elements, unique=True)
    amounts_list_st: st.SearchStrategy = st.lists(UINT256_POSITIVE_STRATEGY, min_size=num_elements, max_size=num_elements)

    address_list: list = draw(address_list_st)
    amounts_list: list = draw(amounts_list_st)

    return list(zip(address_list, amounts_list))