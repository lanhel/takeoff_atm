"""Bank Account ATM Login"""


class AccountLogin(object):
    """Links an ATM to a specific Account after authentication."""

    def __init__(self, account, pin):
        self.account = account
        self.authenticated = False
        if self.account.pin == pin:
            self.authenticated = True
        else:
            raise PermissionError

    def close(self):
        self.authenticated = False
