import json
import numpy as np

np.set_printoptions(threshold=np.inf)
np.set_printoptions(linewidth=6000)
import collections
from GameInitialization import bc
from GameInitialization import game_controller
import config
import time
import heapq

gc = game_controller.gc
tryRotate = [0, -1, 1, -2, 2]
directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South,
              bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]

allDirections = list(bc.Direction)  # includes center, and is weirdly ordered


class ProcessMap():
    def __init__(self):

        self.game_map = gc.starting_map(gc.planet())
        self.game_map = self.game_map.to_json()
        self.game_map = json.loads(self.game_map)
        self.initial_karbonite = self.game_map["initial_karbonite"]
        self.passable_terrain = self.game_map['is_passable_terrain']

        self.mars_map = gc.starting_map(bc.Planet.Mars)
        self.mars_map = self.mars_map.to_json()
        self.mars_map = json.loads(self.mars_map)
        self.mars_passable_terrain = self.mars_map['is_passable_terrain']
        self.mars_terrain_array = np.asanyarray(self.mars_passable_terrain)
        self.mars_terrain_array = np.where([self.mars_terrain_array == True], [0], [-1])
        self.mars_terrain_array = np.fliplr(np.squeeze(self.mars_terrain_array, 0))

        self.karbonite_array = np.fliplr(np.asanyarray(self.initial_karbonite))
        self.terrain_array = np.asanyarray(self.passable_terrain)
        self.terrain_array = np.where([self.terrain_array == True], [0], [-1])
        self.terrain_array = np.fliplr(np.squeeze(self.terrain_array, 0))
        self.terrain_composite = np.add(self.karbonite_array, self.terrain_array)

        self.planet_y = np.size(self.terrain_array, 0)
        self.planet_x = np.size(self.terrain_array, 1)
        self.planet_total_starting_karbonite = np.sum(np.where(self.karbonite_array > 0))

        if gc.planet() == bc.Planet.Earth:

            self.root_sector_1 = bc.MapLocation(bc.Planet.Earth, 0, 0)
            self.root_sector_2 = bc.MapLocation(bc.Planet.Earth, 0, self.planet_y - 1)
            self.root_sector_3 = bc.MapLocation(bc.Planet.Earth, self.planet_x - 1, 0)
            self.root_sector_4 = bc.MapLocation(bc.Planet.Earth, self.planet_x - 1, self.planet_y - 1)
            self.root_sector_5 = bc.MapLocation(bc.Planet.Earth, int((self.planet_x - 1) / 2),
                                                int((self.planet_y - 1) / 2))
        else:
            self.root_sector_1 = bc.MapLocation(bc.Planet.Mars, 0, 0)
            self.root_sector_2 = bc.MapLocation(bc.Planet.Mars, 0, self.planet_y - 1)
            self.root_sector_3 = bc.MapLocation(bc.Planet.Mars, self.planet_x - 1, 0)
            self.root_sector_4 = bc.MapLocation(bc.Planet.Mars, self.planet_x - 1, self.planet_y - 1)
            self.root_sector_5 = bc.MapLocation(bc.Planet.Mars, int((self.planet_x - 1) / 2),
                                                int((self.planet_y - 1) / 2))

        self.sector_maps = {}
        for sector in range(1, 6):
            self.sector_maps["sector_" + str(sector)] = np.copy(self.terrain_array)

        if gc.planet() == bc.Planet.Earth:
            self.initial_units = self.game_map['initial_units']
            self.starting_units = len(self.game_map['initial_units'])
            self.initial_units_array_Red = []
            self.initial_units_array_Blue = []
            for starting_unit in range(0, self.starting_units):
                if self.game_map['initial_units'][starting_unit]['team'] == 'Red':
                    self.initial_units_array_Red.append(self.game_map['initial_units'][starting_unit]['location'])
                else:
                    self.initial_units_array_Blue.append(self.game_map['initial_units'][starting_unit]['location'])

    def sector_breadth_first_search(self):
        tick = time.clock()
        self.root_sector_1 = Pathing(self.sector_maps['sector_1']).search_pattern(self.root_sector_1)
        config.sector_1 = Pathing(self.sector_maps['sector_1']).breadth_first_search_1(
            self.root_sector_1)

        self.root_sector_2 = Pathing(self.sector_maps['sector_2']).search_pattern(self.root_sector_2)
        config.sector_2 = Pathing(self.sector_maps['sector_2']).breadth_first_search_1(
            self.root_sector_2)

        self.root_sector_3 = Pathing(self.sector_maps['sector_3']).search_pattern(self.root_sector_3)
        config.sector_3 = Pathing(self.sector_maps['sector_3']).breadth_first_search_1(
            self.root_sector_3)

        self.root_sector_4 = Pathing(self.sector_maps['sector_4']).search_pattern(self.root_sector_4)
        config.sector_4 = Pathing(self.sector_maps['sector_4']).breadth_first_search_1(
            self.root_sector_4)

        self.root_sector_5 = Pathing(self.sector_maps['sector_5']).search_pattern(self.root_sector_5)
        config.sector_5 = Pathing(self.sector_maps['sector_5']).breadth_first_search_1(
            self.root_sector_5)

        tock = time.clock()
        print("Initial BFS", (tick - tock) * 1000, "ms")

    def sector_aStar_search(self):
        self.root_sector_1 = Pathing(self.sector_maps['sector_1']).search_pattern(self.root_sector_1)
        config.sector_AS = Pathing(np.copy(self.terrain_array)).a_star_search(
            self.root_sector_1, self.root_sector_5)


