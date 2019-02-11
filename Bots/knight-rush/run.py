import battlecode as bc
import random
import sys
import traceback


# ######################## INITIALIZE ########################
print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
#random.seed(6139)

# GLOBALS
enemy_locations = []
enemies = []

# ######################## Functions ########################


# Simple Actions
def try_harvest(worker):
    for direction in directions:
        if gc.can_harvest(worker.id, direction):
            # TODO: pick best place to harvest
            gc.harvest(worker.id, direction)
            return True
    return False


def try_move_strict(robot, direction):
    if gc.can_move(robot.id, direction) and gc.is_move_ready(robot.id):
        gc.move_robot(robot.id, direction)
        return True
    return False


def try_move_loose(robot, direction, tollerance):
    if not gc.is_move_ready(robot.id):
        return False
    if try_move_strict(robot, direction):
        return True
    left = direction
    right = direction
    for i in range(1, tollerance):
        left = rotate_left(left)
        right = rotate_right(right)
        if try_move_strict(robot, left) or try_move_strict(robot, right):
            return True
    return False


def nearest_enemy(my_map_location):
    nearest = None
    # print("Finding nearest of:", len(enemies), ' to ', my_map_location)
    if len(enemies) > 0:
        nearest_distance = 9999
        for enemy in enemies:
            if enemy.location.is_on_map():
                enemy_distance = my_map_location.distance_squared_to(enemy.location.map_location())
                # print("Enemy is ", enemy_distance, " away.")
                if nearest_distance > enemy_distance:
                    # print("Closer!", enemy_distance)
                    nearest_distance = enemy_distance
                    nearest = enemy
            # else:
            #     print("Enemy not on map:", enemy)
    # print("Found:", nearest)
    return nearest


# basic helper functions
def rotate_left(direction):
    if direction == bc.Direction.North:
        return bc.Direction.Northwest
    if direction == bc.Direction.Northwest:
        return bc.Direction.West
    if direction == bc.Direction.West:
        return bc.Direction.Southwest
    if direction == bc.Direction.Southwest:
        return bc.Direction.South
    if direction == bc.Direction.South:
        return bc.Direction.Southeast
    if direction == bc.Direction.Southeast:
        return bc.Direction.East
    if direction == bc.Direction.East:
        return bc.Direction.Northeast
    if direction == bc.Direction.Northeast:
        return bc.Direction.North
    if direction == bc.Direction.Center:
        return bc.Direction.Center


def rotate_right(direction):
    if direction == bc.Direction.North:
        return bc.Direction.Northeast
    if direction == bc.Direction.Northwest:
        return bc.Direction.North
    if direction == bc.Direction.West:
        return bc.Direction.Northwest
    if direction == bc.Direction.Southwest:
        return bc.Direction.West
    if direction == bc.Direction.South:
        return bc.Direction.Southwest
    if direction == bc.Direction.Southeast:
        return bc.Direction.South
    if direction == bc.Direction.East:
        return bc.Direction.Southeast
    if direction == bc.Direction.Northeast:
        return bc.Direction.East
    if direction == bc.Direction.Center:
        return bc.Direction.Center


def get_opposite_direction(direction):
    if direction == bc.Direction.North:
        return bc.Direction.South
    if direction == bc.Direction.Northwest:
        return bc.Direction.Southeast
    if direction == bc.Direction.West:
        return bc.Direction.East
    if direction == bc.Direction.Southwest:
        return bc.Direction.Northeast
    if direction == bc.Direction.South:
        return bc.Direction.North
    if direction == bc.Direction.Southeast:
        return bc.Direction.Northwest
    if direction == bc.Direction.East:
        return bc.Direction.West
    if direction == bc.Direction.Northeast:
        return bc.Direction.Southwest
    if direction == bc.Direction.Center:
        return bc.Direction.Center

def compute_optimal_launch_time(curr_round):
    orbit_pattern = gc.orbit_pattern()
    durations = [(i, orbit_pattern.duration(i)+i) for i in range(curr_round+5, curr_round + 30)]
    return min(durations, key = lambda x: x[1])

