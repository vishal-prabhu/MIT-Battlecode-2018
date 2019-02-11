import battlecode as bc
import random
import sys
import traceback
import math
import gc_file
import map_info

my_team = gc_file.gc.team()
if my_team == bc.Team.Red:
    opponent_team = bc.Team.Blue
else:
    opponent_team = bc.Team.Red

my_karbonite_value = 0
my_units_value = 0

enemy_karbonite_value = 0
enemy_units_value = 0


myFactories = []
myWorkers = []
myHealers = []
myRangers = []
myMages = []
myKnights = []
myRockets = []

enemyFactories = []
enemyWorkers = []
enemyHealers = []
enemyRangers = []
enemyMages = []
enemyKnights = []
enemyRockets = []

someLoc = None

enemy_locations = []
enemies = []

# frequent try/catches are a good idea
def update_units():
    try:
        # walk through our units:
        for unit in gc_file.gc.my_units():
            if unit.unit_type == bc.UnitType.Factory:
                myFactories.append(unit)
            elif unit.unit_type == bc.UnitType.Worker:
                myWorkers.append(unit)
            elif unit.unit_type == bc.UnitType.Ranger:
                myRangers.append(unit)
            elif unit.unit_type == bc.UnitType.Knight:
                myKnights.append(unit)
            elif unit.unit_type == bc.UnitType.Healer:
                myHealers.append(unit)
            elif unit.unit_type == bc.UnitType.Mage:
                myMages.append(unit)
            elif unit.unit_type == bc.UnitType.Rocket:
                myRockets.append(unit)
            else:
                print("ERROR: Unknown unit type ", unit)

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

def compute_optimal_launch_time(curr_round):
    orbit_pattern = gc_file.gc.orbit_pattern()
    durations = [(i, orbit_pattern.duration(i)+i) for i in range(curr_round+5, curr_round + 30)]
    return min(durations, key = lambda x: x[1])

def launch(rocket):
    launched = 0
    while launched == 0:
        landing_site = random.choice(map_info.lst_of_passable_mars)
        #print("LANDING SITE: {}".format(landing_site))
        if gc_file.gc.can_launch_rocket(rocket.id, bc.MapLocation(map_info.mars, landing_site[0], landing_site[1])):
            gc_file.gc.launch_rocket(rocket.id, bc.MapLocation(map_info.mars, landing_site[0], landing_site[1]))
            launched = 1
    return
