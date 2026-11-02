"""Bank account management module.

Manages an in-memory ledger of accounts: creation, deposits, withdrawals,
promotional bonus calculation and a plain-text backup export.
"""

import hashlib
import os
import secrets

SERVICE_FEE = 2.50
PBKDF2_ITERATIONS = 100_000

account_data = {}


def create_account(acc_id, name, initial_deposit=0, transactions=None):
    """Create a new account and log the creation.

    Returns False if the account already exists or the deposit is negative.
    """
    if acc_id in account_data or initial_deposit < 0:
        return False
    if transactions is None:
        transactions = []
    transactions.append(
        f"Created {acc_id} with initial balance {initial_deposit:.2f}"
    )
    account_data[acc_id] = {
        "name": name,
        "balance": initial_deposit,
        "transactions": transactions,
    }
    return True


def deposit(acc_id, amount):
    """Add a positive amount to an account. Returns True on success."""
    if amount <= 0:
        return False
    try:
        account_data[acc_id]["balance"] += amount
    except KeyError:
        return False
    return True


def withdraw(acc_id, amount):
    """Withdraw an amount plus the service fee. Returns True on success."""
    if amount <= 0 or account_data.get(acc_id) is None:
        return False
    total = amount + SERVICE_FEE
    if account_data[acc_id]["balance"] < total:
        return False
    account_data[acc_id]["balance"] -= total
    return True


def compute_bonus(acc_id, rate):
    """Return the promotional bonus: account balance times a numeric rate."""
    balance = account_data[acc_id]["balance"]
    return balance * float(rate)


def get_hash(pin, salt=None):
    """Return a salted PBKDF2-SHA256 hash of a PIN as 'salt$digest' hex."""
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", pin.encode(), salt, PBKDF2_ITERATIONS
    )
    return salt.hex() + "$" + digest.hex()


def generate_temp_pin():
    """Return a cryptographically secure random 4-digit PIN."""
    return 1000 + secrets.randbelow(9000)


def backup_data(filename="backup.txt"):
    """Write the account ledger to a text file."""
    with open(filename, "w", encoding="utf-8") as backup_file:
        backup_file.write(str(account_data))
    print("Backup complete:", filename)


def main():
    """Run a short demo of the account operations."""
    admin_token = os.environ.get("BANK_ADMIN_TOKEN")
    create_account("A01", "Alice", 1000)
    deposit("A01", 500)
    withdraw("A01", 200)
    print("Balance:", account_data["A01"]["balance"])
    print("Bonus:", compute_bonus("A01", 0.05))
    print("PIN Hash:", get_hash("1234"))
    print("Temp PIN:", generate_temp_pin())
    backup_data()
    print("Token initialized:", admin_token is not None)


if __name__ == "__main__":
    main()
