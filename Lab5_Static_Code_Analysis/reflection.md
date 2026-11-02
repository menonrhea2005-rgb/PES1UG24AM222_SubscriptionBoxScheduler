# Lab 5 – Reflection

**Student:** Rhea Menon (PES1UG24AM222)

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 style issues and most Pylint conventions. These include the unused `sys` import, `== None` → `is None`, the missing final newline, the long line, the snake_case rename and the docstrings. Each one names an exact line and rule, and the fix is mechanical and does not change behaviour.

**Hardest:** the security issues that needed a design decision, not a one-line change.
- **`eval()`:** I could not just delete it, because `compute_bonus` relied on it. I had to change the function's interface to take a numeric rate and update the caller.
- **MD5 hashing:** swapping in SHA-256 alone would still be fast and unsalted, so I used salted PBKDF2. That changed the output format to `salt$digest`.
- **Unused `service_fee`:** the tools only said "unused variable", but the real problem was a logic bug (withdrawals were never charged). Deleting the variable would have silenced the warning and hidden the bug. I had to read the code and check the program's output to see what was intended.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no outright false positives, but some findings needed judgement:
- **Bandit B105 (hard-coded password):** Bandit guesses from the variable name and string, so it reports only *Medium confidence*. Here it was a real problem, but the same pattern would fire on a harmless constant such as `TOKEN_HEADER = "Authorization"`.
- **Bandit B311 (`random`):** this is a false positive whenever `random` is used for non-security work, such as shuffling demo data. Here it generated a PIN, so it was valid.
- **Flake8 F841 / Pylint W0612 (unused `service_fee`):** the warning was correct, but the obvious "fix" (deleting the line) would have been wrong. The tool found the symptom, not the cause.

Several issues were reported by two or three tools at once (bare `except`, unused variables, `== None`). That is useful for confirming a problem, but the reports overlap, so the raw issue count overstates how many distinct problems there are.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint in the editor (VS Code extensions) so issues show up while typing. Add a **pre-commit hook** (`pre-commit` with flake8, pylint and bandit) so badly formatted or insecure code cannot be committed.
- **In CI:** add a GitHub Actions job that runs all three tools on every push and pull request. The build fails if Bandit finds any Medium/High issue, Flake8 reports anything, or the Pylint score drops below a threshold (e.g. `pylint --fail-under=9.5`).
- **Configuration:** keep a shared `.pylintrc` / `setup.cfg` / `.bandit` in the repo so the whole team uses the same rules. Any suppression (`# nosec`, `# pylint: disable=`) must be explicit and justified in code review.

### 4. What tangible improvements did you observe in code quality, readability, or potential robustness after applying the fixes?

- **Security:** all six Bandit findings are gone. There is no shell execution, no `eval`, no MD5, no hard-coded secret and no predictable PIN generator.
- **Correctness:** the program now gives the right answer. The service fee is charged (balance 1297.50 instead of 1300). Each account keeps its own transaction log instead of one shared list. Deposits to missing accounts and negative amounts are rejected instead of silently ignored, and balances are no longer truncated by `%d`.
- **Robustness:** the backup file is always closed (`with`) and written in a fixed encoding. Importing the module no longer runs the demo or writes files.
- **Readability and maintainability:** every function has a docstring. Names follow PEP 8, magic numbers are named constants, and control flow is flatter. The Pylint score went from **5.62 to 10.00/10**, and Flake8 reports nothing.
