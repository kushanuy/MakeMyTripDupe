# test_tripeasy.py - test cases TC01 to TC28.   Run with:  python3 -m pytest -v

import booking
from app import app

DATE = "2099-01-01"      # a date far in the future, so it is never "in the past"


def start():
    """Every test starts with fresh flights and no bookings."""
    booking.reset_data()


def book_one(flight_id="6E101", name="Test Passenger", email="kushanuy@gmail.com"):
    """Helper: make one valid booking."""
    return booking.make_booking(flight_id, DATE, "Economy", name, "25", "Male", "9876543210", email)


# ---------------- Search (TC01 - TC05) ----------------

def test_tc01_search_valid_route_gives_flights():
    start()
    found, error = booking.find_flights("Bengaluru", "Delhi", DATE)
    assert error == ""
    assert len(found) == 3


def test_tc02_same_city_gives_error():
    start()
    found, error = booking.find_flights("Delhi", "Delhi", DATE)
    assert error == "From and To cities cannot be the same."


def test_tc03_past_date_gives_error():
    start()
    found, error = booking.find_flights("Delhi", "Mumbai", "2000-01-01")
    assert error == "Travel date cannot be in the past."


def test_tc04_empty_date_gives_error():
    start()
    found, error = booking.find_flights("Delhi", "Mumbai", "")
    assert error == "Please choose a travel date."


def test_tc05_business_costs_double_economy():
    start()
    flight = booking.get_flight("6E101")
    assert booking.get_price(flight, "Economy") == 4500
    assert booking.get_price(flight, "Business") == 9000


# ---------------- Booking (TC06 - TC12) ----------------

def test_tc06_valid_booking_is_confirmed():
    start()
    b, error = book_one()
    assert error == ""
    assert b.status == "Confirmed"
    assert b.pnr == "TE1001"
    assert b.fare == 4500


def test_tc07_booking_reduces_seats_by_one():
    start()
    book_one()
    assert booking.get_flight("6E101").seats == 9


def test_tc08_sold_out_flight_cannot_be_booked():
    start()
    for i in range(10):
        book_one()
    assert booking.get_flight("6E101").seats == 0
    b, error = book_one()
    assert b is None
    assert error == "Sorry, this flight is sold out."


def test_tc09_empty_name_gives_error():
    start()
    b, error = book_one(name="")
    assert error == "Please enter a valid name (letters only)."


def test_tc10_name_with_numbers_or_symbols_gives_error():
    start()
    for bad_name in ["R2D2", "<script>", "A1"]:
        b, error = book_one(name=bad_name)
        assert error == "Please enter a valid name (letters only)."


def test_tc11_bad_age_gives_error():
    start()
    for bad_age in ["abc", "0", "150", ""]:
        b, error = booking.make_booking("6E101", DATE, "Economy", "Asha Rao", bad_age, "Female", "9876543210", "a@b.com")
        assert error == "Age must be a number between 1 and 120."


def test_tc12_bad_phone_gives_error():
    start()
    for bad_phone in ["12345", "98765abcde", "", "98765432101"]:
        b, error = booking.make_booking("6E101", DATE, "Economy", "Asha Rao", "30", "Female", bad_phone, "a@b.com")
        assert error == "Phone number must be exactly 10 digits."


# ---------------- Cancellation (TC13 - TC16) ----------------

def test_tc13_cancel_gives_90_percent_refund():
    start()
    b, error = book_one()
    error = booking.cancel_booking("TE1001", "kushanuy@gmail.com")
    assert error == ""
    assert b.status == "Cancelled"
    assert b.refund == 4050


def test_tc14_cancel_gives_the_seat_back():
    start()
    book_one()
    booking.cancel_booking("TE1001", "kushanuy@gmail.com")
    assert booking.get_flight("6E101").seats == 10


def test_tc15_cancel_twice_gives_error():
    start()
    book_one()
    booking.cancel_booking("TE1001", "kushanuy@gmail.com")
    error = booking.cancel_booking("TE1001", "kushanuy@gmail.com")
    assert error == "This booking is already cancelled."


def test_tc16_cannot_cancel_someone_elses_booking():
    start()
    book_one()
    error = booking.cancel_booking("TE1001", "other@example.com")
    assert error == "Booking not found."


# ---------------- Login (TC17 - TC20) ----------------

def test_tc17_correct_login_works():
    assert booking.check_login("kushanuy@gmail.com", "abcd12345") == ""


def test_tc18_wrong_password_gives_error():
    assert booking.check_login("kushanuy@gmail.com", "wrong") == "Incorrect password."


def test_tc19_unknown_email_gives_error():
    assert booking.check_login("random@example.com", "abcd12345") == "No account found for this email."


def test_tc20_empty_login_gives_error():
    assert booking.check_login("", "") == "Please enter your email and password."


# ---------------- Website pages (TC21 - TC28) ----------------

BOOK_URL = "/book/6E101?date=2099-01-01&cabin=Economy"


def login(client):
    """Helper: log in from the booking page, like a real user."""
    return client.post("/login", follow_redirects=True, data={
        "email": "kushanuy@gmail.com", "password": "abcd12345",
        "flight_id": "6E101", "date": DATE, "cabin": "Economy"})


def test_tc21_home_page_loads():
    start()
    page = app.test_client().get("/")
    assert page.status_code == 200
    assert b"SEARCH" in page.data


def test_tc22_booking_page_needs_login():
    start()
    page = app.test_client().get(BOOK_URL)
    assert page.status_code == 302
    assert "/login" in page.headers["Location"]


def test_tc23_login_returns_to_booking_with_saved_details():
    start()
    page = login(app.test_client())
    assert b"Passenger details" in page.data
    assert b"Kushanu Y" in page.data
    assert b"9876543210" in page.data
    assert b"kushanuy@gmail.com" in page.data


def test_tc24_wrong_password_shows_error_on_page():
    start()
    page = app.test_client().post("/login", data={"email": "kushanuy@gmail.com", "password": "nope"})
    assert b"Incorrect password." in page.data


def test_tc25_unknown_email_shows_no_account_message():
    start()
    page = app.test_client().post("/login", data={"email": "random@example.com", "password": "abcd12345"})
    assert b"No account found for this email." in page.data


def test_tc26_full_booking_on_website():
    start()
    client = app.test_client()
    login(client)
    page = client.post(BOOK_URL, data={"name": "Kushanu Y", "age": "20", "gender": "Male", "phone": "9876543210"})
    assert b"Booking Confirmed" in page.data
    assert b"TE1001" in page.data


def test_tc27_my_trips_shows_booking_and_cancel_works():
    start()
    client = app.test_client()
    login(client)
    client.post(BOOK_URL, data={"name": "Kushanu Y", "age": "20", "gender": "Male", "phone": "9876543210"})
    trips = client.get("/trips")
    assert b"TE1001" in trips.data and b"Confirmed" in trips.data
    cancelled = client.post("/cancel/TE1001")
    assert b"Cancelled" in cancelled.data and b"Refund" in cancelled.data


def test_tc28_logout_then_my_trips_needs_login():
    start()
    client = app.test_client()
    login(client)
    client.get("/logout")
    page = client.get("/trips")
    assert page.status_code == 302
    assert "/login" in page.headers["Location"]
