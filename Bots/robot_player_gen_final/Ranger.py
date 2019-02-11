import json
import numpy as np
import collections
from GameInitialization import bc
from GameInitialization import game_controller
import config
import Navigation
import random
import time
import Utilities

directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South,
              bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]
allDirections = list(bc.Direction)  # includes center, and is weirdly ordered
tryRotate = [0, -1, 1, -2, 2]
gc = game_controller.gc


def ranger_actions(unit_id):
    if not gc.can_sense_unit(unit_id):
        return
    this_unit = gc.unit(unit_id)

    config.my_units = gc.my_units()
    ranger_actions.attack_moving = False
    ranger_actions.boarded_rocket = False
    ranger_actions.moving_to_board_rocket = False

    if this_unit.location.is_in_garrison() or this_unit.location.is_in_space():
        return  # can't move from inside a factory

    # tick=time.clock()
    if gc.round() > config.rocket_launch_round and gc.planet() == bc.Planet.Earth:
        ranger_actions.boarded_rocket, ranger_actions.moving_to_board_rocket = Utilities.board_rocket(unit_id)
    # tock=time.clock()
    # print("BOAR ROCKET",(tick-tock)*1000)
    # tick=time.clock()
    if ranger_actions.boarded_rocket == False and ranger_actions.moving_to_board_rocket == False:
        ranger_actions.attack_moving = Utilities.attack_move(this_unit.id)
    # tock = time.clock()
    # print("ATTACK MOVE",(tick-tock)*1000)
    # tick=time.clock()
    if ranger_actions.attack_moving == False and ranger_actions.boarded_rocket == False and ranger_actions.moving_to_board_rocket == False:
        Utilities.random_moves(this_unit.id)
    # tock=time.clock()
    # print("RANDOM MOVE",(tick-tock)*1000)
