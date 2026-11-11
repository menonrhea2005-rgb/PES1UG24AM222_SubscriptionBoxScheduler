"""Ride share fare helpers, hardened against invalid input (Lab 7).

Every function returns None for input it cannot handle instead of crashing.
"""
import math

GST_RATE = 1.18


def _to_number(text):
    """Convert text to a finite, non-negative float, or return None."""
    try:
        value = float(text.strip())
    except (ValueError, AttributeError):
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return value


def parse_trip(text):
    """Parse 'cab:km' into (cab name, distance). Returns None if invalid."""
    if not isinstance(text, str) or text.count(':') != 1:
        return None
    cab, km = text.split(':')
    cab = cab.strip()
    distance = _to_number(km)
    if cab == "" or distance is None:
        return None
    return cab.title(), distance


def fare_average(fares_csv):
    """Average a CSV of fares, rounded to 2 decimals. Returns None if invalid."""
    if not isinstance(fares_csv, str) or fares_csv.strip() == "":
        return None
    values = [_to_number(part) for part in fares_csv.split(',')]
    if any(v is None for v in values):
        return None
    count = len(values)
    # Divide each value first so the sum can never overflow to infinity.
    return round(sum(v / count for v in values), 2)


def payable_fare(text):
    """Fare plus 18% GST minus promo, never below 0. Returns None if invalid."""
    if not isinstance(text, str) or text.count('|') != 1:
        return None
    fare_text, promo_text = text.split('|')
    fare = _to_number(fare_text)
    promo = _to_number(promo_text)
    if fare is None or promo is None:
        return None
    total = fare * GST_RATE - promo
    if not math.isfinite(total):
        return None
    return round(max(total, 0.0), 2)


def main():
    print("==== Running parse_trip ====")
    user_input = input("Enter cab:distance in km (e.g. sedan:12): ")
    result = parse_trip(user_input)
    if result is None:
        print("Invalid input: use the form cab:km with a non-negative distance")
    else:
        print("Cab and Distance:", result)

    print("\n==== Running fare_average ====")
    user_input = input("Enter fares as CSV (e.g. 120,95,210): ")
    result = fare_average(user_input)
    if result is None:
        print("Invalid input: enter non-negative numbers separated by commas")
    else:
        print("Average Fare:", result)

    print("\n==== Running payable_fare ====")
    user_input = input("Enter fare|promo (e.g. 250|30): ")
    result = payable_fare(user_input)
    if result is None:
        print("Invalid input: use the form fare|promo with non-negative numbers")
    else:
        print("Payable Fare:", result)


if __name__ == "__main__":
    main()
