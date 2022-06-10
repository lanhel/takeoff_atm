"""Bank Account"""

import datetime
import dataclasses

from decimal import Decimal


class Account(object):
    """Bank account for a specific customer."""

    @dataclasses.dataclass
    class Transaction(object):
        """Contains information for a single transaction."""

        amount: Decimal
        balance: Decimal
        timestamp: datetime.datetime = None

        def __post_init__(self):
            if not isinstance(self.amount, Decimal):
                self.amount = Decimal(self.amount)
            if not isinstance(self.balance, Decimal):
                self.balance = Decimal(self.balance)
            if self.timestamp is None:
                self.timestamp = datetime.datetime.now(datetime.timezone.utc)

        def __str__(self):
            return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} {self.amount:> 8.2f} {self.balance:> 9.2f}"

    def __init__(self, account_id, pin, balance):
        self.account_id = str(account_id)
        self.pin = str(pin)
        self.transactions = [Account.Transaction(amount=0.0, balance=balance)]

    @property
    def overdraft_fee(self):
        return Decimal(5.0)

    @property
    def balance(self):
        return self.transactions[0].balance

    def __repr__(self):
        return (
            f"Account(account_id={self.account_id}, pin=****, balance={self.balance})"
        )

    def __add__(self, other):
        value = Decimal(other)
        transaction = Account.Transaction(amount=value, balance=self.balance + value)
        self.transactions.insert(0, transaction)
        return self

    def __sub__(self, other):
        if self.balance < 0.0:
            raise ValueError("Account Overdrawn")
        value = Decimal(-other)
        transaction = Account.Transaction(amount=value, balance=self.balance + value)
        self.transactions.insert(0, transaction)
        if self.balance < 0.0:
            transaction = Account.Transaction(
                amount=-self.overdraft_fee, balance=self.balance - self.overdraft_fee
            )
            self.transactions.insert(0, transaction)
        return self
