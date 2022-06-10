"""ATM Machine Tests"""

import decimal

import pytest

from atm.atm_machine import ATMMachine


@pytest.fixture
def atm(bank):
    sut = ATMMachine(bank)
    yield sut


@pytest.fixture
def atm_authorized(atm, account):
    atm.authorize(f"{account.account_id} {account.pin}")
    yield atm
    atm.logout


def test_no_auth(bank):
    sut = ATMMachine(bank)
    assert sut.bank == bank
    assert sut.cash == 10000
    assert sut.account is None


def test_authorize(bank, account):
    sut = ATMMachine(bank)
    sut.authorize(f"{account.account_id} {account.pin}")
    assert sut.account == account


def test_authorize_fail(capsys, bank, account):
    sut = ATMMachine(bank)
    sut.authorize(f"{account.account_id} {account.pin}_NOPE")
    assert sut.account is None
    captured = capsys.readouterr()
    assert captured.out == "Authorization failed.\n"


def test_authorize_bad_params(capsys, bank):
    sut = ATMMachine(bank)

    sut.authorize(None)
    captured = capsys.readouterr()
    assert captured.err == "Authorize requires account id and pin\n"

    sut.authorize("")
    captured = capsys.readouterr()
    assert captured.err == "Authorize requires account id and pin\n"


def test_logout(capsys, bank, account):
    sut = ATMMachine(bank)
    sut.authorize(f"{account.account_id} {account.pin}")
    assert sut.account == account

    sut.logout()
    assert sut.account is None
    captured = capsys.readouterr()
    assert captured.out == f"Account {account.account_id} logged out.\n"

    sut.logout()
    captured = capsys.readouterr()
    assert captured.out == "No account is currently authorized.\n"


@pytest.mark.parametrize(
    "method",
    [
        "withdraw",
        "deposit",
        "balance",
        "history",
    ],
)
def test_authorize_required(capsys, atm, method):
    getattr(atm, method)("")
    captured = capsys.readouterr()
    assert captured.out == "Authorization required.\n"


def test_withdraw(capsys, atm_authorized, balance):
    atm_authorized.withdraw(40)
    assert atm_authorized.account.balance == balance - 40
    captured = capsys.readouterr()
    assert captured.out == f"Amount dispensed: $40\nCurrent balance: 10\n"


def test_withdraw_overdraft(capsys, atm_authorized, balance):
    atm_authorized.withdraw(60)
    assert (
        atm_authorized.account.balance
        == balance - atm_authorized.account.overdraft_fee - 60
    )
    captured = capsys.readouterr()
    assert (
        captured.out
        == f"Amount dispensed: $60\nYou have been charged an overdraft fee of ${atm_authorized.account.overdraft_fee}. Current balance: -15\n"
    )


def test_withdraw_overdrawn(capsys, atm_authorized, balance):
    atm_authorized.withdraw(60)
    captured = capsys.readouterr()
    atm_authorized.withdraw(20)
    captured = capsys.readouterr()
    assert (
        captured.out
        == "Your account is overdrawn! You may not make withdrawals at this time.\n"
    )


def test_withdraw_no_cash(capsys, atm_authorized, balance):
    atm_authorized.cash = decimal.Decimal(20)
    atm_authorized.withdraw(60)
    captured = capsys.readouterr()
    assert (
        captured.out
        == f"Unable to dispense full amount requested at this time.\nAmount dispensed: $20\nCurrent balance: {balance - 20}\n"
    )


def test_withdraw_invalidparam(capsys, atm_authorized):
    atm_authorized.withdraw(None)
    captured = capsys.readouterr()
    assert captured.err == "Withdraw requires a numeric quantity\n"

    atm_authorized.withdraw("A")
    captured = capsys.readouterr()
    assert captured.err == "Withdraw requires a numeric quantity\n"

    atm_authorized.withdraw("30")
    captured = capsys.readouterr()
    assert captured.err == "Amount withdraw must be a multiple of $20\n"


def test_deposit(capsys, atm_authorized):
    old = atm_authorized.account.balance
    atm_authorized.deposit(50)
    assert atm_authorized.account.balance == old + 50
    captured = capsys.readouterr()
    assert captured.out == f"Current balance: {atm_authorized.account.balance}\n"


def test_deposit_invalidparam(capsys, atm_authorized):
    atm_authorized.deposit(None)
    captured = capsys.readouterr()
    assert captured.err == "Deposit requires a numeric quantity\n"

    atm_authorized.deposit("A")
    captured = capsys.readouterr()
    assert captured.err == "Deposit requires a numeric quantity\n"


def test_balance(capsys, atm_authorized):
    atm_authorized.balance()
    captured = capsys.readouterr()
    assert captured.out == f"Current balance: {atm_authorized.account.balance}\n"


def test_history(capsys, atm_authorized):
    atm_authorized.deposit(50)
    atm_authorized.withdraw(50)
    captured = capsys.readouterr()
    atm_authorized.history()
    captured = capsys.readouterr()
    assert captured.out.endswith("    50.00    100.00\n")


def test_history_none(capsys, atm_authorized):
    atm_authorized.history()
    captured = capsys.readouterr()
    assert captured.out == "No history found\n"
