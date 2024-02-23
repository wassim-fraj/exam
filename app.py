from flask import Flask, request, render_template, Response
import requests
import time
from prometheus_client import Counter, Histogram
from prometheus_client.exposition import generate_latest

app = Flask(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'request_count', 'App Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency',
                            ['method', 'endpoint'])


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():
    start_time = time.time()

    # Increment the request count metric
    REQUEST_COUNT.labels(request.method, '/search', '200').inc()

    query = request.form["q"]
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {"q": query, "format": "json", "limit": "1"},
    ).json()

    if location:
        coordinate = [location[0]["lat"], location[0]["lon"]]
        time = requests.get(
            "https://timeapi.io/api/Time/current/coordinate",
            {"latitude": coordinate[0], "longitude": coordinate[1]},
        )
        latency = time.time() - start_time
        # Record the request latency
        REQUEST_LATENCY.labels(request.method, '/search').observe(latency)

        return render_template("success.html", location=location[0], time=time.json())
    else:
        return render_template("fail.html")


# Endpoint to expose Prometheus metrics
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype="text/plain")


if __name__ == '__main__':
    app.run(debug=True)
