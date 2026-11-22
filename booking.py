# booking.py - the logic of the flight booking system (no website code here)

import datetime

CITIES = ["Bengaluru", "Delhi", "Mumbai", "Chennai"]

# The only account that can log in (hard-coded for this project)
USERS = {
    "kushanuy@gmail.com": {
        "password": "abcd12345",
        "name": "Kushanu Y",
        "age": "20",
        "gender": "Male",
        "phone": "9876543210",
    }
}


class Flight:
    def __init__(self, flight_id, airline, origin, destination, time, price, seats):
        self.flight_id = flight_id
        self.airline = airline
        self.origin = origin
        self.destination = destination
        self.time = time
        self.price = price      # Economy price
        self.seats = seats      # seats still available


class Booking:
    def __init__(self, pnr, flight, travel_date, cabin, name, age, gender, phone, email, fare):
        self.pnr = pnr
        self.flight = flight
        self.travel_date = travel_date
        self.cabin = cabin
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.email = email
        self.fare = fare
        self.status = "Confirmed"
        self.refund = 0


def make_flights():
    return [
        Flight("6E101", "IndiGo", "Bengaluru", "Delhi", "06:15", 4500, 10),
        Flight("AI202", "Air India", "Bengaluru", "Delhi", "10:30", 5200, 10),
        Flight("UK303", "Vistara", "Bengaluru", "Delhi", "18:45", 5800, 10),
        Flight("6E104", "IndiGo", "Delhi", "Bengaluru", "07:00", 4600, 10),
        Flight("AI205", "Air India", "Delhi", "Bengaluru", "15:20", 5300, 10),
        Flight("6E106", "IndiGo", "Bengaluru", "Mumbai", "08:10", 3200, 10),
        Flight("UK307", "Vistara", "Bengaluru", "Mumbai", "19:00", 3900, 10),
        Flight("AI208", "Air India", "Mumbai", "Bengaluru", "09:30", 3300, 10),
        Flight("6E109", "IndiGo", "Delhi", "Mumbai", "11:00", 4100, 10),
        Flight("AI210", "Air India", "Mumbai", "Delhi", "16:40", 4300, 10),
        Flight("6E111", "IndiGo", "Chennai", "Bengaluru", "07:45", 2500, 10),
        Flight("6E112", "IndiGo", "Bengaluru", "Chennai", "20:00", 2600, 10),
    ]


flights = make_flights()    # all flights
bookings = []               # all bookings made so far (lost when the program stops)


def reset_data():
    """Put everything back to the start (used by the tests)."""
    flights.clear()
    flights.extend(make_flights())
    bookings.clear()


def get_flight(flight_id):
    for f in flights:
        if f.flight_id == flight_id:
            return f
    return None


def get_price(flight, cabin):
    if cabin == "Business":
        return flight.price * 2
    return flight.price


def check_login(email, password):
    """Returns an error message, or "" if the login is correct."""
    email = email.strip().lower()
    if email == "" or password == "":
        return "Please enter your email and password."
    if email not in USERS:
        return "No account found for this email."
    if USERS[email]["password"] != password:
        return "Incorrect password."
    return ""


def find_flights(origin, destination, travel_date):
    """Returns (list of flights, error message)."""
    if origin == destination:
        return [], "From and To cities cannot be the same."
    if travel_date == "":
        return [], "Please choose a travel date."
    if travel_date < datetime.date.today().isoformat():
        return [], "Travel date cannot be in the past."
    found = []
    for f in flights:
        if f.origin == origin and f.destination == destination:
            found.append(f)
    return found, ""


def make_booking(flight_id, travel_date, cabin, name, age, gender, phone, email):
    """Returns (booking, error message). If there is an error, booking is None."""
    flight = get_flight(flight_id)
    if flight is None:
        return None, "Flight not found."
    if flight.seats == 0:
        return None, "Sorry, this flight is sold out."
    name = name.strip()
    if name == "" or not name.replace(" ", "").isalpha():
        return None, "Please enter a valid name (letters only)."
    if not age.isdigit() or int(age) < 1 or int(age) > 120:
        return None, "Age must be a number between 1 and 120."
    if gender == "":
        return None, "Please choose a gender."
    if not phone.isdigit() or len(phone) != 10:
        return None, "Phone number must be exactly 10 digits."

    flight.seats = flight.seats - 1
    pnr = "TE" + str(1001 + len(bookings))
    fare = get_price(flight, cabin)
    booking = Booking(pnr, flight, travel_date, cabin, name, age, gender, phone, email, fare)
    bookings.append(booking)
    return booking, ""


def user_bookings(email):
    mine = []
    for b in bookings:
        if b.email == email:
            mine.append(b)
    return mine


def cancel_booking(pnr, email):
    """Returns an error message, or "" if the cancellation worked. Refund is 90%."""
    for b in bookings:
        if b.pnr == pnr and b.email == email:
            if b.status == "Cancelled":
                return "This booking is already cancelled."
            b.status = "Cancelled"
            b.refund = b.fare * 90 // 100
            b.flight.seats = b.flight.seats + 1
            return ""
    return "Booking not found."
