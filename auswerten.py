import math
import glob
import json
import matplotlib.pyplot as plt
import matplotlib.markers as marker
import numpy as np

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

routePoints = {
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
    ]
}

data = {
    "high": [],
    "balanced": [],
    "gps": [],
}

colors = {
    "high": "r",
    "balanced": "b",
    "gps": "g",
}

for route in [1, 2]:
    for accuracy in ["high", "balanced", "gps"]:
        files = glob.glob("route{}/{}/*.json".format(route, accuracy))
        for file in files:
            with open(file, "r") as f:
                decJson = json.loads(f.read())
                if len(decJson) != len(routePoints[route]):
                    print(file, "missmatch point length")
                    continue
                count = -1
                for key in decJson.keys():
                    count = count + 1
                    v = decJson[key]
                    latLng = (v["lat"], v["lng"])

                    posOrig = routePoints[route][count]
                    distance = haversine(posOrig, latLng)

                    data[accuracy].append(distance)


fig = plt.figure()
ax1 = fig.add_subplot()
for accuracy in ["high", "balanced", "gps"]:
    xData = data[accuracy]
    xDataSorted = np.sort(xData)

    # calculate the proportional values of samples
    p = 1. * np.arange(len(xData)) / (len(xData) - 1)

    ax1.plot(xDataSorted, p, colors[accuracy], marker=marker.CARETDOWNBASE)


ax1.set_xlabel('Error distance ($meters$)')
ax1.set_ylabel('$p$')
fig.savefig("graph.png")