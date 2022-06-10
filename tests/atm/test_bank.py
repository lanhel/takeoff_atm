"""Bank tests"""

from atm.bank import Bank


def test_get_account(account):
    sut = Bank([account])
    assert account == sut.get_account(account.account_id)


def test_get_account_missing(account):
    sut = Bank([account])
    assert sut.get_account(account.account_id + "NO") is None


def test_str():
    sut = Bank([])
    assert str(sut) is not None
