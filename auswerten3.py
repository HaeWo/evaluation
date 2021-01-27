import glob
import json
import os

import matplotlib.pyplot as plt

import folium
from folium.plugins import MarkerCluster

m = folium.Map(
    location=[51.44708882, 7.27355495],
    zoom_start=19,
    tiles="CartoDB positron"
)

def posdataToPopUp(coord, accuracy, gpsFixes):
    lat, lon = coord
    return """
    Accuracy: {}m
    [lat: {}, lng: {}]
    GPS-Fix: {}
    """.format(accuracy, lat, lon, gpsFixes)

colors = {
    "DISTANCE": "#EF3E36", # Red
    "PERIODIC": "#17BEBB", # Blue
    "SLEEP_AWARE": "#EDB88B", # Beige
    "SLEEP_AWARE_MOTION": "#8A6642", # Grün
    "SPEED": "#32a852", # Grün
}


fig = plt.figure()
ax1 = fig.add_subplot()
for route in colors.keys():
    files = glob.glob("prakt3/{}/*.json".format(route))
    group = folium.FeatureGroup(route)
    lastGPSFixes = None
    startTimeStamp = None
    xData = []
    yData = []
    for file in files:
        baseName = os.path.basename(file)
        fileTime = int(os.path.splitext(baseName)[0])

        if startTimeStamp is None:
            startTimeStamp = fileTime
            xData.append(0)
        else:
            xData.append(fileTime - startTimeStamp)
        
        with open(file, "r") as f:
            decJson = json.loads(f.read())
            latLng = (decJson["lat"], decJson["lng"])
            if lastGPSFixes is None:
                fixDiff = decJson["gpsfix"]
            else:
                fixDiff = decJson["gpsfix"] - lastGPSFixes
            yData.append(decJson["gpsfix"])
            folium.CircleMarker(
                location=latLng,
                radius=4,
                color=colors[route],
                fill=True,
                fill_color=colors[route],
                popup=posdataToPopUp(latLng, decJson["accuracy"], fixDiff),
            ).add_to(group)
            lastGPSFixes = decJson["gpsfix"]
    line, = ax1.plot(xData, yData, colors[route])
    line.set_label(route)
    m.add_child(group)


ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
ax1.set_xlabel('Zeit ($sekunden$)')
ax1.legend()
ax1.set_ylabel('$GPS-Fixes$')
fig.savefig("docs/prakt3_graph.png", bbox_inches='tight')

folium.LatLngPopup().add_to(m)
m.add_child(folium.map.LayerControl())
m.save("docs/map3.html")