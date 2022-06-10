"""ATM fixtures"""

from decimal import Decimal

import pytest

from atm.account import Account
from atm.bank import Bank


@pytest.fixture
def balance():
    return Decimal(50.0)


@pytest.fixture
def account(balance):
    yield Account("0", "0", balance)


@pytest.fixture
def bank(account):
    yield Bank([account])
