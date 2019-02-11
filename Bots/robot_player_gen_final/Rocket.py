import json
import numpy as np
import collections
from GameInitialization import bc
from GameInitialization import game_controller
import config
import Navigation
import random

directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South,
              bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]
allDirections = list(bc.Direction)  # includes center, and is weirdly ordered
tryRotate = [0, -1, 1, -2, 2]
gc = game_controller.gc


def rocket_actions(unit_id):
    if gc.unit(unit_id).structure_is_built() and (gc.unit(unit_id).location.is_on_planet(bc.Planet.Earth) or
                                                  gc.unit(unit_id).location.is_on_planet(bc.Planet.Mars)):
        config.my_units = gc.my_units()
        this_rocket = gc.unit(unit_id)
        # print ("I AM ROCKET", unit_id)
    else:
        return

    garrison = this_rocket.structure_garrison()

    if gc.round() >= config.rocket_launch_round and this_rocket.location.is_on_planet(bc.Planet.Earth):

        if len(garrison) >= 7:  #
            destination = Navigation.pick_random_landing_location()
            if gc.can_launch_rocket(this_rocket.id, destination):
                gc.launch_rocket(this_rocket.id, destination)

        else:
            if gc.round() >= 700 and len(garrison) >= 1:
                if gc.can_launch_rocket(this_rocket.id, Navigation.pick_random_landing_location()):
                    gc.launch_rocket(this_rocket.id, Navigation.pick_random_landing_location())

    if this_rocket.location.is_on_planet(bc.Planet.Mars):
        if len(garrison) > 0:  # ungarrison
            d = random.choice(directions)
            if gc.can_unload(this_rocket.id, d):
                gc.unload(this_rocket.id, d)
                config.my_units = gc.my_units()
