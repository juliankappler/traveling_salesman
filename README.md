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
round trip. The following example is from [this notebook](Munich.ipynb).

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
        'Nordbad, München',
        'Münchner Stadtbibliothek Maxvorstadt',
        'Schellingstr. 4 Muenchen']
names_resolved, locations = ts.set_locations(names)
# To ensure that the provided names have been resolved correctly, one might
# want to compare names[i] with names_resolved[i]. The latter contains the
# name of the found location that will be used for the traveling salesman
# problem

# Solve the traveling salesman problem
results = ts.solve() # takes ~30s on my MacBook Pro
# by default, ts.solve() solves the traveling salesman problem three times
# and takes the best path of the three solutions
# Output:
# Found shortest path:
# 1. Lindwurmstraße 167, Munich, BY, Germany
#     1.74 km
# 2. Sendlinger-Tor-Platz, Munich, BY, Germany
#     1.94 km
# 3. Museumsinsel 1, Munich, BY, Germany
#     2.85 km
# 4. Schellingstraße 4, Munich, BY, Germany
#     0.89 km
# 5. Pinakothek der Moderne, Munich, BY, Germany
#     0.84 km
# 6. Münchner Stadtbibliothek Maxvorstadt, Munich, BY, Germany
#     1.36 km
# 7. Nordbad, Munich, BY, Germany
#     2.91 km
# 8. Rotkreuzplatz, Munich, BY, Germany
#     4.93 km
# 9. Lindwurmstraße 167, Munich, BY, Germany
#
# Total distance: 17.46 km

# Plot result
ts.plot_shortest_path(filename='munich_car.html') 
# filename is optional. If no filename is provided, nothing will be saved
```

Here is an illustration of the resulting round trip (locations are marked as blue dots, the routes between them as colored solid lines):

![munich_car](https://user-images.githubusercontent.com/37583039/232321130-6befe1fa-db3a-45cf-a94f-86968373553b.png)

An interactive map is obtained by opening the file munich_car.html in a 
browser. This interactive map can be viewed directly [here](https://htmlpreview.github.io/?https://github.com/juliankappler/traveling_salesman/blob/main/munich_car.html).

In [the example notebook](Munich.ipynb), also the shortest round trip for the
same locations and a pedestrian is solved. With a total distance of 16.00 km, 
the pedestrian has a slightly shorter route:

![munich_pedestrian](https://user-images.githubusercontent.com/37583039/232321135-fd0efcd4-a61f-403a-a94a-8183faf22ba0.png)

[Here is the corresponding interactive map](https://htmlpreview.github.io/?https://github.com/juliankappler/traveling_salesman/blob/main/munich_pedestrian.html).


## Installation

To use the module simply clone the repository, move the 
file [traveling_salesman.py](traveling_salesman.py) into your working directory,
and import it in your python script as shown in the above example
 (or the corresponding [notebook](Munich.ipynb)).

To download the repository and install the dependencies ([numpy](https://numpy.org/), [requests](https://requests.readthedocs.io/en/latest/), [plotly](https://plotly.com/python/)),
run the commands

```bash
>> git clone https://github.com/juliankappler/traveling_salesman.git
>> cd traveling_salesman
>> pip install -r requirements.txt
```
