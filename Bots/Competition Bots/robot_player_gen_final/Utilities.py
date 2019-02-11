from GameInitialization import bc
from GameInitialization import game_controller
import random
import sys
import traceback
import os
import json
import collections
import numpy as np
import time
import Navigation
import Worker
import config

gc = game_controller.gc
my_unit_list = None


def census():
    worker_count_temp, healer_count_temp, mage_count_temp, ranger_count_temp, knight_count_temp, factory_count_temp \
        , rocket_count_temp = 0, 0, 0, 0, 0, 0, 0
    census_units = gc.my_units()
    for unit in census_units:
        if unit.unit_type == bc.UnitType.Worker:
            worker_count_temp = worker_count_temp + 1

        if unit.unit_type == bc.UnitType.Healer:
            healer_count_temp = healer_count_temp + 1

        if unit.unit_type == bc.UnitType.Mage:
            mage_count_temp = mage_count_temp + 1

        if unit.unit_type == bc.UnitType.Ranger:
            ranger_count_temp = ranger_count_temp + 1

        if unit.unit_type == bc.UnitType.Knight:
            knight_count_temp = knight_count_temp + 1

        if unit.unit_type == bc.UnitType.Factory:
            factory_count_temp = factory_count_temp + 1

        if unit.unit_type == bc.UnitType.Rocket:
            rocket_count_temp = rocket_count_temp + 1

    return (worker_count_temp, healer_count_temp, mage_count_temp, ranger_count_temp, knight_count_temp,
            factory_count_temp, rocket_count_temp)


def global_enemy_scanner(location1):
    if config.global_round != gc.round():
        config.global_enemy_scan = None
        config.global_enemy_scan = gc.sense_nearby_units_by_team(location1, 99999,
                                                                 config.enemy_team)
        config.global_round = gc.round()

        # if len(config.global_enemy_scan) > 0:
        # print("round", gc.round(), "GLOBAL SCAN COMPLETE ENEMIES DETECTED Found", len(config.global_enemy_scan),
        # "Enemies")
        # print("target location", config.global_enemy_scan[0])


def avoid_enemies(unit_id):
    nearbyEnemies = gc.sense_nearby_units_by_team(gc.unit(unit_id).location.map_location(),
                                                  gc.unit(unit_id).vision_range, config.enemy_team)

    if len(nearbyEnemies) > 0:
        for enemy in nearbyEnemies:
            if enemy.unit_type != bc.UnitType.Worker and enemy.unit_type != bc.UnitType.Factory and enemy.unit_type != bc.UnitType.Rocket and enemy.unit_type != bc.UnitType.Healer:
                dir_to_run = enemy.location.map_location().direction_to(
                    gc.unit(unit_id).location.map_location())
                destination = gc.unit(unit_id).location.map_location().add(dir_to_run)
                Navigation.fuzzygoto(gc.unit(unit_id).id, destination)
                return True
            else:
                return False
    return False


def attack_move(unit_id):
    attackableEnemies = gc.sense_nearby_units_by_team(gc.unit(unit_id).location.map_location(),
                                                      gc.unit(unit_id).attack_range(), config.enemy_team)

    if len(attackableEnemies) <= 0 and len(config.global_enemy_scan) <= 0:
        return False

    if len(attackableEnemies) > 0:

        Navigation.a_star_move(unit_id, attackableEnemies[0].location.map_location())
        if gc.is_attack_ready(gc.unit(unit_id).id) and gc.can_attack(gc.unit(unit_id).id,
                                                                     attackableEnemies[0].id) and gc.unit(
                unit_id).attack_heat() < 10:
            gc.attack(gc.unit(unit_id).id, attackableEnemies[0].id)

        return True

    else:
        if len(config.global_enemy_scan) > 0:
            destination = config.global_enemy_scan[0].location.map_location()
            distance_to_enemy = gc.unit(unit_id).location.map_location().distance_squared_to(destination)
            if distance_to_enemy > 100:
                Navigation.fuzzygoto(unit_id, config.global_enemy_scan[0].location.map_location())
            else:
                Navigation.a_star_move(unit_id, destination)

            return True

    return False


def board_rocket(unit_id):
    if gc.planet() == bc.Planet.Mars:
        return
    nearby_rockets = gc.sense_nearby_units_by_type(gc.unit(unit_id).location.map_location(), 99999,
                                                   bc.UnitType.Rocket)

    if len(nearby_rockets) <= 0:
        return False, False
    board_rocket.distance = 9999
    board_rocket.target_unit = None
    for unit in nearby_rockets:
        if unit.structure_is_built() and unit.team == config.my_team and len(unit.structure_garrison()) < 8:
            if gc.can_load(unit.id, gc.unit(unit_id).id):
                gc.load(unit.id, gc.unit(unit_id).id)
                return True, False

            else:
                new_distance = unit.location.map_location().distance_squared_to(
                    gc.unit(unit_id).location.map_location())
                if new_distance < board_rocket.distance and unit.structure_is_built() and unit.team == config.my_team and len(
                        unit.structure_garrison()) < 8:
                    board_rocket.target_unit = unit.id

    if board_rocket.target_unit != None:
        destination = gc.unit(board_rocket.target_unit).location.map_location()
        Navigation.fuzzygoto(gc.unit(unit_id).id, destination)
        return False, True

    return False, False


def random_moves(unit_id):
    if gc.unit(unit_id).location.is_in_garrison() or gc.unit(unit_id).location.is_in_space():
        return
    if config.attack_moving == False and config.rocket_boarding == False:
        destination = gc.unit(unit_id).location.map_location().add(Navigation.random_dir())
        Navigation.fuzzygoto(gc.unit(unit_id).id, destination)
        return


def build_targets_set():
    if (config.planet_map.planet_y * config.planet_map.planet_x) <= 400:
        config.mapsize = "S"
        config.factory_target = 2
        config.rocket_target = 2
        config.rocket_target_round = 500
        config.worker_target = 4
        config.ranger_target = 15
        config.mage_target = 10
        config.knight_target = 6
        config.healer_target = 0
    if (config.planet_map.planet_y * config.planet_map.planet_x) > 400 and (
            config.planet_map.planet_y * config.planet_map.planet_x) <= 1200:
        config.mapsize = "M"
        config.factory_target = 4
        config.rocket_target = 10
        config.rocket_target_round = 500
        config.worker_target = 3
        config.ranger_target = 20
        config.knight_target = 10
        config.mage_target = 15
        config.healer_target = 0
    if (config.planet_map.planet_y * config.planet_map.planet_x) > 1200:
        config.mapsize = "L"
        config.factory_target = 6
        config.rocket_target = 16
        config.rocket_target_round = 500
        config.worker_target = 16
        config.ranger_target = 25
        config.mage_target = 15
        config.knight_target = 15
        config.healer_target = 0
