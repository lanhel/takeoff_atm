"""Bank"""

import csv
import io
import textwrap

from .account import Account


class Bank(object):
    """Bank that owns various resources such as ATM or customer accounts."""

    def __init__(self, accounts):
        self.accounts = set(accounts)

    def get_account(self, account_id):
        for account in self.accounts:
            if account.account_id == account_id:
                return account

    def __str__(self):
        return f"<Bank: Accounts {len(self.accounts)}>"

    @classmethod
    def create_bank(cls):
        """Create a bank and initialize with startup information.

        This is to ease setup while in a test and demo mode. It is not meant
        to be used in a production environment.
        """

        # Read and parse the CSV accounts file
        def from_csv(row):
            name_map = {"ACCOUNT_ID": "account_id", "PIN": "pin", "BALANCE": "balance"}
            return {name_map[key]: value for key, value in row.items()}

        accounts_csv = textwrap.dedent(
            """
            ACCOUNT_ID,PIN,BALANCE
            2859459814,7386,10.24
            1434597300,4557,90000.55
            7089382418,0075,0.00
            2001377812,5950,60.00
        """
        ).lstrip()
        accounts_csvfile = io.StringIO(accounts_csv)
        accounts_reader = csv.DictReader(accounts_csvfile)
        accounts = [Account(**from_csv(row)) for row in accounts_reader]
        return cls(accounts)
