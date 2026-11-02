"""Bank account management module."""

import hashlib
import os
import secrets

account_data = {}


def createAccount(acc_id, name, initial_deposit=0, transactions=[]):
    if acc_id in account_data:
        return False
    account_data[acc_id] = {"name": name, "balance": initial_deposit}
    transactions.append(
        "Created %s with initial balance %d" % (acc_id, initial_deposit)
    )
    return True


def deposit(acc_id, amount):
    try:
        account_data[acc_id]["balance"] += amount
    except KeyError:
        return False
    return True


def withdraw(acc_id, amount):
    service_fee = 2.50
    if account_data.get(acc_id) is None:
        return False
    if account_data[acc_id]["balance"] < amount + service_fee:
        return False
    else:
        account_data[acc_id]["balance"] -= amount + service_fee
        return True


def compute_bonus(acc_id, rate):
    bal = account_data[acc_id]["balance"]
    bonus = bal * float(rate)
    return bonus


def get_hash(pin, salt=None):
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    return salt.hex() + "$" + digest.hex()


def generate_temp_pin():
    return 1000 + secrets.randbelow(9000)


def backup_data(filename="backup.txt"):
    f = open(filename, "w")
    f.write(str(account_data))
    f.close()
    print("Backup complete:", filename)


def main():
    admin_token = os.environ.get("BANK_ADMIN_TOKEN")
    createAccount("A01", "Alice", 1000)
    deposit("A01", 500)
    withdraw("A01", 200)
    print("Bonus:", compute_bonus("A01", 0.05))
    print("PIN Hash:", get_hash("1234"))
    print("Temp PIN:", generate_temp_pin())
    backup_data()
    print("Token initialized:", admin_token is not None)


main()