def launch(rocket):
    launched = 0
    while launched == 0:
        landing_site = random.choice(lst_of_passable_mars)
        #print("LANDING SITE: {}".format(landing_site))
        if gc.can_launch_rocket(rocket.id, bc.MapLocation(mars, landing_site[0], landing_site[1])):
            gc.launch_rocket(rocket.id, bc.MapLocation(mars, landing_site[0], landing_site[1]))
            launched = 1
    return

# ######################## Main ##############################

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)

mars = bc.Planet.Mars
earth = bc.Planet.Earth

launch_times = {}

my_team = gc.team()
if my_team == bc.Team.Red:
    opponent_team = bc.Team.Blue
else:
    opponent_team = bc.Team.Red

mars_map = gc.starting_map(bc.Planet.Mars)
mars_width = mars_map.width
mars_height = mars_map.height

passable_locations_mars = {}

for x in range(-1, mars_width + 1):
    for y in range(-1, mars_height + 1):
        coords = (x, y)
        if x == -1 or y == -1 or x == mars_map.width or y == mars_map.height:
            passable_locations_mars[coords] = False
        elif mars_map.is_passable_terrain_at(bc.MapLocation(mars, x, y)):
            passable_locations_mars[coords] = True
        else:
            passable_locations_mars[coords] = False

lst_of_passable_mars = [loc for loc in passable_locations_mars if passable_locations_mars[loc]]


while True:
    # We only support Python 3, which means brackets around print()

    myFactories = []
    myWorkers = []
    myHealers = []
    myRangers = []
    myMages = []
    myKnights = []
    myRockets = []

    someLoc = None

