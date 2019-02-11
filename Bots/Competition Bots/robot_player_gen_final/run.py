import config
from GameInitialization import bc
from GameInitialization import game_controller
import sys
import traceback
import numpy as np
import time
import Utilities
import Navigation
import Worker
import Factory
import Ranger
import Knight
import Mage
import Rocket

gc = game_controller.gc

directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South,
              bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]
allDirections = list(bc.Direction)  # includes center, and is weirdly ordered
tryRotate = [0, -1, 1, -2, 2]

config.my_team = game_controller.my_team

if config.my_team == bc.Team.Red:
    config.enemy_team = bc.Team.Blue
if config.my_team == bc.Team.Blue:
    config.enemy_team = bc.Team.Red

print(config.my_team)
print(config.enemy_team)

gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)

config.my_units = gc.my_units()

config.planet_map = Navigation.ProcessMap()
config.planet_pathing = Navigation.Pathing(config.planet_map.terrain_array)
config.karbonite_map = np.copy(config.planet_map.karbonite_array)
Utilities.build_targets_set()


if gc.planet() == bc.Planet.Earth:
    config.planet_map.sector_breadth_first_search()
    config.planet_map.sector_aStar_search()

if gc.planet() == bc.Planet.Mars:
    config.planet_map.sector_breadth_first_search()
    config.planet_map.sector_aStar_search()

while True:

    print('pyround:', config.global_round, 'time left:', gc.get_time_left_ms(), 'ms', ">>>>>>>>>>>>>>>")

    config.worker_count, config.healer_count, config.mage_count, config.ranger_count, config.knight_count, config.factory_count \
        , config.rocket_count = Utilities.census()

    config.my_units = gc.my_units()

    try:

        for unit in config.my_units:
            if unit.unit_type != bc.UnitType.Factory and not unit.location.is_in_garrison():
                Utilities.global_enemy_scanner(unit.location.map_location())

            if unit.unit_type == bc.UnitType.Worker:
                # tick=time.clock()
                Worker.worker_actions(unit.id)
                # tock=time.clock()
                # print("Worker",unit.id,"time to act",(tick-tock)*1000,"ms")
            # if unit.unit_type == bc.UnitType.Healer:
            # Healer.healer_actions(unit.id)

            if unit.unit_type == bc.UnitType.Mage:
                Mage.mage_actions(unit.id)

            if unit.unit_type == bc.UnitType.Ranger:
                # tick = time.clock()
                Ranger.ranger_actions(unit.id)
                # tock = time.clock()
                # print("Ranger", unit.id, "time to act", (tick - tock) * 1000, "ms")

            if unit.unit_type == bc.UnitType.Knight:
                Knight.knight_actions(unit.id)

            if unit.unit_type == bc.UnitType.Factory:
                # tick = time.clock()
                Factory.factory_actions(unit.id)
                # tock = time.clock()
                # print("Factory", unit.id, "time to act", (tick - tock) * 1000, "ms")

            if unit.unit_type == bc.UnitType.Rocket:
                Rocket.rocket_actions(unit.id)


    except Exception as e:
        print('Error:', e)

        traceback.print_exc()

    tock = time.clock()
    gc.next_turn()

    sys.stdout.flush()
    sys.stderr.flush()
