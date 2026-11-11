"""Lab 7: Fuzz tests for ride_share_fare.py using Hypothesis.

Two kinds of tests for each function:
1. "No crash" tests: throw random text (and None) at the function. It must
   never raise an exception.
2. Property tests: build inputs that *look* valid (cab:km, CSV of fares,
   fare|promo) but use fuzzed numbers, including negatives, huge values,
   NaN and infinity. Any result the function returns must make sense.

For invalid input, the hardened functions return None instead of crashing.
"""
import math

from hypothesis import given, strategies as st

from ride_share_fare import parse_trip, fare_average, payable_fare

# Numbers written the way a user might type them, including nasty ones.
any_number = st.one_of(
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
).map(str)
weird_number_text = st.sampled_from(
    ["nan", "inf", "-inf", "1e309", "-0", "", " ", "abc", "1_000", "12.5.3"]
)
number_text = any_number | weird_number_text


# ---------------------------------------------------------------- parse_trip

@given(st.text() | st.none())
def test_parse_trip_no_crash(s):
    try:
        parse_trip(s)
    except Exception as e:
        assert False, f"parse_trip crashed with: {e!r}"


@given(st.text(), number_text)
def test_parse_trip_valid_result(cab, km):
    try:
        result = parse_trip(f"{cab}:{km}")
    except Exception as e:
        assert False, f"parse_trip crashed with: {e!r}"
    if result is not None:
        name, distance = result
        assert name != "", "cab name should not be empty"
        assert math.isfinite(distance), f"distance is not finite: {distance}"
        assert distance >= 0, f"distance is negative: {distance}"


# -------------------------------------------------------------- fare_average

@given(st.text() | st.none())
def test_fare_average_no_crash(s):
    try:
        fare_average(s)
    except Exception as e:
        assert False, f"fare_average crashed with: {e!r}"


@given(st.lists(number_text, min_size=0, max_size=8))
def test_fare_average_valid_result(fares):
    try:
        result = fare_average(",".join(fares))
    except Exception as e:
        assert False, f"fare_average crashed with: {e!r}"
    if result is not None:
        assert math.isfinite(result), f"average is not finite: {result}"
        assert result >= 0, f"average fare is negative: {result}"


@given(st.lists(st.integers(min_value=0, max_value=10_000), min_size=1, max_size=8))
def test_fare_average_is_correct(fares):
    result = fare_average(",".join(map(str, fares)))
    expected = sum(fares) / len(fares)
    assert result is not None
    assert math.isclose(result, expected, abs_tol=0.01), (
        f"average of {fares} should be {expected:.2f}, got {result}"
    )


# -------------------------------------------------------------- payable_fare

@given(st.text() | st.none())
def test_payable_fare_no_crash(s):
    try:
        payable_fare(s)
    except Exception as e:
        assert False, f"payable_fare crashed with: {e!r}"


@given(number_text, number_text)
def test_payable_fare_valid_result(fare, promo):
    try:
        result = payable_fare(f"{fare}|{promo}")
    except Exception as e:
        assert False, f"payable_fare crashed with: {e!r}"
    if result is not None:
        assert math.isfinite(result), f"payable fare is not finite: {result}"
        assert result >= 0, f"payable fare is negative: {result}"


@given(
    st.floats(min_value=0, max_value=100_000, allow_nan=False),
    st.floats(min_value=-100_000, max_value=100_000, allow_nan=False),
)
def test_payable_fare_promo_never_increases_fare(fare, promo):
    with_promo = payable_fare(f"{fare}|{promo}")
    without_promo = payable_fare(f"{fare}|0")
    assert without_promo is not None
    # A rejected promo (None) is fine; an accepted one must not raise the fare.
    if with_promo is not None:
        assert with_promo <= without_promo, (
            f"promo {promo} raised the fare from {without_promo} to {with_promo}"
        )
