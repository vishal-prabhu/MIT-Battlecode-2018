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


def factory_actions(unit_id):
    this_factory = gc.unit(unit_id)
    config.my_units = gc.my_units()
    factory_actions.producing_robot = False
    # print ("I AM FACTORY", unit_id)

    garrison = this_factory.structure_garrison()

    if len(garrison) > 0:  # ungarrison
        d = random.choice(directions)
        if gc.can_unload(this_factory.id, d):
            gc.unload(this_factory.id, d)
    elif gc.can_produce_robot(this_factory.id, bc.UnitType.Worker) and (
            config.worker_count <= config.worker_target or config.worker_count <= 2) and factory_actions.producing_robot == False:
        gc.produce_robot(this_factory.id, bc.UnitType.Worker)
        factory_actions.producing_robot = True
    # print("Producing Worker!")

    elif gc.can_produce_robot(this_factory.id,
                              bc.UnitType.Ranger) and config.ranger_count <= config.ranger_target and factory_actions.producing_robot == False:
        gc.produce_robot(this_factory.id, bc.UnitType.Ranger)
    # print("Producing Ranger!")

    elif gc.can_produce_robot(this_factory.id, bc.UnitType.Mage) and config.mage_count <= config.mage_target:
        gc.produce_robot(this_factory.id, bc.UnitType.Mage)
        # print("Producing Mage!")

    elif gc.can_produce_robot(this_factory.id, bc.UnitType.Knight) and config.knight_count <= config.knight_target:
        gc.produce_robot(this_factory.id, bc.UnitType.Knight)
        # print("Producing Knight!")

    elif gc.can_produce_robot(this_factory.id, bc.UnitType.Ranger) and config.mage_count >= config.mage_target and \
            config.ranger_count >= config.ranger_target \
            and config.knight_count >= config.knight_target and config.ranger_count <= config.ranger_target:
        gc.produce_robot(this_factory.id, bc.UnitType.Ranger)
    # print("Producing Mage!")
