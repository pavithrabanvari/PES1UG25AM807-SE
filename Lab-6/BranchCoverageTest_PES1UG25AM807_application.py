import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# ---------------- BILL TOTAL BRANCH TESTS ----------------

def test_valid_dine_in():
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_invalid_section():
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("invalid", 1000, 2, False)


def test_negative_food_total():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -100, 2, False)


def test_zero_guests():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", 1000, 0, False)


def test_happy_hour_discount_applied():
    assert bill_total("dine_in", 1000, 2, True) == 924


def test_happy_hour_not_applied():
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_happy_hour_takeaway():
    assert bill_total("takeaway", 1000, 2, True) == 1050


def test_large_party_service_charge():
    assert bill_total("dine_in", 1000, 8, False) == 1365


def test_small_party_no_extra_charge():
    assert bill_total("dine_in", 1000, 7, False) == 1155


# ---------------- SPLIT BILL BRANCH TESTS ----------------

def test_invalid_people():
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_negative_tip():
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 2, -5)


def test_split_exactly():
    assert split_bill(100, 2, 0) == 50


def test_split_with_remainder():
    assert split_bill(100, 3, 0) == 34


# ---------------- TABLE WAIT BRANCH TESTS ----------------

def test_party_over_12():
    assert table_wait(13, 5, False) == "call ahead"


def test_party_not_over_12_with_reservation():
    assert table_wait(4, 0, True) == "seat now"


def test_no_reservation_and_no_free_tables():
    assert table_wait(4, 0, False) == "waitlist"


def test_large_party_with_one_free_table():
    assert table_wait(8, 1, False) == "waitlist"


def test_large_party_with_two_free_tables():
    assert table_wait(8, 2, False) == "seat now"


def test_small_party_with_free_table():
    assert table_wait(4, 1, False) == "seat now"