import battlecode as bc
import random
import sys
import traceback
import math
import gc_file

#gc.gc = bc.GameController()
directions = list(bc.Direction)

mars = bc.Planet.Mars
earth = bc.Planet.Earth

earth_map = gc_file.gc.starting_map(earth)
earth_width = earth_map.width
earth_height = earth_map.height

mars_map = gc_file.gc.starting_map(mars)
mars_width = mars_map.width
mars_height = mars_map.height

passable_locations_earth = {}

karbonite_locations_earth = []
karbonite_locations_mars = []

lst_of_passable_earth = []
lst_of_impassable_earth = []

lst_of_passable_mars = []
lst_of_impassable_mars = []

def initiate_maps():
    for x in range(earth_width):
        for y in range(earth_height):
            coords = (x, y)
            if x == -1 or y == -1 or x == earth_map.width or y == earth_map.height:
                passable_locations_earth[coords] = False
            elif earth_map.is_passable_terrain_at(bc.MapLocation(earth, x, y)):
                passable_locations_earth[coords] = True
            else:
                passable_locations_earth[coords] = False

    lst_of_passable_earth = [loc for loc in passable_locations_earth if passable_locations_earth[loc]]
    lst_of_impassable_earth = [loc for loc in passable_locations_earth if not passable_locations_earth[loc]]
    #print("EARTH: {}".format(lst_of_impassable_earth))


    mars_map = gc_file.gc.starting_map(bc.Planet.Mars)
    mars_width = mars_map.width
    mars_height = mars_map.height

    passable_locations_mars = {}

    for x in range(mars_width):
        for y in range(mars_height):
            coords = (x, y)
            if x == -1 or y == -1 or x == mars_map.width or y == mars_map.height:
                passable_locations_mars[coords] = False
            elif mars_map.is_passable_terrain_at(bc.MapLocation(mars, x, y)):
                passable_locations_mars[coords] = True
            else:
                passable_locations_mars[coords] = False

#print(passable_locations_mars)
#print(passable_locations_earth)

    for loc in passable_locations_mars:
        if passable_locations_mars[loc] == True:
            lst_of_passable_mars.append(loc)

    for loc in passable_locations_mars:
        if passable_locations_mars[loc] == False:
            lst_of_impassable_mars.append(loc)
    #print("MARS: {}".format(lst_of_impassable_mars))


    #print(lst_of_passable_mars)



'''
def get_karbonite(planet):
    if planet == earth:
        for i in range(earth_width):
            for j in range(earth_width):
                map_location = bc.MapLocation(earth, i, j)
                karbonite_at = gc_file.gc.karbonite_at(map_location)
                if karbonite_at > 0:
                    karbonite_locations_earth.append((x, y))

    elif planet == mars:
        for i in range(mars_width):
            for j in range(mars_width):
                map_location = bc.MapLocation(mars, i, j)
                karbonite_at = gc_file.gc.karbonite_at(map_location)
                if karbonite_at > 0:
                    karbonite_locations_mars.append((x, y))

    else:
        print("WRONG PLANET")
'''
