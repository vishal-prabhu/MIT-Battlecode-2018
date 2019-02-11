import battlecode as bc
import gc_file
import random
import sys
import traceback
import math
import potential_fields as pf
import units
import evolution
import map_info

# ######################## INITIALIZE ########################
print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
#gc = bc.GameController()
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
        if gc_file.gc.can_harvest(worker.id, direction):
            # TODO: pick best place to harvest
            gc_file.gc.harvest(worker.id, direction)
            return True
    return False


def try_move_strict(robot, direction):
    if gc_file.gc.can_move(robot.id, direction) and gc_file.gc.is_move_ready(robot.id):
        gc_file.gc.move_robot(robot.id, direction)
        return True
    return False


def try_move_loose(robot, direction, tollerance):
    if not gc_file.gc.is_move_ready(robot.id):
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
                #print("Enemy is ", enemy_distance, " away.")
                if nearest_distance > enemy_distance:
                    # print("Closer!", enemy_distance)
                    nearest_distance = enemy_distance
                    nearest = enemy
            # else:
            #     print("Enemy not on map:", enemy)
    #print("My loc: {},  enemy loc: {},  d: {}".format(my_map_location, nearest.location.map_location(), nearest_distance))
    #print("Found:", nearest)
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



# ######################## Main ##############################

# let's start off with some research!
# we can queue as much as we want.
gc_file.gc.queue_research(bc.UnitType.Worker)
gc_file.gc.queue_research(bc.UnitType.Knight)
gc_file.gc.queue_research(bc.UnitType.Knight)
gc_file.gc.queue_research(bc.UnitType.Knight)
gc_file.gc.queue_research(bc.UnitType.Rocket)
gc_file.gc.queue_research(bc.UnitType.Rocket)
gc_file.gc.queue_research(bc.UnitType.Rocket)

#print("START")

launch_times = {}

pf.init_potentials()

pop = evolution.loadLastestPopulation()
#population = pop["population"]
chromosome = evolution.DPEA_Part1()

map_info.initiate_maps()

pf.set_params(chromosome)


while True:
    # We only support Python 3, which means brackets around print()

