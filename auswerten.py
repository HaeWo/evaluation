import math
import glob
import json
import matplotlib.pyplot as plt
import matplotlib.markers as marker
import numpy as np

# Map Plotting
import folium
from folium.plugins import MarkerCluster


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

def posdataToPopUp(coord, accuracy, distance):
    lat, lon = coord
    return """
    {}
    {}
    {}
    {}m
    """.format(accuracy, lat, lon, round(distance, 2))

routePoints = {
    # Bochum Citypoint
    1: [
        (51.48219, 7.21652),
        (51.4822, 7.21686),
        (51.4821, 7.21719),
        (51.48174, 7.2173),
        (51.48136, 7.21724),
        (51.48073, 7.21715),
        (51.4804, 7.21711),
        (51.48019, 7.21651),
    ],
    # Bochum HBF
    2: [
        (51.47938, 7.22209),
        (51.47923, 7.22229),
        (51.47912, 7.22252),
        (51.47888, 7.22279),
        (51.47845, 7.22331),
        (51.47807, 7.22376),
        (51.47789, 7.22352),
        (51.4777, 7.22276),
        (51.47807, 7.22227),
        (51.47837, 7.22193),
    ],
    # Bochum Querenburg
    3: [
        (51.46154, 7.27469),
        (51.46179, 7.27643),
        (51.46106, 7.27863),
        (51.46011, 7.28052),
        (51.45937, 7.28211),
        (51.45936, 7.2836),
    ],
    # Mülheim an der Ruhr
    4: [
        (51.42779, 6.88152),
        (51.42844, 6.88298),
        (51.42894, 6.88485),
        (51.42953, 6.88671),
        (51.43044, 6.88661),
        (51.43176, 6.88676),
        (51.43183, 6.8886),
        (51.43321, 6.88873),
    ]
}

data = {
    "high": [],
    "balanced": [],
    "gps": [],
    "gps_high": [],
}

colors = {
    "high": "#EF3E36", # Red
    "balanced": "#17BEBB", # Blue
    "gps": "#EDB88B", # Beige
    "gps_high": "#32a852", # Grün
}

m = folium.Map(
    location=[51.48219, 7.21652],
    zoom_start=19,
    tiles="CartoDB positron"
)

for route in [1,2,3,4]:
    folium.PolyLine(routePoints[route], color="#2E282A").add_to(m)
    for point in routePoints[route]:
        folium.CircleMarker(
            location=point,
            radius=4,
            color="black",
        ).add_to(m)

    for accuracy in data.keys():
        files = glob.glob("route{}/{}/*.json".format(route, accuracy))
        for file in files:
            with open(file, "r") as f:
                decJson = json.loads(f.read())
                onlyPlot=False
                if len(decJson) != len(routePoints[route]):
                    print(file, "missmatch point length", len(decJson), len(routePoints[route]))
                    onlyPlot=True
                count = -1
                if isinstance(decJson, dict):
                    for key in decJson.keys():
                        count = count + 1
                        v = decJson[key]
                        latLng = (v["lat"], v["lng"])

                        if not onlyPlot:
                            posOrig = routePoints[route][count]
                            distance = haversine(posOrig, latLng)

                            data[accuracy].append(distance)
                        else:
                            distance = 0

                        folium.CircleMarker(
                            location=latLng,
                            radius=8,
                            color=colors[accuracy],
                            fill=True,
                            fill_color=colors[accuracy],
                            popup=posdataToPopUp(latLng, accuracy, distance),
                        ).add_to(m)

                elif isinstance(decJson, list):
                    for v in decJson:
                        count = count + 1
                        latLng = (v["Latitude"], v["Longitude"])

                        if not onlyPlot:
                            posOrig = routePoints[route][count]
                            distance = haversine(posOrig, latLng)
                            data[accuracy].append(distance)
                        else:
                            distance=0

                        folium.CircleMarker(
                            location=latLng,
                            radius=8,
                            popup=posdataToPopUp(latLng, accuracy, distance),
                            color=colors[accuracy],
                            fill=True,
                            fill_color=colors[accuracy]
                        ).add_to(m)


fig = plt.figure()
ax1 = fig.add_subplot()
for accuracy in data.keys():
    xData = data[accuracy]
    if len(xData) == 0:
        continue
    xDataSorted = np.sort(xData)

    # calculate the proportional values of samples
    p = 1. * np.arange(len(xData)) / (len(xData) - 1)

    line, = ax1.plot(xDataSorted, p, colors[accuracy], marker=marker.CARETDOWNBASE)
    line.set_label(accuracy)

    xvalues = line.get_xdata()
    yvalues = line.get_ydata()
    val50 = np.interp(0.5, yvalues, xvalues)
    val95 = np.interp(0.95, yvalues, xvalues)
    print(accuracy, "0.5", val50, "0.95", val95)

ax1.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
plt.xticks((0, 10, 20, 50, 70, 100, 150, 200, 250))
plt.yticks((0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0))
plt.xlim(left=0, right=300)
ax1.set_xlabel('Error distance ($meters$)')
ax1.legend()
ax1.set_ylabel('$p$')
fig.savefig("docs/graph.png", bbox_inches='tight')

m.save("docs/map.html")
