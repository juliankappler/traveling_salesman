# Traveling salesman using real-world data

## Introduction

Here, we solve the traveling salesman problem on real-world data. 

The user provides a list of addresses/location names. Using the 
openrouteservice.org API, we resolve the given names to locations on the world
map. Subsequently, we use a genetic algorithm to determine the shortest round
trip such that the beginning and end location are identical, and each other l
ocation is visited exactly once.

## Example: Munich

We provide a short example on how to determine and visualize the shortest 
round trip. The following example is from [this notebook]().

```Python
from traveling_salesman import traveling_salesman

# To resolve names to locations on the world map, and to obtain the traveling 
# distances and routes between locations, we need to open a free account at
# openstreetservice.org and create an api key. Here we point to the text file
# that contains this api key:
parameters = {'api_key_filename':'api_key.txt'}

# Instantiate class
ts = traveling_salesman(parameters=parameters)

# Set locations
names = ['Lindwurmstr. 167 München',# salesman always starts at first location
         'Museumsinsel 1, 80538 München',
        'Sendlinger Tor München',
        'Pinakothek der Moderne, München',
        'Rotkreuzplatz München',
        'Muenchner Freiheit, München',
        'Münchner Stadtbibliothek Maxvorstadt',
        'Schellingstr. 4 Muenchen'
        ]
names_resolved, locations = ts.set_locations(names)
# To ensure that the provided names have been resolved correctly, one might
# want to compare names[i] with names_resolved[i]. The latter contains the
# name of the found location that will be used for the traveling salesman
# problem

# Solve the traveling salesman problem
results = ts.solve() # takes ~30s on my MacBook Pro
# by default, ts.solve() solves the traveling salesman problem three times
# and takes the best path of the three solutions
# Output here:
# Found shortest path:
# 1. Lindwurmstraße 167, Munich, BY, Germany
#     1.74 km
# 2. Sendlinger-Tor-Platz, Munich, BY, Germany
#     1.94 km
# 3. Museumsinsel 1, Munich, BY, Germany
#     2.85 km
# 4. Schellingstraße 4, Munich, BY, Germany
#     2.37 km
# 5. Muenchner Freiheit, Munich, BY, Germany
#     3.32 km
# 6. Pinakothek der Moderne, Munich, BY, Germany
#     0.84 km
# 7. Münchner Stadtbibliothek Maxvorstadt, Munich, BY, Germany
#     2.81 km
# 8. Rotkreuzplatz, Munich, BY, Germany
#     4.93 km
# 9. Lindwurmstraße 167, Munich, BY, Germany
#
# Total duration: 20.80 km

# Plot result
ts.plot_shortest_path(filename='munich_car.html') 
# filename is optional. If no filename is provided, nothing will be saved
```

Here is the result:

{% include munich_car.html %}

## Installation

