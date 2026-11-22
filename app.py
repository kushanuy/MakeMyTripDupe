# app.py - the website. Run with:  python3 app.py   then open http://127.0.0.1:5000

import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import booking

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="/static")
app.secret_key = "school-project"     # needed so the site can remember who is logged in


@app.route("/")
def home():
    today = datetime.date.today().isoformat()
    return render_template("index.html", cities=booking.CITIES, today=today, error="")


@app.route("/search")
def search():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    travel_date = request.args.get("date")
    cabin = request.args.get("cabin")

    found, error = booking.find_flights(origin, destination, travel_date)
    if error != "":
        today = datetime.date.today().isoformat()
        return render_template("index.html", cities=booking.CITIES, today=today, error=error)
    return render_template("results.html", flights=found, origin=origin, destination=destination,
                           date=travel_date, cabin=cabin, get_price=booking.get_price)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    # These three remember which flight the user was trying to book
    flight_id = request.values.get("flight_id", "")
    travel_date = request.values.get("date", "")
    cabin = request.values.get("cabin", "")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        error = booking.check_login(email, password)
        if error == "":
            session["user"] = email.strip().lower()
            if flight_id != "":
                return redirect(url_for("book", flight_id=flight_id, date=travel_date, cabin=cabin))
            return redirect(url_for("home"))
    return render_template("login.html", error=error, flight_id=flight_id, date=travel_date, cabin=cabin)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/book/<flight_id>", methods=["GET", "POST"])
def book(flight_id):
    travel_date = request.values.get("date", "")
    cabin = request.values.get("cabin", "Economy")

    # Booking needs a login
    if "user" not in session:
        return redirect(url_for("login", flight_id=flight_id, date=travel_date, cabin=cabin))

    flight = booking.get_flight(flight_id)
    if flight is None:
        return redirect(url_for("home"))

    error = ""
    form = booking.USERS[session["user"]]    # the saved details fill the form boxes
    if request.method == "POST":
        form = request.form
        new_booking, error = booking.make_booking(flight_id, travel_date, cabin, form["name"],
                                                  form["age"], form["gender"], form["phone"],
                                                  session["user"])
        if error == "":
            return render_template("confirmation.html", b=new_booking)

    return render_template("book.html", flight=flight, date=travel_date, cabin=cabin,
                           price=booking.get_price(flight, cabin), form=form, error=error,
                           email=session["user"])


@app.route("/trips")
def trips():
    if "user" not in session:
        return redirect(url_for("login"))
    mine = booking.user_bookings(session["user"])
    return render_template("trips.html", trips=mine, message="")


@app.route("/cancel/<pnr>", methods=["POST"])
def cancel(pnr):
    if "user" not in session:
        return redirect(url_for("login"))
    error = booking.cancel_booking(pnr, session["user"])
    message = "Booking " + pnr + " cancelled. Refund will be processed." if error == "" else error
    mine = booking.user_bookings(session["user"])
    return render_template("trips.html", trips=mine, message=message)


if __name__ == "__main__":
    app.run(debug=True)
