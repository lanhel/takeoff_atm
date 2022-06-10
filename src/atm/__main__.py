"""Main entry point"""

import atm


def main(args=None):
    bank = atm.Bank.create_bank()
    machine = atm.ATMMachine(bank)
    machine()


if __name__ == "__main__":
    main()
