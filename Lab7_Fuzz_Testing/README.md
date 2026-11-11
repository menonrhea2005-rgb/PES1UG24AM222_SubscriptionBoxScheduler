# Lab 7 – Fuzz Testing with Hypothesis

**Name:** Rhea Menon
**SRN:** PES1UG24AM222
**Assigned repo:** L6_L7_40 – Ride Share Fare

## Files

| File | Description |
|------|-------------|
| `ride_share_fare.py` | The application, hardened against invalid input |
| `test_ride_share_fare.py` | Hypothesis fuzz tests for all three functions |

## Tests

Each function has a "no crash" test (random text and `None`) and a property test that builds
realistic-looking input (`cab:km`, a CSV of fares, `fare|promo`) from fuzzed numbers, including
negatives, huge values, `nan` and `inf`. There are 8 tests in all.

- Buggy version: **8 failed**
- Fixed version: **8 passed**

## Bugs found by fuzzing and how they were fixed

| Function | Bug found | Fix |
|----------|-----------|-----|
| `parse_trip` | Crashes on `None`, on missing `:` and on extra `:` | Check type and that there is exactly one `:` |
| `parse_trip` | Crashes on empty or non-numeric distance | Safe number conversion that returns `None` |
| `parse_trip` | Accepts negative, `nan` and `inf` distances, and an empty cab name | Reject non-finite or negative values and blank names |
| `fare_average` | Crashes on `None`, an empty string and empty items (`1,,3`) | Check input; reject any part that is not a valid number |
| `fare_average` | Floor division gives wrong averages (`0,1` gives 0, not 0.5) | True division, rounded to 2 decimals |
| `fare_average` | `int()` rejects decimal fares like `120.5` | Fares are parsed as floats |
| `payable_fare` | Crashes on `None`, a missing `\|` and non-numeric parts | Same checks as above |
| `payable_fare` | `nan\|0` returns `nan`; huge fares return `inf` | Reject non-finite input and results |
| `payable_fare` | A negative promo increases the fare (`100\|-50` gives 168) | Reject negative fares and promos |

Invalid input now returns `None`, and `main()` prints an "Invalid input" message instead of crashing.