#if someLoc is None and unit.location.is_on_map():
#                someLoc = unit.location.map_location()

    #print("ROUND {} STARTS".format(gc_file.gc.round()))
    
    print('pyround:', gc_file.gc.round(), 'time left:', gc_file.gc.get_time_left_ms(), 'ms')
    
    #print("My pf: {}".format(pf.pf_my_units))
    #print("Enemy pf: {}".format(pf.pf_enemy_units))

    #print(map_info.lst_of_passable_mars)

    try:
        
        units.update_units()
        #print(len(units.myWorkers))
        if gc_file.gc.planet() == bc.Planet.Earth:
            #print("EARTH!!!!!!!!!!!!!!!!!!!!!!!!!!")
            #k_earth = map_info.get_karbonite(map_info.earth)
            
            if len(units.myWorkers) < 8 and gc_file.gc.karbonite() > 16:
                #print('Not enough workers:', gc_file.gc.karbonite())
                for worker in units.myWorkers:
                    d = random.choice(directions)
                    if gc_file.gc.can_replicate(worker.id, d):
                        gc_file.gc.replicate(worker.id, d)
                        #print('replicated! ', gc_file.gc.karbonite())

            if gc_file.gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and (len(units.myFactories) < 3 or gc_file.gc.karbonite() > 300):
                d = random.choice(directions)
                for worker in units.myWorkers:
                    if gc_file.gc.can_blueprint(worker.id, bc.UnitType.Factory, d):
                        gc_file.gc.blueprint(worker.id, bc.UnitType.Factory, d)
                        break

            factoriesToHeal = []
            for factory in units.myFactories:
                x, y = factory.location.map_location().x, factory.location.map_location().y
                #print("FACTORY AT: {},{}".format(x,y))
                if factory.health < factory.max_health:
                    factoriesToHeal.append(factory)
                garrison = factory.structure_garrison()
                if len(garrison) > 0:
                    #print("Unloading Garrisoned units")
                    d = random.choice(directions)
                    if gc_file.gc.can_unload(factory.id, d):
                        gc_file.gc.unload(factory.id, d)
                        #continue
                elif gc_file.gc.can_produce_robot(factory.id, bc.UnitType.Knight):
                    #print("PRODUCING")
                    gc_file.gc.produce_robot(factory.id, bc.UnitType.Knight)
                    #continue

            if (len(units.myRockets) < 3 or gc_file.gc.karbonite() > bc.UnitType.Rocket.blueprint_cost()) and gc_file.gc.round() > 500 and gc_file.gc.round() < 726:
                d = random.choice(directions)
                for worker in units.myWorkers:
                    if gc_file.gc.can_blueprint(worker.id, bc.UnitType.Rocket, d):
                        gc_file.gc.blueprint(worker.id, bc.UnitType.Rocket, d)
                        break

            # Have workers move to
            for worker in units.myWorkers:
                location = worker.location
                #x, y = location.map_location().x, location.map_location().y
                #print("BREAK")
                #print(type(x), type(y))
                #print("{},{}".format(x,y))
                #print(worker.location.map_location())
                if not location.is_on_map():
                    # can't do anything, in garrison or rocket
                    continue
                map_location = location.map_location()

                # what to do?
                # Action: try building or repairing
                nearby = gc_file.gc.sense_nearby_units(map_location, 2)
                for other in nearby:
                    if gc_file.gc.can_build(worker.id, other.id):
                        gc_file.gc.build(worker.id, other.id)
                        # print('built a factory!')
                        # skip moving
                        continue
                    elif gc_file.gc.can_repair(worker.id, other.id):
                        gc_file.gc.repair(worker.id, other.id)
                        #print('repaired a factory!')
                        continue
                # Action: try harvesting
                try_harvest(worker)

                # where to go?
                '''
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
                        # if gc.gc.is_move_ready(worker.id) and gc.gc.can_move(worker.id, d):
                        #     gc.gc.move_robot(worker.id, d)
                
                else:  # move randomly
                    d = random.choice(directions)
                    try_move_loose(worker, d, 1)
                    # if gc.gc.is_move_ready(worker.id) and gc.gc.can_move(worker.id, d):
                    #     gc.gc.move_robot(worker.id, d)
                '''
                
                d = pf.calc_field(worker)
                #print("Directions: {}".format(directions))
                #print("D: {}".format(d))
                if gc_file.gc.is_move_ready(worker.id):
                    if gc_file.gc.can_move(worker.id, d):
                        gc_file.gc.move_robot(worker.id, d)
                else:
                    continue

            #print("FINAL: {},{}".format(x,y))
            if gc_file.gc.round() > 450 and len(units.myRockets) > 0:
                for knight in units.myKnights:
                    location = knight.location
                    if location.is_on_map():
                        #rocket_loc = rocket.location.map_location()
                        is_rocket_adjacent = gc_file.gc.sense_nearby_units_by_team(location.map_location(), 2, units.my_team)
                        for unit in is_rocket_adjacent:
                            if unit.unit_type == bc.UnitType.Rocket and gc_file.gc.can_load(unit.id, knight.id):
                                #print("WHY IS THIS NOT WORKING")
                                gc_file.gc.load(unit.id, knight.id)
                                continue
                            
                            '''
                            nearby_units = gc_file.gc.sense_nearby_units_by_team(location.map_location(), 25, units.my_team)
                            dist = []
                            for unit in nearby_units:
                                if unit.unit_type == bc.UnitType.Rocket and (len(unit.structure_garrison()) < 8):
                                    unit_loc = unit.location.map_location()
                                    d = location.map_location().direction_to(unit_loc)
                                    if gc.is_move_ready(knight.id) and gc.can_move(knight.id, d):
                                        gc.move_robot(knight.id, d)
                                        continue
                            '''


            '''
            if gc.gc.round() > 550 and len(units.myRockets) > 0:
                workers_in_rocket = 0
                for rocket in units.myRockets:
                    rocket_loc = rocket.location.map_location()
                    for dir in directions[:-1]:
                        near = rocket_loc.add(dir)
                        if gc.gc.has_unit_at_location(near):
                            nearby_unit = gc.gc.sense_unit_at_location(near)
                            if nearby_unit.unit_type == bc.UnitType.Worker:
                                if workers_in_rocket < 4:
                                    workers_in_rocket += 1
                                else:
                                    continue
                            if nearby_unit.unit_type != bc.UnitType.Factory and nearby_unit.unit_type != bc.UnitType.Rocket and gc.gc.can_load(rocket.id, nearby_unit.id):
                                gc.gc.load(rocket.id, nearby_unit.id)
                                print("Loading")
            '''
            
            if gc_file.gc.round() > 500 and len(units.myRockets) > 0:
                workers_in_rocket = 0
                for rocket in units.myRockets:
                    rocket_loc = rocket.location.map_location()
                    nearby_units = gc_file.gc.sense_nearby_units_by_team(rocket_loc, 2, units.my_team)
                    for unit in nearby_units:
                        if unit.unit_type == bc.UnitType.Worker:
                            if workers_in_rocket < 4 and gc_file.gc.can_load(rocket.id, unit.id):
                                gc_file.gc.load(rocket.id, unit.id)
                                workers_in_rocket += 1
                        elif unit.unit_type != bc.UnitType.Factory and unit.unit_type != bc.UnitType.Rocket and gc_file.gc.can_load(rocket.id, unit.id):
                            gc_file.gc.load(rocket.id, unit.id)
                        #print("Loading")
                        else:
                            continue
            

            #print("Before launch logic")
            for rocket in units.myRockets:
                if rocket.structure_is_built():
                    #print("In launch logic")
                    if rocket.id in launch_times:
                        if launch_times[rocket.id] <= gc_file.gc.round():
                            #print("launching!!!")
                            units.launch(rocket)
                            del launch_times[rocket.id]
                                
                    else:
                        if len(rocket.structure_garrison()) > 6 or (gc_file.gc.round() >= 700 and len(rocket.structure_garrison()) > 0):
                            #print("Setting launch time")
                            time = units.compute_optimal_launch_time(gc_file.gc.round())[0]
                            #if rocket.id in launch_times:
                            #if rocket.id in launch_times:
                            #    continue
                            #else:
                            #launch_times[time].append(rocket.id)
                            #else:
                            launch_times[rocket.id] = time
            #print("launch times: {}".format(launch_times))
            #print("garrison: {}".format(len(rocket.structure_garrison())))
            
            units.my_karbonite_value = gc_file.gc.manager_karbonite(units.my_team)
            units.my_units_value = ((len(units.myMages)+len(units.myHealers)+len(units.myRangers)+len(units.myKnights)) * 20) + (len(units.myFactories) * 100) + (len(units.myRockets) * 75) + (len(units.myWorkers) * 25)
            
            #units.enemy_units_value = ((len(units.enemyMages)+len(units.enemyHealers)+len(units.enemyRangers)+len(units.enemyKnights)) * 20) + (len(units.enemyFactories) * 100) + (len(units.enemyRockets) * 75) + (len(units.enemyWorkers) * 25)
            print(units.my_units_value)
            f = (10 * units.my_units_value) + units.my_karbonite_value
            evolution.DPEA_Part2(chromosome, f)
            
            '''
            if len(launch_times) > 0 :
                print("In launch logic")
                if launch_times.get(gc.gc.round()) != None:
                    print("Launching!!")
                    rocket_to_launch = launch_times.get(gc.gc.round())
                    launch(rocket_to_launch)
                    continue
                
            if len(launch_times) > 0:
                if gc.gc.round() in launch_times:
                    print("Launching!!")
                    rocket_to_launch = launch_times[gc.gc.round()]
                    launch(rocket_to_launch)
                    p = launch_times.pop(gc.gc.round(), None)
                    print("Popped time".format(p))
            '''


        else:   # Mars
            #print("HEYA")
            for rocket in units.myRockets:
                if rocket.location.is_on_map():
                    loc = rocket.location.map_location()
                    if rocket.location.is_on_planet(map_info.mars):
                        if len(rocket.structure_garrison()) > 0:  # try to unload a unit if there exists one in the garrison
                            #d = pf.calc_field(worker)
                            #gc_file.gc.move_robot(worker.id, d)
                            d = random.choice(directions)
                            if d is not None and gc_file.gc.can_unload(rocket.id, d):
                                gc_file.gc.unload(rocket.id, d)
                
            for worker in units.myWorkers:
                location = worker.location
                if location.is_on_planet(map_info.mars):
                    map_location = location.map_location()
                    try_harvest(worker)
                    d = pf.calc_field(worker)
                    if gc_file.gc.can_move(worker.id, d):
                        gc_file.gc.move_robot(worker.id, d)
                        continue
                    #d = random.choice(directions)
                    #try_move_loose(worker, d, 1)


        units.enemy_locations = []
        # sense enemies
        for unit in gc_file.gc.my_units():
            if unit.location.is_on_map():
                someLoc = unit.location.map_location()
                if someLoc is not None:
                    units.enemies = list(gc_file.gc.sense_nearby_units_by_team(someLoc, 5001, units.opponent_team))
                    #print("enemies sensed by {}: {}".format(someLoc, len(enemies)))
                    for unit in units.enemies:
                        if unit.location.is_on_map():
                            units.enemy_locations.append(unit.location.map_location())

        # moves knights around randomly
        for knight in units.myKnights:
            location = knight.location
            if location.is_on_map():
                mapLoc = location.map_location()
                nearby = gc_file.gc.sense_nearby_units(location.map_location(), 5001)
                #print("NEAR A knight: {}".format(nearby))
                for other in nearby:
                    if other.team != units.my_team and gc_file.gc.is_attack_ready(knight.id) and gc_file.gc.can_attack(knight.id, other.id):
                        #print('attacked a thing!')
                        gc_file.gc.attack(knight.id, other.id)
                        continue

                '''
                target = nearest_enemy(mapLoc)
                if target is not None:
                    if gc.gc.is_attack_ready(knight.id) and gc.gc.can_attack(knight.id, target.id):
                        #print('better attack')
                        gc.gc.attack(knight.id, target.id)
                    distance = mapLoc.distance_squared_to(target.location.map_location())
                    print("Location: {}".format(target.location.map_location()))
                    if not target.location.map_location().is_within_range(knight.attack_range(), mapLoc):
                        try_move_loose(knight, mapLoc.direction_to(target.location.map_location()), 2)
                        #elif target.location.map_location().is_within_range(knight.knight_cannot_attack_range()+1, mapLoc):
                        #try_move_loose(knight, target.location.map_location().direction_to(mapLoc), 2)

                else:
                    d = random.choice(directions)
                    if gc.gc.is_move_ready(knight.id) and gc.gc.can_move(knight.id, d):
                        gc.gc.move_robot(knight.id, d)
                '''
                    
                d = pf.calc_field(knight)
                #d = pf.calc_dir(knight, field)
                if gc_file.gc.is_move_ready(knight.id):
                    if gc_file.gc.can_move(knight.id, d):
                        gc_file.gc.move_robot(knight.id, d)
                else:
                    continue

