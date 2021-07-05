import json
import io

from flask import Flask, request, send_file
import pyproj
from pyproj.exceptions import CRSError

from heatmap import Heatmap

app = Flask(__name__, static_url_path="")

with open("earthquakes.geojson") as f:
    data = json.load(f)


@app.route("/")
def root():
    return app.send_static_file("index.html")


@app.route("/wms", methods=["GET"])
def wms():
    width = int(request.args.get("width", default=400, type=int))
    height = int(request.args.get("height", default=300, type=int))
    bbox = request.args.get("bbox", default="13.25638,52.43927,13.53790,52.58177")
    # layers = request.args.get("layers")
    srs = request.args.get("srs", default="EPSG:4326")

    west, south, east, north = (float(q) for q in bbox.split(","))

    try:
        proj = pyproj.Proj(srs)
    except CRSError as err:
        return f"Provided projection {srs} invalid. Error: {str(err)}", 400

    heatmap = Heatmap(width, height, west, south, east, north)

    for feature in data["features"]:
        lonlat = feature["geometry"]["coordinates"][:2]
        magnitude = feature["properties"]["mag"]
        if srs != "EPSG:4326":
            lonlat = proj(*lonlat, errcheck=True)
        heatmap.add_point(*lonlat, val=magnitude)

    heatmap.update_pixel_grid_rgba()
    image_bytes = heatmap.get_heatmap_image_bytes()
    return send_file(io.BytesIO(image_bytes), mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
