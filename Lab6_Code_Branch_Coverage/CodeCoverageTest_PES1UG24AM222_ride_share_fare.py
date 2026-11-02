"""Code (line) coverage tests for ride_share_fare.py.

Goal: execute every line of the module at least once.
"""
import pytest
from ride_share_fare import extra_distance_fare, seats_and_bags_ok, pickup_status


# ---------- extra_distance_fare ----------

def test_within_included_distance():
    # sedan includes 8 km, 5 km travelled -> no extra fare
    assert extra_distance_fare("sedan", 5, "city", False) == 0


def test_unknown_cab_type_raises():
    with pytest.raises(ValueError, match="unknown cab type"):
        extra_distance_fare("bike", 10, "city", False)


def test_negative_distance_raises():
    with pytest.raises(ValueError, match="invalid distance"):
        extra_distance_fare("mini", -1, "city", False)


def test_subscriber_mini_city_short_trip():
    # mini includes 5 + 3 (subscriber) = 8 km; 10 km -> 2 extra km at 12/km
    assert extra_distance_fare("mini", 10, "city", True) == 24


def test_outstation_long_trip():
    # suv includes 12 km; 40 km -> 28 extra km (> 20)
    # rate = 18 (non-city) + 8 (long trip) + 4 (outstation) = 30
    assert extra_distance_fare("suv", 40, "outstation", False) == 28 * 30


# ---------- seats_and_bags_ok ----------

def test_seats_and_bags_ok():
    assert seats_and_bags_ok(2, 1, False) is True


def test_wheelchair_with_two_passengers():
    assert seats_and_bags_ok(2, 5, True) is True


def test_too_many_passengers():
    assert seats_and_bags_ok(5, 0, False) is False


# ---------- pickup_status ----------

def test_scheduled_airport_on_time():
    # cutoff = 10 (scheduled) + 10 (airport) = 20
    assert pickup_status(20, True, True) == "on_time"


def test_unscheduled_delayed():
    # cutoff = 5; 0 >= 5 - 15 -> delayed
    assert pickup_status(0, False, False) == "delayed"


def test_unscheduled_missed():
    # cutoff = 5; -20 < 5 - 15 -> missed
    assert pickup_status(-20, False, False) == "missed"
