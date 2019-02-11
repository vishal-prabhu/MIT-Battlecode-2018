import json
import numpy as np
import collections
from GameInitialization import bc
from GameInitialization import game_controller
import config
import Navigation
import Utilities
import time

directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South,
              bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]
allDirections = list(bc.Direction)  # includes center, and is weirdly ordered
tryRotate = [0, -1, 1, -2, 2]
gc = game_controller.gc


def worker_actions(unit_id):
    if not gc.can_sense_unit(unit_id):
        return
    this_worker = gc.unit(unit_id)
    config.my_units = gc.my_units()
    worker_actions.building_rocket = False
    worker_actions.building_factory = False
    worker_actions.moving_to_build = False
    worker_actions.harvesting_karbonite = False
    worker_actions.harvesting_location = False

    worker_actions.destination = None
    worker_actions.moving_to_harvest = False
    worker_actions.boarded_rocket = False
    worker_actions.avoiding_enemies = False
    worker_actions.moving_to_board_rocket = False

    def build_rocket(unit_id):
        worker_actions.building_rocket = False
        worker_actions.worker_moving_to_build = False
        if gc.round() >= config.rocket_target_round and config.rocket_count < config.rocket_target:
            for dir in directions:
                if gc.can_blueprint(unit_id, bc.UnitType.Rocket, dir):
                    gc.blueprint(unit_id, bc.UnitType.Rocket, dir)
                    config.rocket_count = config.rocket_count + 1
                    worker_actions.building_rocket = True
                    worker_actions.moving_to_build = False
                    return

        very_nearby_rockets = gc.sense_nearby_units_by_type(gc.unit(unit_id).location.map_location(), 1,
                                                            bc.UnitType.Rocket)
        if len(very_nearby_rockets) > 0:
            for unit in very_nearby_rockets:
                if not unit.structure_is_built() and unit.team == config.my_team:
                    blueprint_waiting = unit.id
                    if gc.can_build(unit_id, blueprint_waiting):
                        gc.build(unit_id, blueprint_waiting)
                        worker_actions.moving_to_build = False
                        worker_actions.building_rocket = True
                        return

        nearby_rockets = gc.sense_nearby_units_by_type(gc.unit(unit_id).location.map_location(), 60,
                                                       bc.UnitType.Rocket)
        if worker_actions.building_rocket is False:
            if len(nearby_rockets) > 0:
                for unit in nearby_rockets:
                    if not unit.structure_is_built() and unit.team == config.my_team:
                        worker_actions.destination = unit.location.map_location()
                        worker_actions.moving_to_build = True
                        worker_actions.building_rocket = False
                        Navigation.fuzzygoto(gc.unit(unit_id).id, worker_actions.destination)
                        return

        worker_actions.building_rocket = False
        worker_actions.worker_moving_to_build = False
        return

    def build_factory(unit_id):
        worker_actions.building_factory = False
        worker_actions.moving_to_build = False
        if config.factory_count < config.factory_target and gc.round() < config.rocket_target_round:
            for dir in directions:
                if gc.can_blueprint(unit_id, bc.UnitType.Factory, dir):
                    gc.blueprint(unit_id, bc.UnitType.Factory, dir)
                    config.factory_count = config.factory_count + 1
                    worker_actions.building_factory = True
                    worker_actions.moving_to_build = False
                    return

        very_nearby_factories = gc.sense_nearby_units_by_type(gc.unit(unit_id).location.map_location(), 1,
                                                              bc.UnitType.Factory)

        if len(very_nearby_factories) > 0:
            for unit in very_nearby_factories:
                if not unit.structure_is_built() and unit.team == config.my_team:
                    # factories_qued = factories_qued + 1
                    blueprint_waiting = unit.id
                    if gc.can_build(unit_id, blueprint_waiting):
                        gc.build(unit_id, blueprint_waiting)
                        worker_actions.building_factory = True
                        worker_actions.moving_to_build = False
                        return

        nearby_factories = gc.sense_nearby_units_by_type(gc.unit(unit_id).location.map_location(), 16,
                                                         bc.UnitType.Factory)
        if worker_actions.building_factory is False:
            if len(nearby_factories) > 0:
                for unit in nearby_factories:
                    if not unit.structure_is_built() and unit.team == config.my_team:
                        # print("factory built",unit.structure_is_built())
                        worker_actions.destination = unit.location.map_location()
                        worker_actions.building_factory = False
                        worker_actions.moving_to_build = True
                        # print("inner move to build",worker_actions.moving_to_build)
                        Navigation.fuzzygoto(gc.unit(unit_id).id, worker_actions.destination)
                        return
        worker_actions.building_factory = False
        worker_actions.moving_to_build = False

        return

    def replicate(unit_id):

        if gc.unit(unit_id).location.is_on_planet(bc.Planet.Earth):
            if config.worker_count < 3 or (config.factory_count >= 1 and config.worker_count < config.worker_target) or \
                    (worker_actions.harvesting_karbonite == True and config.worker_count < min(
                        int(config.planet_map.planet_total_starting_karbonite / 300), 20)):
                for dir in directions:
                    if gc.can_replicate(unit_id, dir):
                        gc.replicate(unit_id, dir)
                        config.worker_count = config.worker_count + 1

        if gc.unit(unit_id).location.is_on_planet(bc.Planet.Mars):
            for dir in directions:
                if gc.can_replicate(unit_id, dir) and config.worker_count < 100:
                    gc.replicate(unit_id, dir)
                    config.worker_count = config.worker_count + 1

    def harvest_karbonite(unit_id):

        tick = time.clock()
        loc = find_karbonite(unit_id)

        tock = time.clock()
        # print("time to find karb", (tick - tock) * 1000, loc, gc.unit(unit_id).location.map_location())

        # print("distance to karb", loc.distance_squared_to(gc.unit(unit_id).location.map_location()))

        if gc.unit(unit_id).location.map_location().distance_squared_to(loc) <= 2:
            harvest_karbonite_at_location(loc)
            # print("harvesting, less than 2 dist, 141")

        if gc.unit(unit_id).location.map_location().distance_squared_to(loc) > 2:
            Navigation.a_star_move(unit_id, loc)

    def harvest_karbonite_at_location(loc):
        np_loc = Navigation.trans_coord_to_np(loc)
        # print(np_loc)
        y = np_loc[0]
        x = np_loc[1]
        # print(y,x)
        if gc.can_sense_location(loc):
            karb_at_loc = gc.karbonite_at(loc)
            # print("karb at location",karb_at_loc)
            if karb_at_loc == 0:
                config.karbonite_map[y, x] = 0
                # print("updated karb",config.karbonite_map[y,x])
                worker_actions.harvesting_karbonite = False
                worker_actions.harvesting_location = None
            if karb_at_loc > 0:
                config.karbonite_map[y, x] = karb_at_loc
                # print("updated karb",config.karbonite_map[y,x])
                bestDir = gc.unit(unit_id).location.map_location().direction_to(loc)
                # print("karb direction", bestDir)
                if gc.can_harvest(gc.unit(unit_id).id, bestDir):
                    gc.harvest(gc.unit(unit_id).id, bestDir)
                    # print("harvested", bestDir)
                    worker_actions.harvesting_karbonite = True
                    worker_actions.harvesting_location = loc

    def find_karbonite(unit_id):

        start = Navigation.trans_coord_to_np(gc.unit(unit_id).location.map_location())
        start = (start[0], start[1])

        if config.karbonite_map[start[0], start[1]] > 0 or config.karbonite_depleted == True:
            # print("found karbonite at",start[0],start[1])
            return Navigation.trans_coord_to_ml(start[0], start[1])

        levels = max(config.planet_map.planet_x, config.planet_map.planet_y)
        y_root = start[0]
        x_root = start[1]

        for level in range(1, levels + 1):
            y_allowed = [level, -level]
            x_allowed = [level, -level]
            for y in y_allowed:
                for x in range(-level, level + 1):
                    if 0 <= x + x_root < config.planet_map.planet_x and 0 <= y + y_root < config.planet_map.planet_y:
                        # print(y + y_root,config.planet_map.planet_y-1, x + x_root,config.planet_map.planet_x-1)
                        if config.karbonite_map[y + y_root, x + x_root] > 0:
                            # print("found karbonite", y + y_root, x + x_root,config.karbonite_map[y + y_root, x + x_root])
                            return Navigation.trans_coord_to_ml(y + y_root, x + x_root)
            for x in x_allowed:
                for y in range(-(level + 1), level):
                    if 0 <= x + x_root < config.planet_map.planet_x and 0 <= y + y_root < config.planet_map.planet_y:
                        # print(y + y_root, config.planet_map.planet_y - 1, x + x_root, config.planet_map.planet_x - 1)
                        if config.karbonite_map[y + y_root, x + x_root] > 0:
                            # print("found karbonite", y + y_root, x + x_root,config.karbonite_map[y + y_root, x + x_root])
                            return Navigation.trans_coord_to_ml(y + y_root, x + x_root)
        config.karbonite_depleted = True
        return gc.unit(unit_id).location.map_location()

    if this_worker.location.is_on_planet(bc.Planet.Earth) and not (
            this_worker.location.is_in_garrison() or this_worker.location.is_in_space()):
        # tick=time.clock()
        worker_actions.avoid_enemies = Utilities.avoid_enemies(unit_id)
        # tock=time.clock()
        # print((tick-tock)*1000)
        if worker_actions.avoid_enemies == False:

            build_rocket(unit_id)

            build_factory(unit_id)

            if worker_actions.building_factory == False and worker_actions.moving_to_build == False and worker_actions.building_rocket == False \
                    and config.karbonite_depleted == False:
                harvest_karbonite(unit_id)

            replicate(unit_id)

            if gc.round() > config.rocket_launch_round and gc.planet() == bc.Planet.Earth:
                worker_actions.boarded_rocket, worker_actions.moving_to_board_rocket = Utilities.board_rocket(unit_id)

            if config.karbonite_depleted == True and worker_actions.building_factory == False and worker_actions.moving_to_build == False and worker_actions.building_rocket == False and worker_actions.boarded_rocket == False and worker_actions.avoid_enemies == False and worker_actions.moving_to_board_rocket == False:
                destination = gc.unit(unit_id).location.map_location().add(Navigation.random_dir())
                Navigation.fuzzygoto(gc.unit(unit_id).id, destination)


def onEarth(loc):
    if (loc.x < 0) or (loc.y < 0) or (loc.x >= config.planet_map.planet_x) or (
            loc.y >= config.planet_map.planet_y): return False
    return True


def checkK(loc):
    if not onEarth(loc): return 0
    if gc.can_sense_location(loc):
        return gc.karbonite_at(loc)
    else:
        return 0


def bestKarboniteDirection(loc):
    mostK = 0
    bestDir = None
    for dir in allDirections:
        newK = checkK(loc.add(dir))
        if newK > mostK:
            mostK = newK
            bestDir = dir
    return mostK, bestDir
