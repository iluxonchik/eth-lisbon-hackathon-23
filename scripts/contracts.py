import random
from typing import cast, Optional

from brownie import MyERC20
from brownie.network.account import Account
from brownie.network.contract import ContractContainer, ProjectContract
from brownie.network.transaction import TransactionReceipt
from web3.constants import ADDRESS_ZERO



def force_deploy_contract_instance(contract_cls: ContractContainer, account: Account, *deploy_args) -> ProjectContract:
    deploy_args += ({"from": account},)
    return contract_cls.deploy(*deploy_args)


def get_or_create_deployed_instance(contract_cls: ContractContainer, account: Account, *deploy_args) -> ProjectContract:
    try:
        return contract_cls[0]
    except IndexError:
        return force_deploy_contract_instance(contract_cls, account, *deploy_args)


class ContractBuilder:

    ERC_20_SUPPLY: int = 2 ** 256 - 1

    def __init__(self, *, account: Account, force_deploy: bool = False):
        self._account: Account = account
        self._force_deploy: bool = force_deploy

    @classmethod
    def get_my_erc20_contract(cls, *, account: Account, force_deploy: bool = False) -> MyERC20:
        args: tuple = (MyERC20, account, "Jasmine", "JSM", cls.ERC_20_SUPPLY)
        return force_deploy_contract_instance(*args) if force_deploy else get_or_create_deployed_instance(*args)

    @property
    def MyERC20(self) -> MyERC20:
        return self.get_my_erc20_contract(account=self._account, force_deploy=self._force_deploy)

    @classmethod
    def deploy_my_erc_20_with_distribution(cls, *, deployer: Account, holders: list[Account]) -> MyERC20:
        my_erc_20: MyERC20 = cls.get_my_erc20_contract(account=deployer, force_deploy=True)
        for holder in holders:
            my_erc_20.transfer(holder, cls.ERC_20_SUPPLY // len(holders), {"from": deployer})

        return my_erc_20