#if gc.round() > 645:
#        print(gc.round())

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():
            if unit.unit_type == bc.UnitType.Factory:
                myFactories.append(unit)
            elif unit.unit_type == bc.UnitType.Worker:
                myWorkers.append(unit)
            elif unit.unit_type == bc.UnitType.Knight:
                myKnights.append(unit)
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
            if someLoc is None and unit.location.is_on_map():
                someLoc = unit.location.map_location()
        """
        print('Knight Rush:', gc.round(),
              ' karbonite:', gc.karbonite(),
              ' units:', len(myWorkers), ',', len(myFactories), ',', len(myKnights))
        """
        
        if gc.planet() == bc.Planet.Earth:
            #print("EARTH!!!!!!!!!!!!!!!!!!!!!!!!!!")
            if len(myWorkers) < 5 and gc.karbonite() > 16:
                #print('Not enough workers:', gc.karbonite())
                d = random.choice(directions)
                for worker in myWorkers:
                    if gc.can_replicate(worker.id, d):
                        gc.replicate(worker.id, d)
                        #print('replicated! ', gc.karbonite())
                        break

            if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and (len(myFactories) < 3 or gc.karbonite() > 300):
                d = random.choice(directions)
                for worker in myWorkers:
                    if gc.can_blueprint(worker.id, bc.UnitType.Factory, d):
                        gc.blueprint(worker.id, bc.UnitType.Factory, d)
                        break

            factoriesToHeal = []
            for factory in myFactories:
                if factory.health < factory.max_health:
                    factoriesToHeal.append(factory)
                garrison = factory.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(factory.id, d):
                        gc.unload(factory.id, d)
                        continue
                elif gc.can_produce_robot(factory.id, bc.UnitType.Knight):
                    gc.produce_robot(factory.id, bc.UnitType.Knight)
                    continue

            if (len(myRockets) < 3 or gc.karbonite() > bc.UnitType.Rocket.blueprint_cost()) and gc.round() > 450 and gc.round() < 726:
                d = random.choice(directions)
                for worker in myWorkers:
                    if gc.can_blueprint(worker.id, bc.UnitType.Rocket, d):
                        gc.blueprint(worker.id, bc.UnitType.Rocket, d)
                        break

            # Have workers move to
            for worker in myWorkers:
                location = worker.location
                if not location.is_on_map():
                    # can't do anything, in garrison or rocket
                    continue
                map_location = location.map_location()

                # what to do?
                # Action: try building or repairing
                nearby = gc.sense_nearby_units(map_location, 2)
                for other in nearby:
                    if gc.can_build(worker.id, other.id):
                        gc.build(worker.id, other.id)
                        # print('built a factory!')
                        # skip moving
                        continue
                    if gc.can_repair(worker.id, other.id):
                        gc.repair(worker.id, other.id)
                        #print('repaired a factory!')
                        continue
                # Action: try harvesting
                try_harvest(worker)

                # where to go?
                if len(factoriesToHeal) > 0:  # move towards closest factory
                    closestFactory = None
                    distance = 999
                    mapLocation = location.map_location()
                    for factory in factoriesToHeal:
                        loc = factory.location.map_location()
                        dist = mapLocation.distance_squared_to(loc)
                        if dist < distance:
                            distance = dist
                            closestFactory = factory
                    if closestFactory is not None:
                        # print("Moving to closest factory:", dist)
                        d = mapLocation.direction_to(factory.location.map_location())
                        try_move_strict(worker, d)
                        # if gc.is_move_ready(worker.id) and gc.can_move(worker.id, d):
                        #     gc.move_robot(worker.id, d)
                
                else:  # move randomly
                    d = random.choice(directions)
                    try_move_loose(worker, d, 1)
                    # if gc.is_move_ready(worker.id) and gc.can_move(worker.id, d):
                    #     gc.move_robot(worker.id, d)

            '''
            if gc.round() > 550 and len(myRockets) > 0:
                workers_in_rocket = 0
                for rocket in myRockets:
                    rocket_loc = rocket.location.map_location()
                    for dir in directions[:-1]:
                        near = rocket_loc.add(dir)
                        if gc.has_unit_at_location(near):
                            nearby_unit = gc.sense_unit_at_location(near)
                            if nearby_unit.unit_type == bc.UnitType.Worker:
                                if workers_in_rocket < 4:
                                    workers_in_rocket += 1
                                else:
                                    continue
                            if nearby_unit.unit_type != bc.UnitType.Factory and nearby_unit.unit_type != bc.UnitType.Rocket and gc.can_load(rocket.id, nearby_unit.id):
                                gc.load(rocket.id, nearby_unit.id)
                                print("Loading")
            '''


            if location.is_on_map():
                if gc.round() > 450 and len(myRockets) > 0:
                    #rocket_loc = rocket.location.map_location()
                    is_rocket_adjacent = gc.sense_nearby_units_by_team(location.map_location(), 2, my_team)
                    for rocket in is_rocket_adjacent:
                        if rocket.unit_type == bc.UnitType.Rocket and gc.can_load(rocket.id, knight.id):
                            print("WHY IS THIS NOT WORKING")
                            gc.load(rocket.id, knight.id)
                            continue
                                
                        nearby_units = gc.sense_nearby_units_by_team(location.map_location(), 25, my_team)
                        dist = []
                        for unit in nearby_units:
                            if unit.unit_type == bc.UnitType.Rocket and (len(unit.structure_garrison()) < 8):
                                unit_loc = unit.location.map_location()
                                d = location.map_location().direction_to(unit_loc)
                                if gc.is_move_ready(knight.id) and gc.can_move(knight.id, d):
                                    gc.move_robot(knight.id, d)
                                    continue

            if gc.round() > 500 and len(myRockets) > 0:
                workers_in_rocket = 0
                for rocket in myRockets:
                    rocket_loc = rocket.location.map_location()
                    nearby_units = gc.sense_nearby_units_by_team(rocket_loc, 2, my_team)
                    for unit in nearby_units:
                        if unit.unit_type == bc.UnitType.Worker:
                            if workers_in_rocket < 4 and gc.can_load(rocket.id, unit.id):
                                gc.load(rocket.id, unit.id)
                                workers_in_rocket += 1
                        elif unit.unit_type != bc.UnitType.Factory and unit.unit_type != bc.UnitType.Rocket and gc.can_load(rocket.id, unit.id):
                            gc.load(rocket.id, unit.id)
                        #print("Loading")
                        else:
                            continue

            '''
            if len(launch_times) > 0:
                if gc.round() in launch_times:
                    print("Launching!!")
                    rocket_to_launch = launch_times[gc.round()]
                    for r in rocket_to_launch:
                        launch(r)
                        del launch_times[gc.round()]
                        print("Launch times after deletion: {}".format(launch_times))
            '''

            #print("Before launch logic")
            #print("My rockets: {} : {}".format(len(myRockets), myRockets))
            for rocket in myRockets:
                if rocket.structure_is_built():
                    #print("In launch logic")
                    if rocket.id in launch_times:
                        if launch_times[rocket.id] <= gc.round():
                            #print("launching!!!")
                            launch(rocket)
                            del launch_times[rocket.id]
                    
                    else:
                        if len(rocket.structure_garrison()) > 6 or (gc.round() >= 700 and len(rocket.structure_garrison()) > 0):
                            #print("Setting launch time")
                            time = compute_optimal_launch_time(gc.round())[0]
                                #if rocket.id in launch_times:
                                #if rocket.id in launch_times:
                                #    continue
                                #else:
                                #launch_times[time].append(rocket.id)
                                #else:
                            launch_times[rocket.id] = time
                        #print("launch times: {}".format(launch_times))
