from flask import Flask, request, render_template
import requests

app = Flask(__name__)


@app.route("/")
def home():

    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():

    # Get the search query
    query = request.form["q"]

    # Pass the search query to the Nominatim API to get a location
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    # If a location is found, pass the coordinate to the Time API to get the current time
    if location:
        coordinate = [location[0]["lat"], location[0]["lon"]]

        time = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )

        return render_template("success.html", location=location[0], time=time.json())

    # If a location is NOT found, return the error page
    else:

        return render_template("fail.html")
