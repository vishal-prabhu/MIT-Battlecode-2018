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


def healer_actions(unit_id):
    this_healer = gc.unit(unit_id)
    config.my_units = gc.my_units()
    #print("I AM HEALER", unit_id)
    healable_friendly = 0

    if not this_healer.location.is_in_garrison():  # can't move from inside a factory
        friendlies = gc.sense_nearby_units_by_team(this_healer.location.map_location(), this_healer.attack_range(),
                                                   config.my_team)

        if len(friendlies)>0:
            for friendly in friendlies:
                if friendly.health / friendly.max_health <= .9:
                    healable_friendly = friendly.id
                    break

        if healable_friendly > 0:
            if gc.is_heal_ready(this_healer.id) and this_healer.attack_heat() < 10:
                gc.heal(this_healer.id, healable_friendly)

        elif gc.is_move_ready(this_healer.id):
            nearbyFriendlies = gc.sense_nearby_units_by_team(this_healer.location.map_location(),
                                                             this_healer.vision_range,
                                                             config.my_team)
            if len(nearbyFriendlies) > 0:
                destination = nearbyFriendlies[0].location.map_location()
                print("Friends nearby")
            else:
                print("no friends moving randomly")
                destination = this_healer.location.map_location().add(Navigation.random_dir())
            Navigation.fuzzygoto(this_healer.id, destination)