#print("garrison: {}".format(len(rocket.structure_garrison())))
            
            '''
            if len(launch_times) > 0 :
                print("In launch logic")
                if launch_times.get(gc.round()) != None:
                    print("Launching!!")
                    rocket_to_launch = launch_times.get(gc.round())
                    launch(rocket_to_launch)
                    continue
            '''


        else:   # Mars
        #print("HEYA")
            for rocket in myRockets:
                if rocket.location.is_on_map():
                    loc = rocket.location.map_location()
                    if rocket.location.is_on_planet(mars):
                        if len(rocket.structure_garrison()) > 0:  # try to unload a unit if there exists one in the garrison
                            d = random.choice(directions)
                            if d is not None and gc.can_unload(rocket.id, d):
                                gc.unload(rocket.id, d)

            for worker in myWorkers:
                location = worker.location
                if location.is_on_planet(mars):
                    map_location = location.map_location()
                    try_harvest(worker)
                    d = random.choice(directions)
                    try_move_loose(worker, d, 1)
        
        enemy_locations = []
        # sense enemies
        if someLoc is not None:
            enemies = list(gc.sense_nearby_units_by_team(someLoc, 5001, opponent_team))
            #print('enemies sensed:', len(enemies))
            for unit in enemies:
                if unit.location.is_on_map():
                    enemy_locations.append(unit.location.map_location())

        # moves knights around randomly
        for knight in myKnights:
            location = knight.location
            
            if location.is_on_map():
                mapLoc = location.map_location()
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if other.team != my_team and gc.is_attack_ready(knight.id) and gc.can_attack(knight.id, other.id):
                        #print('attacked a thing!')
                        gc.attack(knight.id, other.id)
                        continue

                target = nearest_enemy(mapLoc)
                if target is not None:
                    if gc.is_attack_ready(knight.id) and gc.can_attack(knight.id, target.id):
                        #print('better attack')
                        gc.attack(knight.id, target.id)
                    distance = mapLoc.distance_squared_to(target.location.map_location())
                    if not target.location.map_location().is_within_range(knight.attack_range(), mapLoc):
                        try_move_loose(knight, mapLoc.direction_to(target.location.map_location()), 2)
                        #elif target.location.map_location().is_within_range(knight.knight_cannot_attack_range()+1, mapLoc):
                        #try_move_loose(knight, target.location.map_location().direction_to(mapLoc), 2)

                else:
                    d = random.choice(directions)
                    if gc.is_move_ready(knight.id) and gc.can_move(knight.id, d):
                        gc.move_robot(knight.id, d)


#print(gc.manager_karbonite(my_team))
        #print(gc.is_over())

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

#print("ROUND ENDING")
    karbonite_value = gc.manager_karbonite(my_team)
    units_value = ((len(myMages)+len(myHealers)+len(myRangers)+len(myKnights)) * 20) + (len(myFactories) * 100) + (len(myRockets) * 75) + (len(myWorkers) * 25)

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    print("karbonite: {}".format(karbonite_value))
    print("units: {}".format(units_value))


#print("KARBONITE: {}".format(gc.manager_karbonite(opponent_team)))
#if gc.is_over():
#        print("{} is the winner!!".format(gc.winning_team()))
#print("My units: {} round: {}".format(len(myMages)+len(myHealers)+len(myRangers)+len(myKnights)+len(myFactories)+len(myRockets)+len(myWorkers), gc.round()))
    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

#if gc.is_over():
#    print("Halelujah")
