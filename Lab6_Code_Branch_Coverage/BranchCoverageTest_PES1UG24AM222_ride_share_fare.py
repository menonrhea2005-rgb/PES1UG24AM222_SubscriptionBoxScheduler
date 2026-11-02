"""Branch coverage tests for ride_share_fare.py.

Goal: make every decision (if / elif / else) evaluate both True and False,
including boundary values.
"""
import pytest
from ride_share_fare import extra_distance_fare, seats_and_bags_ok, pickup_status


# ---------- extra_distance_fare ----------

@pytest.mark.parametrize("cab_type", ["bike", "", "SEDAN"])
def test_unknown_cab_type_raises(cab_type):
    # line 5: cab_type not in INCLUDED_KM -> True
    with pytest.raises(ValueError, match="unknown cab type"):
        extra_distance_fare(cab_type, 10, "city", False)


def test_negative_distance_raises():
    # line 7: distance_km < 0 -> True
    with pytest.raises(ValueError, match="invalid distance"):
        extra_distance_fare("mini", -1, "city", False)


def test_zero_distance_is_free():
    # line 7 False at the boundary (0 is valid), line 13 True
    assert extra_distance_fare("mini", 0, "city", False) == 0


def test_exactly_included_distance_is_free():
    # line 13: extra == 0 -> True (boundary of extra <= 0)
    assert extra_distance_fare("sedan", 8, "city", False) == 0


def test_one_km_over_included():
    # line 13: extra == 1 -> False
    assert extra_distance_fare("sedan", 9, "city", False) == 12


def test_subscriber_gets_three_extra_km():
    # line 10: subscriber and not suv -> True (8 + 3 = 11 km included)
    assert extra_distance_fare("sedan", 11, "city", True) == 0
    assert extra_distance_fare("sedan", 12, "city", True) == 12


def test_subscriber_suv_gets_no_bonus():
    # line 10: subscriber but suv -> False (still 12 km included)
    assert extra_distance_fare("suv", 13, "city", True) == 12


def test_non_subscriber_gets_no_bonus():
    # line 10: not subscriber -> False
    assert extra_distance_fare("mini", 6, "city", False) == 12


def test_city_rate():
    # line 15 True -> rate 12; line 19 False
    assert extra_distance_fare("mini", 15, "city", False) == 10 * 12


def test_non_city_rate():
    # line 15 False -> rate 18; line 19 False
    assert extra_distance_fare("mini", 15, "suburb", False) == 10 * 18


def test_extra_exactly_20_has_no_long_trip_surcharge():
    # line 19: extra == 20 -> False (boundary)
    assert extra_distance_fare("mini", 25, "city", False) == 20 * 12


def test_long_city_trip():
    # line 19 True, line 21 False (city): rate = 12 + 8 = 20
    assert extra_distance_fare("mini", 26, "city", False) == 21 * 20


def test_long_non_city_non_outstation_trip():
    # line 19 True, line 21 False (suburb): rate = 18 + 8 = 26
    assert extra_distance_fare("mini", 30, "suburb", False) == 25 * 26


def test_long_outstation_trip():
    # line 19 True, line 21 True: rate = 18 + 8 + 4 = 30
    assert extra_distance_fare("suv", 40, "outstation", False) == 28 * 30


# ---------- seats_and_bags_ok ----------

@pytest.mark.parametrize("passengers, expected", [(2, True), (3, False)])
def test_wheelchair_passenger_limit(passengers, expected):
    # line 27 True; line 28 both outcomes (boundary at 2)
    assert seats_and_bags_ok(passengers, 0, True) is expected


@pytest.mark.parametrize("passengers, expected", [(4, True), (5, False)])
def test_passenger_limit_without_wheelchair(passengers, expected):
    # line 27 False; line 29 both outcomes (boundary at 4)
    assert seats_and_bags_ok(passengers, 0, False) is expected


@pytest.mark.parametrize("bags, expected", [(2, True), (3, False)])
def test_bag_limit(bags, expected):
    # line 31 both outcomes (boundary at 2)
    assert seats_and_bags_ok(3, bags, False) is expected


# ---------- pickup_status ----------

@pytest.mark.parametrize(
    "is_scheduled, is_airport, cutoff",
    [(True, True, 20), (True, False, 10), (False, True, 15), (False, False, 5)],
)
def test_pickup_cutoffs(is_scheduled, is_airport, cutoff):
    # lines 35 and 39 both True and False; lines 41 and 43 both outcomes
    assert pickup_status(cutoff, is_scheduled, is_airport) == "on_time"
    assert pickup_status(cutoff - 1, is_scheduled, is_airport) == "delayed"
    assert pickup_status(cutoff - 15, is_scheduled, is_airport) == "delayed"
    assert pickup_status(cutoff - 16, is_scheduled, is_airport) == "missed"
