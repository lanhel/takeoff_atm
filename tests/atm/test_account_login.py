"""Account login tests"""

import pytest

from atm.account_login import AccountLogin


def test_login(account):
    pin = account.pin
    login = AccountLogin(account, pin)
    assert login.authenticated


def test_login_fail(account):
    pin = account.pin + "BAD"
    with pytest.raises(PermissionError) as exc_info:
        login = AccountLogin(account, pin)
        assert not login.authenticated


def test_close(account):
    pin = account.pin
    login = AccountLogin(account, pin)
    assert login.authenticated
    login.close()
    assert not login.authenticated
