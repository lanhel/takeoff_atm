"""ATM Machine"""

import re
import sys
import decimal

from .account_login import AccountLogin


class ATMMachine(object):
    """A specific ATM machine.

    This assumes that `stdout` is attached to the display screen to display
    message to the customer.
    """

    def __init__(self, bank, cash=10000):
        self.bank = bank
        self.cash = decimal.Decimal(cash)
        self.__account_login = None

    def __call__(self):
        """Start running the ATM."""
        input_re = re.compile(r"""^(?P<command>\S+)\s+(?P<params>.+)?$""")
        cmd_map = {
            "authorize": self.authorize,
            "withdraw": self.withdraw,
            "deposit": self.deposit,
            "balance": self.balance,
            "history": self.history,
            "logout": self.logout,
        }

        with decimal.localcontext() as ctx:
            ctx.prec = 12
            while True:
                mo = input_re.match(input("--> ") + " ")
                if mo is None:
                    print("Invalid Command", file=sys.stderr)
                    continue
                if mo.groupdict()["command"] == "end":
                    break
                command = cmd_map.get(mo.groupdict()["command"], None)
                if command is None:
                    print(
                        "Invalid Command:", mo.groupdict()["command"], file=sys.stderr
                    )
                    continue
                params = mo.groupdict()["params"]
                command(params)

    @property
    def account(self):
        """The current authorized account on this machine. If no account is
        authorized will return `None`."""
        return self.__account_login.account if self.__account_login else None

    def authorize(self, params):
        """Authenticate a specific account on this machine.

        :param account: The account number of customer to authorize.

        :param pin: The pin given by customer.
        """
        try:
            account_id, pin = params.split()
        except AttributeError:
            print("Authorize requires account id and pin", file=sys.stderr)
            return
        except ValueError:
            print("Authorize requires account id and pin", file=sys.stderr)
            return
        try:
            account = self.bank.get_account(account_id)
            login = AccountLogin(account, pin)
            self.__account_login = login
        except AttributeError:
            print("Authorization failed.")
            return
        except PermissionError:
            print("Authorization failed.")
            return

    def logout(self, params=None):
        """Remove the current authentication against this machine. This
        method is idempotent.
        """
        if self.__account_login:
            account = self.account
            self.__account_login.close()
            self.__account_login = None
            print(f"Account {account.account_id} logged out.")
        else:
            print("No account is currently authorized.")

    def withdraw(self, params):
        """Withdraw the specified amount from the current authenticated
        customer on this machine.

        :param value: Amount to be withdrawn.
        """
        if self.account is None:
            print("Authorization required.")
            return
        try:
            value = decimal.Decimal(params)
        except TypeError:
            print("Withdraw requires a numeric quantity", file=sys.stderr)
            return
        except decimal.InvalidOperation:
            print("Withdraw requires a numeric quantity", file=sys.stderr)
            return
        if value % 20 != 0:
            print("Amount withdraw must be a multiple of $20", file=sys.stderr)
            return
        allowed = value if self.cash - value >= 0.0 else self.cash
        try:
            self.account - allowed
            self.cash = self.cash - allowed
            if allowed < value:
                print("Unable to dispense full amount requested at this time.")
            print(f"Amount dispensed: ${allowed}")
            if self.account.balance < 0.0:
                print(
                    f"You have been charged an overdraft fee of ${self.account.overdraft_fee}.",
                    end=" ",
                )
            self.balance()
        except ValueError:
            print(
                "Your account is overdrawn! You may not make withdrawals at this time."
            )

    def deposit(self, params):
        """Deposit the specified amount into the current authenticated
        customer on this machine.

        :param value: Amount to be deposited.
        """
        if self.account is None:
            print("Authorization required.")
            return
        try:
            value = decimal.Decimal(params)
        except TypeError:
            print("Deposit requires a numeric quantity", file=sys.stderr)
            return
        except decimal.InvalidOperation:
            print("Deposit requires a numeric quantity", file=sys.stderr)
            return
        self.account + value
        self.balance()

    def balance(self, params=None):
        """Displays the balance of the current authenticated customer on
        this machine.
        """
        if self.account is None:
            print("Authorization required.")
            return
        print(f"Current balance: {self.account.balance}")

    def history(self, params=None):
        """Displays a history for the current authenticated customer on
        this machine.
        """
        if self.account is None:
            print("Authorization required.")
            return
        if len(self.account.transactions) > 1:
            for transaction in self.account.transactions[:-1]:
                print(transaction)
        else:
            print("No history found")