#if gc.gc.is_over():
#print("{} is the winner!!".format(gc.gc.winning_team()))


    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    '''
    units.enemies = list(gc.gc.sense_nearby_units_by_team(someLoc, 5001, opponent_team))
        #print("enemies sensed by {}: {}".format(someLoc, len(enemies)))
        for unit in units.enemies:
            if unit.location.is_on_map():
                units.enemy_locations.append(unit.location.map_location())
    '''

    units.my_karbonite_value = gc_file.gc.manager_karbonite(units.my_team)
    units.my_units_value = ((len(units.myMages)+len(units.myHealers)+len(units.myRangers)+len(units.myKnights)) * 20) + (len(units.myFactories) * 100) + (len(units.myRockets) * 75) + (len(units.myWorkers) * 25)


    for enemy in units.enemies:
        if enemy.unit_type == bc.UnitType.Factory:
            units.enemyFactories.append(unit)
        elif enemy.unit_type == bc.UnitType.Worker:
            units.enemyFactories.append(unit)
        elif enemy.unit_type == bc.UnitType.Mage:
            units.enemyFactories.append(unit)
        elif enemy.unit_type == bc.UnitType.Knight:
            units.enemyFactories.append(unit)
        elif enemy.unit_type == bc.UnitType.Ranger:
            units.enemyFactories.append(unit)
        elif enemy.unit_type == bc.UnitType.Rocket:
            units.enemyFactories.append(unit)
        elif enemy.unit_type == bc.UnitType.Healer:
            units.enemyFactories.append(unit)
        else:
            print("ERROR: Unknown unit type ", unit)


    karbonite_value = gc_file.gc.manager_karbonite(units.my_team)
    units_value = ((len(units.myMages)+len(units.myHealers)+len(units.myRangers)+len(units.myKnights)) * 20) + (len(units.myFactories) * 100) + (len(units.myRockets) * 75) + (len(units.myWorkers) * 25)

    # send the actions we've performed, and wait for our next turn.
    
    units.myFactories = []
    units.myWorkers = []
    units.myHealers = []
    units.myRangers = []
    units.myMages = []
    units.myKnights = []
    units.myRockets = []
    
    gc_file.gc.next_turn()

#print("karbonite: {}".format(karbonite_value))
#    print("units: {}".format(units_value))

#if gc.gc.round() == 749:
#print("In here")
#if gc.gc.is_over():
#        print("{} is the winner!!".format(gc.gc.winning_team()))

#print("My units: {} round: {}".format(len(myMages)+len(myHealers)+len(myRangers)+len(myKnights)+len(myFactories)+len(myRockets)+len(myWorkers), gc.gc.round()))
    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()