class Pathing:

    def __init__(self, grid_orig):
        self.grid = np.copy(grid_orig)

    def in_bounds(self, id):
        [y, x] = id
        return 0 <= x < np.size(self.grid, 1) and 0 <= y < np.size(self.grid, 0)

    def passable(self, id):
        [y, x] = id
        if self.grid[y, x] < 0:
            return False
        else:
            return True

    def passable_as(self, id):
        [y, x] = id
        if self.grid[y, x] <= 0:
            return False
        else:
            return True

    def neighbors(self, id):
        [y, x] = id
        results = [(y, x + 1), (y - 1, x), (y, x - 1), (y + 1, x), (y + 1, x + 1), (y - 1, x - 1), (y - 1, x + 1),
                   (y + 1, x - 1)]
        results = list(filter(self.in_bounds, results))
        results = list(filter(self.passable, results))
        return results

    def neighbors_search_pattern(self, id):
        [y, x] = id
        results = [(y, x + 1), (y - 1, x), (y, x - 1), (y + 1, x), (y + 1, x + 1), (y - 1, x - 1), (y - 1, x + 1),
                   (y + 1, x - 1)]
        results = list(filter(self.in_bounds, results))
        return results

    def heuristic(self, goal, next):
        (x1, y1) = goal
        (x2, y2) = next
        return abs(x1 - x2) + abs(y1 - y2)

    def direction_from(self, current_node, next_node):
        cy, cx = current_node
        ny, nx = next_node

        if ny == cy - 1 and nx == cx + 0:
            return 5
        if ny == cy - 1 and nx == cx + 1:
            return 6
        if ny == cy + 0 and nx == cx + 1:
            return 7
        if ny == cy + 1 and nx == cx + 1:
            return 8
        if ny == cy + 1 and nx == cx + 0:
            return 1
        if ny == cy + 1 and nx == cx - 1:
            return 2
        if ny == cy + 0 and nx == cx + -1:
            return 3
        if ny == cy - 1 and nx == cx - 1:
            return 4
        if ny == cy - 0 and nx == cx + 0:
            return 0
        else:
            return self.came_from[cy, cx]

    def breadth_first_search_1(self, start):

        self.visited = np.copy(self.grid)
        self.came_from = np.copy(self.grid)
        self.cost_so_far = np.copy(self.grid)
        self.distance = np.copy(self.grid)
        start = trans_coord_to_np_new(start)

        frontier = Queue()
        frontier.put(start)

        self.visited[start] = 0
        self.came_from[start] = 0
        self.visited[start] = 1

        while not frontier.empty():
            current = frontier.get()
            for next in self.neighbors(current):
                if self.visited[next] != 1:
                    frontier.put(next)
                    self.visited[next] = 1

                    self.came_from[next] = self.direction_from(current, next)
        return self.came_from

    def nav_next_move(self, map, unit_id):
        start = gc.unit(unit_id).location.map_location()
        start = trans_coord_to_np(start)
        direction_to_move = map[start[0], start[1]] - 1
        return directions[direction_to_move]

    def search_pattern(self, start):
        self.visited = np.copy(self.grid)
        start = trans_coord_to_np(start)
        start = (start[0], start[1])
        frontier = Queue()
        frontier.put(start)
        if self.visited[start] == 0:
            # print("Found Solution", start)
            return trans_coord_to_ml(start[0], start[1])
        self.visited[start] = 1
        while not frontier.empty():
            current = frontier.get()
            # print(current)
            for next in self.neighbors_search_pattern(current):
                y, x = next
                if self.visited[next] == 0:
                    # print("found solution", y, x)
                    return trans_coord_to_ml(next[0], next[1])
                if self.visited[next] != 1:
                    frontier.put(next)
                    self.visited[next] = 1

    def a_star_search(self, start, goal):
        tick = time.clock()
        self.gridA = np.copy(self.grid)
        self.visitedA = np.copy(self.grid)
        self.came_fromA = np.copy(self.grid)
        self.cost_so_farA = np.copy(self.grid)
        self.distanceA = np.copy(self.grid)

        start = trans_coord_to_np_new(start)
        goal = trans_coord_to_np_new(goal)
        # print(goal,"goal")
        # print(start,"start")

        frontier = PriorityQueue()
        frontier.put(goal, 0)

        self.came_fromA[goal] = 0
        self.cost_so_farA[goal] = 0
        self.visitedA[goal] = 1

        while not frontier.empty():
            current = frontier.get()
            if current == start:
                self.cost_so_farA[current] = self.cost_so_farA[current] + 1
                break

            for next in self.neighbors(current):
                new_cost = self.cost_so_farA[current] + 1
                if self.visitedA[next] != 1 or new_cost < self.cost_so_farA[next]:
                    # if self.cost_so_farA[next] ==0 or new_cost < self.cost_so_farA[next]:
                    self.cost_so_farA[next] = new_cost
                    priority = new_cost + self.heuristic(start, next)
                    frontier.put(next, priority)
                    self.visitedA[next] = 1
                    self.came_fromA[next] = self.direction_from(current, next)
        tock = time.clock()
        # print("Astar Exec Time", (tick - tock) * 1000, "ms")

        return self.came_fromA


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Queue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self):
        return len(self.elements) == 0

    def empty_que(self):
        return self.elements.clear()

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()

    def peek(self):
        return self.elements.copy()

    def __len__(self):
        return len(self.elements)


