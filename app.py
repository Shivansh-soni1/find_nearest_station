from flask import Flask, request, render_template
from geopy.geocoders import Nominatim
import csv
import math
import time

app = Flask(__name__)

# --------------------------------------------------
# Geocoder (ONE instance only – important)
# --------------------------------------------------
geolocator = Nominatim(user_agent="railway_station_finder")

def get_lat_lon(place_name):
    location = geolocator.geocode(place_name)
    time.sleep(1)  # avoid Nominatim rate limit
    if location:
        return location.latitude, location.longitude
    return None, None


# --------------------------------------------------
# Haversine distance formula
# --------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# --------------------------------------------------
# Load stations from CSV
# --------------------------------------------------
stations = []

with open("mp_additional_100_stations.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        stations.append({
            "code": row["code"],
            "name": row["name"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"])
        })


def find_nearest_station(lat, lon):
    nearest = None
    min_dist = float("inf")

    for s in stations:
        dist = haversine(lat, lon, s["lat"], s["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = {
                "code": s["code"],
                "name": s["name"],
                "distance_km": round(dist, 2)
            }

    return nearest


# --------------------------------------------------
# Home page
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# Result page (HTML only – NO JSON)
# --------------------------------------------------
@app.route("/from-to-stations")
def from_to_stations():
    from_place = request.args.get("from_place")
    to_place   = request.args.get("to_place")

    if not from_place or not to_place:
        return "Invalid input", 400

    from_lat, from_lon = get_lat_lon(from_place)
    to_lat, to_lon     = get_lat_lon(to_place)

    if not from_lat or not to_lat:
        return "Invalid place name", 400

    from_station = find_nearest_station(from_lat, from_lon)
    to_station   = find_nearest_station(to_lat, to_lon)

    return render_template(
        "result.html",
        from_station=from_station,
        to_station=to_station
    )


# --------------------------------------------------
# Run server
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
