from flask import Flask, request, jsonify
import geopandas as gpd
from shapely.geometry import Point

app = Flask(__name__)

# ─── 1) Load & inspect ────────────────────────────────────────────────
gdf = gpd.read_file("property.geojson")
print("CRS:", gdf.crs)
print("Bounds:", gdf.total_bounds)

# ─── 2) Reproject into WGS84 if needed ───────────────────────────────
if gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)
    print("Reprojected bounds:", gdf.total_bounds)

# ─── 3) Your routes ──────────────────────────────────────────────────
@app.route('/')
def home():
    return "✔️ Zi AI is running. Use /check-zoning?lat=…&lon=…"

@app.route('/check-zoning')
def check_zoning():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    pt = Point(lon, lat)
    buf = pt.buffer(0.0001)
    match = gdf[gdf.intersects(buf)]
    if not match.empty:
        land_use = match.iloc[0]['LAND_USE']
        ok = 'residential' in str(land_use).lower()
        return jsonify({
            "result":  "✅ Yes, residential." if ok else "❌ No, not residential.",
            "land_use": land_use
        })
    return jsonify({"result": "No property found at this location."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