def fuzzygoto(unit_id, dest):
    if gc.unit(unit_id).location.map_location() == dest or gc.unit(unit_id).movement_heat() >= 10: return
    toward = gc.unit(unit_id).location.map_location().direction_to(dest)
    for tilt in tryRotate:
        d = rotate(toward, tilt)
        newLoc = gc.unit(unit_id).location.map_location().add(d)
        if newLoc.x <= config.planet_map.planet_x and newLoc.y <= config.planet_map.planet_y:
            if gc.can_move(unit_id, d) and gc.unit(unit_id).movement_heat() < 10:  # d
                gc.move_robot(unit_id, d)


def rotate(dir, amount):
    ind = directions.index(dir)
    # print("DIRECTION", directions[(ind + amount) % 8])
    return directions[(ind + amount) % 8]


def random_dir():
    amount = np.random.randint(0, 7)
    # print("random dir", directions[amount % 8])
    return directions[amount % 8]


def trans_coord_to_np(maplocation):
    mp1 = maplocation
    np_x = mp1.x
    np_y = config.planet_map.planet_y - mp1.y - 1
    return [np_y, np_x]


def trans_coord_to_np_new(maplocation):
    mp1 = maplocation
    np_x = mp1.x
    np_y = config.planet_map.planet_y - mp1.y - 1
    return np_y, np_x


def trans_coord_to_ml(np_y, np_x):
    this_planet = gc.planet()
    y = config.planet_map.planet_y - np_y - 1
    x = np_x
    if this_planet == bc.Planet.Earth:
        retuned_ml = bc.MapLocation(bc.Planet.Earth, x, y)
    else:
        retuned_ml = bc.MapLocation(bc.Planet.Mars, x, y)
    return retuned_ml


def pick_random_landing_location():
    mars_map = config.planet_map.mars_terrain_array
    print(mars_map)
    mars_x = np.size(mars_map, 1)
    mars_y = np.size(mars_map, 0)
    for i in range(mars_x * mars_y):
        my = np.random.randint(0, mars_y)
        mx = np.random.randint(0, mars_x)
        if mars_map[my, mx] == 0:
            return bc.MapLocation(bc.Planet.Mars, mx, my)


def fuzzy_destination(unit_id, destination):
    distance = gc.unit(unit_id).location.map_location().distance_squared_to(destination)
    max_distance = int(np.sqrt(distance))

    dir_to_destination = gc.unit(unit_id).location.map_location().direction_to(destination)

    if max_distance <= 1:
        destination = gc.unit(unit_id).location.map_location()
        return destination

    for search_range in range(12, max_distance, 4):
        np_test = trans_coord_to_np(
            gc.unit(unit_id).location.map_location().add_multiple(dir_to_destination, search_range))
        npy, npx = np_test

        for y_adj in range(-2, 3, 1):
            for x_adj in range(-2, 3, 1):
                npyt = npy + y_adj
                npxt = npx + x_adj

                if 0 <= npxt < np.size(config.terra_map, 1) and 0 <= npyt < np.size(config.terra_map, 0):

                    if config.terra_map[npyt, npxt] == 0:
                        destination = trans_coord_to_ml(npyt, npxt)

                        return destination
    return destination


def in_bounds(self, grid):
    [y, x] = id
    return 0 <= x < np.size(self.grid, 1) and 0 <= y < np.size(self.grid, 0)


def a_star_move(unit_id, loc):
    check_loc = trans_coord_to_np_new(loc)
    came_from = config.planet_pathing.a_star_search(gc.unit(unit_id).location.map_location(), loc)
    next = config.planet_pathing.nav_next_move(came_from, unit_id)
    nextLoc = gc.unit(unit_id).location.map_location().add(next)
    test_loc = trans_coord_to_np_new(nextLoc)

    if config.planet_map.terrain_array[test_loc[0], test_loc[1]] == -1:
        config.planet_map.terrain_array[check_loc[0], check_loc[1]] = -1
        config.planet_pathing.grid[check_loc[0], check_loc[1]] = -1
        config.karbonite_map[check_loc[0], check_loc[1]] = -1
        return

    fuzzygoto(gc.unit(unit_id).id, nextLoc)
