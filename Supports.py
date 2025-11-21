import re
from urllib.parse import urlparse, parse_qs, unquote
import pydeck as pdk
import pandas as pd
import requests


def extract_coordinates_and_address(url: str):

    # Normalize
    url = unquote(url)
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    lat = lon = None
    address = None

    # ---------------------------------------------------------
    # 1) GOOGLE MAPS: /place/<address>/....
    # e.g. https://www.google.com/maps/place/Empire+State+Building/@40.7,-74.0
    # ---------------------------------------------------------
    m = re.search(r'/maps/place/([^/]+)', url)
    if m:
        address = m.group(1).replace("+", " ")

    # ---------------------------------------------------------
    # 2) GOOGLE MAPS: q=<query or address>
    # e.g. .../maps?q=coffee+shop+near+me
    # ---------------------------------------------------------
    if "q" in qs and not address:
        address = qs["q"][0].replace("+", " ")

    # ---------------------------------------------------------
    # 3) GOOGLE MAPS: coordinates via @lat,lon
    # ---------------------------------------------------------
    m = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if m:
        lat = float(m.group(1))
        lon = float(m.group(2))

    # ---------------------------------------------------------
    # 4) GOOGLE MAPS: /search/<address>
    # e.g. /maps/search/Starbucks/
    # ---------------------------------------------------------
    m = re.search(r'/maps/search/([^/]+)', url)
    if m and not address:
        address = m.group(1).replace("+", " ")

    # ---------------------------------------------------------
    # 5) APPLE MAPS: address via q= or address=
    # ---------------------------------------------------------
    if "address" in qs and not address:
        address = qs["address"][0]
    if "q" in qs and not address:    # sometimes contains address
        address = qs["q"][0]

    # ---------------------------------------------------------
    # 6) APPLE MAPS: coordinates via ll=lat,lon
    # ---------------------------------------------------------
    if "ll" in qs:
        try:
            lat_str, lon_str = qs["ll"][0].split(",")
            lat, lon = float(lat_str), float(lon_str)
        except:
            pass

    # ---------------------------------------------------------
    # 7) OPENSTREETMAP: #map=zoom/lat/lon
    # ---------------------------------------------------------
    m = re.search(r'#map=\d+/(-?\d+\.\d+)/(-?\d+\.\d+)', url)
    if m:
        lat = float(m.group(1))
        lon = float(m.group(2))

    # ---------------------------------------------------------
    # 8) GENERIC fallback: first lat/lon pair
    # ---------------------------------------------------------
    if lat is None or lon is None:
        m = re.search(r'(-?\d+\.\d+)[,/](-?\d+\.\d+)', url)
        if m:
            lat = float(m.group(1))
            lon = float(m.group(2))

    # ---------------------------------------------------------
    # 9) If address was encoded like .../place/Some%20Place/
    # ---------------------------------------------------------
    if address:
        address = address.replace("%20", " ")

    return lat, lon, address

def create_detailed_map(lat, lon, zoom=11):
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame({"lat": [lat], "lon": [lon]}),
        get_position='[lon, lat]',
        get_color='[200, 30, 0, 160]',
        get_radius=200,
    )

    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=zoom,
        pitch=0,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )

    return r

def image_to_pdf(image,pdf):
    img_path = "map.png"


    # Save PIL image from screenshot component
    image.save(img_path)
    pdf.image(img_path, x=10, y=10, w=180)


def get_static_map(lat, lon):
    url = (
        "https://static-maps.yandex.ru/1.x/?"
        f"ll={lon},{lat}&z=14&size=650,450&l=map&pt={lon},{lat},pm2rdm&lang=en_US"
    )
    img_path = "map.png"
    with open(img_path, "wb") as f:
        f.write(requests.get(url).content)
    return img_path