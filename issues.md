# Lab 5 – Issue Table (Bank Account System)

**Student:** Rhea Menon (PES1UG24AM222)
**File:** `bank_account_system.py`

Line numbers refer to the original file. Ordered by severity, high to medium first.

| # | Issue | Type | Tool / Code | Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|----------|---------|-------------|--------------|
| 1 | Shell command injection | Security | Bandit B605 | High | 55 | `os.system("echo Backup complete: " + filename)` runs a shell command built from a parameter. A filename like `x; rm -rf ~` would run arbitrary commands. | Removed the shell call and used `print()` to report completion. |
| 2 | Weak MD5 hash for PINs | Security | Bandit B324 | High | 44 | MD5 is fast and broken, so unsalted MD5 PIN hashes can be brute-forced or looked up in rainbow tables almost instantly. | Replaced with salted `hashlib.pbkdf2_hmac("sha256", …, 100_000)` and a random 16-byte salt per hash, returned as `salt$digest`. |
| 3 | Use of `eval()` | Security | Bandit B307, Pylint W0123 | Medium | 39 | `compute_bonus` evaluated a caller-supplied string, so any Python expression (e.g. `__import__('os').system(...)`) could be executed. | Changed the API to take a numeric `rate` and return `balance * float(rate)`. The caller now passes `0.05` instead of `"bal * 0.05"`. |
| 4 | Mutable default argument | Bug | Pylint W0102 | Medium | 11 | `transactions=[]` is created once and shared by every call, so logs from different accounts pile up in the same list. | Default changed to `None`; a new list is created inside the function and stored with each account's data. |
| 5 | Withdrawal service fee never charged | Bug (logic) | Flake8 F841, Pylint W0612 | Medium | 27–34 | `service_fee = 2.50` was assigned but never used, so withdrawals were free. The original run showed a balance of 1300 instead of 1297.50. | `withdraw` now checks and deducts `amount + SERVICE_FEE`. The fee is a module constant. |
| 6 | Bare `except:` with `pass` | Bug / Security | Bandit B110, Pylint W0702, Flake8 E722 | Low (Bandit) | 20–23 | Every error in `deposit` was silently swallowed (even `KeyboardInterrupt`), so a deposit to a missing account looked successful. | Catch only `KeyError` and return `False`; return `True` on success. Non-positive amounts are also rejected. |
| 7 | Hard-coded secret token printed to console | Security | Bandit B105 | Low | 59, 67 | `admin_token = "SUPER_SECRET_BANK_TOKEN_2026"` was hard-coded in source control and printed in plain text. | Read from the `BANK_ADMIN_TOKEN` environment variable and print only whether it is set. |
| 8 | Insecure random for PIN | Security | Bandit B311 | Low | 48 | `random.randint` is a predictable pseudo-random generator and is not suitable for PINs. | Use `1000 + secrets.randbelow(9000)` (cryptographically secure). |
| 9 | File opened without `with` / encoding | Code quality | Pylint R1732, W1514 | Low | 52–54 | If `write()` raised, the file was never closed. The encoding depended on the platform. | `with open(filename, "w", encoding="utf-8") as backup_file:` |
| 10 | Non-snake_case function name | Style | Pylint C0103 | Low | 11 | `createAccount` breaks PEP 8 naming. | Renamed to `create_account` and updated the call site. |
| 11 | `%` formatting truncates floats | Bug / Style | Pylint C0209 | Low | 15 | `%d` turned balances like 1000.75 into `1000` in the log. | Replaced with an f-string using `:.2f`. |
| 12 | `== None` comparison | Style | Flake8 E711, Pylint C0121 | Low | 28 | Comparing to `None` with `==` can be overridden by `__eq__`. | Use `is None`. |
| 13 | Unnecessary `else` after `return` | Style | Pylint R1705 | Low | 32 | Extra nesting with no purpose. | Removed the `else` and de-indented. |
| 14 | Missing docstrings | Style | Pylint C0116 | Low | 11–58 | 7 functions had no docstring. | Added a docstring to every function and expanded the module docstring. |
| 15 | Unused import / unused variable | Style | Flake8 F401/F841, Pylint W0611/W0612 | Low | 6, 38 | `sys` was imported but never used; `bal` existed only for `eval`. | Removed `sys`; `balance` is now used directly in the calculation. |
| 16 | Line too long, no final newline | Style | Flake8 E501, W292; Pylint C0304 | Low | 15, 70 | Line 15 was 89 characters (limit 79), and the file did not end with a newline. | Wrapped the line and added a trailing newline. |
| 17 | `main()` runs on import | Code quality | (manual review) | Low | 70 | Importing the module ran the demo and wrote `backup.txt`. | Wrapped in `if __name__ == "__main__":`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.62 / 10 (21 messages) | **10.00 / 10** |
| Bandit | 6 issues (2 High, 1 Medium, 3 Low) | **0 issues** |
| Flake8 | 7 issues | **0 issues** |

Reports are in `reports/before/` and `reports/after/`.
