"""Account tests"""

import pytest

from decimal import Decimal


def test_balance(balance, account):
    assert account.balance == balance


def test_deposit(balance, account):
    account = account + 10.0
    assert account.balance == balance + Decimal(10.0)


def test_withdraw(balance, account):
    account = account - 10.0
    assert account.balance == balance - Decimal(10.0)


def test_overdraft(balance, account):
    account = account - (balance + Decimal(1.0))
    assert account.balance == -(account.overdraft_fee + Decimal(1.0))


def test_overdrawn(balance, account):
    account = account - (balance + Decimal(1.0))
    with pytest.raises(ValueError) as exc_info:
        account = account - 1.0
    assert isinstance(exc_info.value, ValueError)
