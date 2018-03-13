import os

import requests


# Tibia maps provided by TibiaMaps.io

def save_maps(con):
    url = "https://tibiamaps.github.io/tibia-map-data/floor-{0:02d}-map.png"
    os.makedirs(f"images/map", exist_ok=True)
    c = con.cursor()
    for z in range(16):
        try:
            if os.path.exists(f"images/map/{z}.png"):
                with open(f"images/map/{z}.png", "rb") as f:
                    image = f.read()
            else:
                r = requests.get(url.format(z))
                r.raise_for_status()
                image = r.content
                with open(f"images/map/{z}.png", "wb") as f:
                    f.write(image)
            c.execute(f"INSERT INTO map(z, image) VALUES(?,?)", (z, image))
            con.commit()
        except requests.HTTPError:
            print(f"Couldn't fetch image for z = {z}")
    con.commit()
    c.close()
