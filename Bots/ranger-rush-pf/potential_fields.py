import battlecode as bc
import random
import sys
import traceback
import map_info
import evolution
import gc_file
import copy
import math
import units

'''
earth_map = gc.gc.gc.gc.starting_map(bc.Planet.Earth)
earth_width = earth_map.width
earth_height = earth_map.height

mars_map = gc.gc.starting_map(bc.Planet.Mars)
mars_width = mars_map.width
mars_height = mars_map.height
'''

#gc.gc = bc.GameController()
directions = list(bc.Direction)

pf_my_units = {"worker": {}, "ranger": {}}#, "ranger": {}, "mage": {}, "healer": {}}

pf_enemy_units = {"worker": {}, "ranger": {}}#, "ranger": {}, "mage": {}, "healer": {}}

pf_karbonite = {"worker": {}}

potentials_earth = []
potentials_mars = []

temp_pf = []
#temp_pf_enemy = []


def init_potentials():
    for x in range(map_info.earth_width):
        p = []
        for y in range(map_info.earth_height):
            p.append(0)
        potentials_earth.append(p)

    for x in range(map_info.mars_width):
        p = []
        for y in range(map_info.mars_height):
            p.append(0)
        potentials_mars.append(p)

    for x in range(map_info.earth_width):
        for y in range(map_info.earth_height):
            if (x,y) in map_info.lst_of_impassable_earth:
                potentials_earth[x][y] = -100
            else:
                potentials_earth[x][y] = 0

    for x in range(map_info.mars_width):
        for y in range(map_info.mars_height):
            if (x,y) in map_info.lst_of_impassable_mars:
                potentials_mars[x][y] = -100
            else:
                potentials_mars[x][y] = 0



    '''
    for x in range(earth_width):
        for y in range(earth_height):
            coords = (x, y)
            if x == -1 or y == -1 or x == earth_map.width or y == earth_map.height:
                passable_locations_earth[coords] = False
            elif earth_map.is_passable_terrain_at(bc.MapLocation(earth, x, y)):
                passable_locations_earth[coords] = True
            else:
                passable_locations_earth[coords] = False

    lst_of_passable_earth = [loc for loc in passable_locations_earth if passable_locations_earth[loc]]
    lst_of_impassable_earth = [loc for loc in passable_locations_earth if not passable_locations_earth[loc]]
    #print("EARTH: {}".format(lst_of_impassable_earth))


    mars_map = gc.gc.starting_map(bc.Planet.Mars)
    mars_width = mars_map.width
    mars_height = mars_map.height

    passable_locations_mars = {}

    for x in range(mars_width):
        for y in range(mars_height):
            coords = (x, y)
            if x == -1 or y == -1 or x == mars_map.width or y == mars_map.height:
                passable_locations_mars[coords] = False
            elif mars_map.is_passable_terrain_at(bc.MapLocation(mars, x, y)):
                passable_locations_mars[coords] = True
            else:
                passable_locations_mars[coords] = False

    lst_of_passable_mars = [loc for loc in passable_locations_mars if passable_locations_mars[loc]]
    lst_of_impassable_mars = [loc for loc in passable_locations_mars if not passable_locations_mars[loc]]
    #print("MARS: {}".format(lst_of_impassable_mars))
    '''


    for coords in map_info.lst_of_impassable_earth:
        for x in range(map_info.earth_width):
            for y in range(map_info.earth_height):
                if potentials_earth[x][y] != -100:
                    d = ((coords[0] - x) ** 2 + (coords[1] - y) ** 2)
                    if d <= 25 and d != 0:
                        v = -80/(abs(coords[0] - x) + abs(coords[1] - y)) ** 2
                        if v < potentials_earth[x][y]:
                            potentials_earth[x][y] = v

    for coords in map_info.lst_of_impassable_mars:
        for x in range(map_info.mars_width):
            for y in range(map_info.mars_height):
                if potentials_mars[x][y] != -100:
                    d = ((coords[0] - x) ** 2 + (coords[1] - y) ** 2)
                    if d <= 25 and d != 0:
                        v = -80/(abs(coords[0] - x) + abs(coords[1] - y)) ** 2
                        if v < potentials_mars[x][y]:
                            potentials_mars[x][y] = v


    for x in range(1, map_info.earth_width-1):
        for y in range(1, map_info.earth_height-1):
            if potentials_earth[x][y] != -100:
                if potentials_earth[x][y] > potentials_earth[x+1][y+1] and potentials_earth[x][y] > potentials_earth[x-1][y-1]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x-1][y+1] and potentials_earth[x][y] > potentials_earth[x+1][y-1]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x+1][y] and potentials_earth[x][y] > potentials_earth[x-1][y]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x-1][y+1] and potentials_earth[x][y] > potentials_earth[x][y-1]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x-1][y] and potentials_earth[x][y] > potentials_earth[x][y+1]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x-1][y] and potentials_earth[x][y] > potentials_earth[x][y-1]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x+1][y] and potentials_earth[x][y] > potentials_earth[x][y-1]:
                    potentials_earth[x][y] = -10
                elif potentials_earth[x][y] > potentials_earth[x+1][y] and potentials_earth[x][y] > potentials_earth[x][y+1]:
                    potentials_earth[x][y] = -10
                else:
                    continue


    for x in range(1, map_info.mars_width-1):
        for y in range(1, map_info.mars_height-1):
            if potentials_mars[x][y] != -100:
                if potentials_mars[x][y] > potentials_mars[x+1][y+1] and potentials_mars[x][y] > potentials_mars[x-1][y-1]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x-1][y+1] and potentials_mars[x][y] > potentials_mars[x+1][y-1]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x+1][y] and potentials_mars[x][y] > potentials_mars[x-1][y]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x-1][y+1] and potentials_mars[x][y] > potentials_mars[x][y-1]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x-1][y] and potentials_mars[x][y] > potentials_mars[x][y+1]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x-1][y] and potentials_mars[x][y] > potentials_mars[x][y-1]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x+1][y] and potentials_mars[x][y] > potentials_mars[x][y-1]:
                    potentials_mars[x][y] = -10
                elif potentials_mars[x][y] > potentials_mars[x+1][y] and potentials_mars[x][y] > potentials_mars[x][y+1]:
                    potentials_mars[x][y] = -10
                else:
                    continue
    '''
    temp_pf = copy.deepcopy(potentials_earth)
    temp_pf_enemy = copy.deepcopy(potentials_earth)
    '''

    for x in range(0, map_info.earth_width):
        t = []
        for y in range(0, map_info.earth_height):
            t.append(potentials_earth[x][y])
            
            temp_pf.append(t)
    #temp_pf_enemy.append(t)


def set_params(chromosome):
    #pop = evolution.loadLatestPopulation()
    #population = pop["population"]
    ww_c, ww_e, ww_k, wk_c, wk_e, wk_k, wf_c, wf_e, wf_k, wro_c, wro_e, wro_k, kw_c, kw_e, kw_k, kk_c, kk_e, kk_k, kf_c, kf_e, kf_k, kro_c, kro_e, kro_k, wew_c, wew_e, wew_k, wek_c, wek_e, wek_k, wer_c, wer_e, wer_k, wem_c, wem_e, wem_k, weh_c, weh_e, weh_k, wef_c, wef_e, wef_k, wero_c, wero_e, wero_k, kew_c, kew_e, kew_k, kek_c, kek_e, kek_k, ker_c, ker_e, ker_k, kem_c, kem_e, kem_k, keh_c, keh_e, keh_k, kef_c, kef_e, kef_k, kero_c, kero_e, kero_k, kbw_c, kbw_e, kbw_k = chromosome#69 values

    ''' wr_c, wr_e, wr_k, wm_c, wm_e, wm_k, wh_c, wh_e, wh_k,''' #after wk_k
    '''kr_c, kr_e, kr_k, km_c, km_e, km_k, kh_c, kh_e, kh_k, '''
    '''rw_c, rw_e, rw_k, rk_c, rk_e, rk_k, rr_c, rr_e, rr_k, rm_c, rm_e, rm_k, rh_c, rh_e, rh_k, rf_c, rf_e, rf_k, rro_c, rro_e, rro_k, mw_c, mw_e, mw_k, mk_c, mk_e, mk_k, mr_c, mr_e, mr_k, mm_c, mm_e, mm_k, mh_c, mh_e, mh_k, mf_c, mf_e, mf_k, mro_c, mro_e, mro_k, hw_c, hw_e, hw_k, hk_c, hk_e, hk_k, hr_c, hr_e, hr_k, hm_c, hm_e, hm_k, hh_c, hh_e, hh_k, hf_c, hf_e, hf_k, hro_c, hro_e, hro_k, '''
    '''rew_c, rew_e, rew_k, rek_c, rek_e, rek_k, rer_c, rer_e, rer_k, rem_c, rem_e, rem_k, reh_c, reh_e, reh_k, ref_c, ref_e, ref_k, rero_c, rero_e, rero_k, mew_c, mew_e, mew_k, mek_c, mek_e, mek_k, mer_c, mer_e, mer_k, mem_c, mem_e, mem_k, meh_c, meh_e, meh_k, mef_c, mef_e, mef_k, mero_c, mero_e, mero_k, hew_c, hew_e, hew_k, hek_c, hek_e, hek_k, her_c, her_e, her_k, hem_c, hem_e, hem_k, heh_c, heh_e, heh_k, hef_c, hef_e, hef_k, hero_c, hero_e, hero_k, '''#213 after this

    pf_my_units["worker"] = {}
    pf_my_units["ranger"] = {}
    '''    pf_my_units["ranger"] = {}
    pf_my_units["mage"] = {}
    pf_my_units["healer"] = {}'''
    
    pf_my_units["worker"]["worker"] = (ww_c, ww_e, ww_k)
    pf_my_units["worker"]["ranger"] = (wk_c, wk_e, wk_k)
    '''    pf_my_units["worker"]["ranger"] = (wr_c, wr_e, wr_k)
    pf_my_units["worker"]["mage"] = (wm_c, wm_e, wm_k)
    pf_my_units["worker"]["healer"] = (wh_c, wh_e, wh_k)'''
    pf_my_units["worker"]["factory"] = (wf_c, wf_e, wf_k)
    pf_my_units["worker"]["rocket"] = (wro_c, wro_e, wro_k)

    pf_my_units["ranger"]["worker"] = (kw_c, kw_e, kw_k)
    pf_my_units["ranger"]["ranger"] = (kk_c, kk_e, kk_k)
    '''    pf_my_units["knight"]["ranger"] = (kr_c, kr_e, kr_k)
    pf_my_units["knight"]["mage"] = (km_c, km_e, km_k)
    pf_my_units["knight"]["healer"] = (kh_c, kh_e, kh_k)'''
    pf_my_units["ranger"]["factory"] = (kf_c, kf_e, kf_k)
    pf_my_units["ranger"]["rocket"] = (kro_c, kro_e, kro_k)

    '''    pf_my_units["ranger"]["worker"] = (rw_c, rw_e, rw_k)
    pf_my_units["ranger"]["knight"] = (rk_c, rk_e, rk_k)
    pf_my_units["ranger"]["ranger"] = (rr_c, rr_e, rr_k)
    pf_my_units["ranger"]["mage"] = (rm_c, rm_e, rm_k)
    pf_my_units["ranger"]["healer"] = (rh_c, rh_e, rh_k)
    pf_my_units["ranger"]["factory"] = (rf_c, rf_e, rf_k)
    pf_my_units["ranger"]["rocket"] = (rro_c, rro_e, rro_k)
    
    pf_my_units["mage"]["worker"] = (mw_c, mw_e, mw_k)
    pf_my_units["mage"]["knight"] = (mk_c, mk_e, mk_k)
    pf_my_units["mage"]["ranger"] = (mr_c, mr_e, mr_k)
    pf_my_units["mage"]["mage"] = (mm_c, mm_e, mm_k)
    pf_my_units["mage"]["healer"] = (mh_c, mh_e, mh_k)
    pf_my_units["mage"]["factory"] = (mf_c, mf_e, mf_k)
    pf_my_units["mage"]["rocket"] = (mro_c, mro_e, mro_k)
    
    pf_my_units["healer"]["worker"] = (hw_c, hw_e, hw_k)
    pf_my_units["healer"]["knight"] = (hk_c, hk_e, hk_k)
    pf_my_units["healer"]["ranger"] = (hr_c, hr_e, hr_k)
    pf_my_units["healer"]["mage"] = (hm_c, hm_e, hm_k)
    pf_my_units["healer"]["healer"] = (hh_c, hh_e, hh_k)
    pf_my_units["healer"]["factory"] = (hf_c, hf_e, hf_k)
    pf_my_units["healer"]["rocket"] = (hro_c, hro_e, hro_k)'''



    pf_enemy_units["worker"] = {}
    pf_enemy_units["ranger"] = {}
    '''    pf_enemy_units["ranger"] = {}
    pf_enemy_units["mage"] = {}
    pf_enemy_units["healer"] = {}'''

    pf_enemy_units["worker"]["worker"] = (wew_c, wew_e, wew_k)
    pf_enemy_units["worker"]["knight"] = (wek_c, wek_e, wek_k)
    '''    pf_enemy_units["worker"]["ranger"] = (wer_c, wer_e, wer_k)
    pf_enemy_units["worker"]["mage"] = (wem_c, wem_e, wem_k)
    pf_enemy_units["worker"]["healer"] = (weh_c, weh_e, weh_k)'''
    pf_enemy_units["worker"]["factory"] = (wef_c, wef_e, wef_k)
    pf_enemy_units["worker"]["rocket"] = (wero_c, wero_e, wero_k)

    pf_enemy_units["ranger"]["worker"] = (kew_c, kew_e, kew_k)
    pf_enemy_units["ranger"]["knight"] = (kek_c, kek_e, kek_k)
    '''    pf_enemy_units["knight"]["ranger"] = (ker_c, ker_e, ker_k)
    pf_enemy_units["knight"]["mage"] = (kem_c, kem_e, kem_k)
    pf_enemy_units["knight"]["healer"] = (keh_c, keh_e, keh_k)'''
    pf_enemy_units["ranger"]["factory"] = (kef_c, kef_e, kef_k)
    pf_enemy_units["ranger"]["rocket"] = (kero_c, kero_e, kero_k)
    
    '''    pf_enemy_units["ranger"]["worker"] = (rew_c, rew_e, rew_k)
    pf_enemy_units["ranger"]["knight"] = (rek_c, rek_e, rek_k)
    pf_enemy_units["ranger"]["ranger"] = (rer_c, rer_e, rer_k)
    pf_enemy_units["ranger"]["mage"] = (rem_c, rem_e, rem_k)
    pf_enemy_units["ranger"]["healer"] = (reh_c, reh_e, reh_k)
    pf_enemy_units["ranger"]["factory"] = (ref_c, ref_e, ref_k)
    pf_enemy_units["ranger"]["rocket"] = (rero_c, rero_e, rero_k)

    pf_enemy_units["mage"]["worker"] = (mew_c, mew_e, mew_k)
    pf_enemy_units["mage"]["knight"] = (mek_c, mek_e, mek_k)
    pf_enemy_units["mage"]["ranger"] = (mer_c, mer_e, mer_k)
    pf_enemy_units["mage"]["mage"] = (mem_c, mem_e, mem_k)
    pf_enemy_units["mage"]["healer"] = (meh_c, meh_e, meh_k)
    pf_enemy_units["mage"]["factory"] = (mef_c, mef_e, mef_k)
    pf_enemy_units["mage"]["rocket"] = (mero_c, mero_e, mero_k)
    
    pf_enemy_units["healer"]["worker"] = (hew_c, hew_e, hew_k)
    pf_enemy_units["healer"]["knight"] = (hek_c, hek_e, hek_k)
    pf_enemy_units["healer"]["ranger"] = (her_c, her_e, her_k)
    pf_enemy_units["healer"]["mage"] = (hem_c, hem_e, hem_k)
    pf_enemy_units["healer"]["healer"] = (heh_c, heh_e, heh_k)
    pf_enemy_units["healer"]["factory"] = (hef_c, hef_e, hef_k)
    pf_enemy_units["healer"]["rocket"] = (hero_c, hero_e, hero_k)'''

    pf_karbonite["worker"] = (kbw_c, kbw_e, kbw_k)

    '''
    pf_my_units = {                                                                                                                                                     "worker": {"worker":(ww_c, ww_e, ww_k), "knight":(wk_c, wk_e, wk_k), "ranger":(wr_c, wr_e, wr_k), "mage":(wm_c, wm_e, wm_k), "healer":(wh_c, wh_e, wh_k), "factory":(wf_c, wf_e, wf_k), "rocket":(wro_c, wro_e, wro_k)},                                                                                                                          "knight": {"worker":(kw_c, kw_e, kw_k), "knight":(kk_c, kk_e, kk_k), "ranger":(kr_c, kr_e, kr_k), "mage":(km_c, km_e, km_k), "healer":(kh_c, kh_e, kh_k), "rocket":(kro_c, kro_e, kro_k)},                                                                                                                           "ranger": {"worker":(rw_c, rw_e, rw_k), "knight":(rk_c, rk_e, rk_k), "ranger":(rr_c, rr_e, rr_k), "mage":(rm_c, rm_e, rm_k), "healer":(rh_c, rh_e, rh_k), "rocket":(rro_c, rro_e, rro_k)},                                                                                                                             "mage": {"worker":(mw_c, mw_e, mw_k), "knight":(mk_c, mk_e, mk_k), "ranger":(mr_c, mr_e, mr_k), "mage":(mm_c, mm_e, mm_k), "healer":(mh_c, mh_e, mh_k), "rocket":(mro_c, mro_e, mro_k)},                                                                                                                           "healer": {"worker":(hw_c, hw_e, hw_k), "knight":(hk_c, hk_e, hk_k), "ranger":(hr_c, hr_e, hr_k), "mage":(hm_c, hm_e, hm_k), "healer":(hh_c, hh_e, hh_k), "rocket":(hro_c, hro_e, hro_k)}                                                                                                                                }

    pf_enemy_units = {                                                                                                                                                  "worker": {"worker":(wew_c, wew_e, wew_k), "knight":(wek_c, wek_e, wek_k), "ranger":(wer_c, wer_e, wer_k), "mage":(wem_c, wem_e, wem_k), "healer":(weh_c,                               weh_e, weh_k)},                                                                                                                                           "knight": {"worker":(kew_c, kew_e, kew_k), "knight":(kek_c, kek_e, kek_k), "ranger":(ker_c, ker_e, ker_k), "mage":(kem_c, kem_e, kem_k), "healer":(keh_c, keh_e, keh_k), "factory":(kef_c, kef_e, kef_k), "rocket":(kero_c, kero_e, kero_k)},                                                                                                                                       "ranger": {"worker":(rew_c, rew_e, rew_k), "knight":(rek_c, rek_e, rek_k), "ranger":(rer_c, rer_e, rer_k), "mage":(rem_c, rem_e, rem_k), "healer":(reh_c, reh_e, reh_k), "factory":(ref_c, ref_e, ref_k), "rocket":(rero_c, rero_e, rero_k)},                                                                                                                                           "mage": {"worker":(mew_c, mew_e, mew_k), "knight":(mek_c, mek_e, mek_k), "ranger":(mer_c, mer_e, mer_k), "mage":(mem_c, mem_e, mem_k), "healer":(meh_c, meh_e, meh_k), "factory":(mef_c, mef_e, mef_k), "rocket":(mero_c, mero_e, mero_k)},                                                                                                                                         "healer": {"worker":(hew_c, hew_e, hew_k), "knight":(hek_c, hek_e, hek_k), "ranger":(her_c, her_e, her_k), "mage":(hem_c, hem_e, hem_k), "healer":(heh_c, heh_e, heh_k)}                                                                                                                                                }
    
    pf_karbonite = {"worker": (kbw_c, kbw_e, kbw_k)}
    '''

    #print("My pf: {}".format(pf_my_units))
    #print("Enemy pf: {}".format(pf_enemy_units))

def get_f(curr_robot, curr_type, other_robot, other_type):
    #print("{} -> {}".format(curr_type, other_type))
    
    '''
    if curr_type in pf_my_units:
        print("KEY1 EXISTS")
    if other_type in pf_my_units.get(curr_type):
        print("KEY2 EXISTS")
    '''
    
    c,e,k = pf_my_units[curr_type][other_type]
    #print("Earth: {}".format(map_info.earth_height))
    #print("Temp: {}".format(temp_pf))
    #for x in range(map_info.earth_width):
    #    for y in range(map_info.earth_height):
    curr_x, curr_y = curr_robot.location.map_location().x, curr_robot.location.map_location().y
    for x in [curr_x - 1, curr_x, curr_x + 1]:
        for y in [curr_y - 1, curr_y, curr_y + 1]:
            if x == curr_x and y == curr_y:
                continue
            if x not in range(map_info.earth_width):
                continue
            if y not in range(map_info.earth_height):
                continue
            #print(other_robot.location.map_location())
            d = ((other_robot.location.map_location().x - x) ** 2) + ((other_robot.location.map_location().y - y) ** 2)
            f = k * (math.exp(-((d-c)**2)/(2*(e**2)))) / (math.sqrt(2*3.14*(e**2)))
            if f > temp_pf[x][y] and temp_pf[x][y] != -100:
                temp_pf[x][y] += f

    return temp_pf


def get_f_enemy(curr_robot, curr_type, other_robot, other_type):
    c,e,k = pf_enemy_units[curr_type][other_type]
    #for x in range(map_info.earth_width):
        #for y in range(map_info.earth_height):
    curr_x, curr_y = curr_robot.location.map_location().x, curr_robot.location.map_location().y
    for x in [curr_x - 1, curr_x, curr_x + 1]:
        for y in [curr_y - 1, curr_y, curr_y + 1]:
            if x == curr_x and y == curr_y:
                continue
            if x not in range(map_info.earth_width):
                continue
            if y not in range(map_info.earth_height):
                continue
            #print(other_robot.location.map_location())
            #x, y =
            d = ((other_robot.location.map_location().x - x) ** 2) + ((other_robot.location.map_location().y - y) ** 2)
            f = k * (math.exp(-((d-c)**2)/(2*(e**2)))) / (math.sqrt(2*3.14*(e**2)))
            if temp_pf[x][y] != -100:                   #f > temp_pf[x][y] and
                temp_pf[x][y] += f
    return temp_pf


def calc_field(robot):
    
    r_type = robot.unit_type
    location = robot.location
    
    '''if location.is_on_map():
        loc = location.map_location()
        if robot.unit_type == bc.'''
    
    if location.is_on_map:
        loc = location.map_location()
        for unit in gc_file.gc.my_units():
            if robot != unit and unit.location.is_on_map():
                unit_loc = unit.location.map_location()
                
                if r_type == bc.UnitType.Worker:
                    r = "worker"
                    if unit.unit_type == bc.UnitType.Worker:
                        o = "worker"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Knight:
                        o = "knight"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Ranger:
                        o = "ranger"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Mage:
                        o = "mage"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Healer:
                        o = "healer"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Factory:
                        o = "factory"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Rocket:
                        o = "rocket"
                        get_f(robot, r, unit, o)
                    else:
                        print("UNIT NOT FOUND!!!")
                        continue


                elif r_type == bc.UnitType.Ranger:
                    r = "ranger"
                    if unit.unit_type == bc.UnitType.Worker:
                        o = "worker"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Knight:
                        o = "knight"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Ranger:
                        o = "ranger"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Mage:
                        o = "mage"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Healer:
                        o = "healer"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Factory:
                        o = "factory"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Rocket:
                        o = "rocket"
                        get_f(robot, r, unit, o)
                    
                    else:
                        print("UNIT NOT FOUND!!!")
                        continue


                elif r_type == bc.UnitType.Knight:
                    r = "knight"
                    if unit.unit_type == bc.UnitType.Worker:
                        o = "worker"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Knight:
                        o = "knight"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Ranger:
                        o = "ranger"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Mage:
                        o = "mage"
                        et_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Healer:
                        o = "healer"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Factory:
                        o = "factory"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Rocket:
                        o = "rocket"
                        get_f(robot, r, unit, o)
                    
                    else:
                        print("UNIT NOT FOUND!!!")
                        continue


                elif r_type == bc.UnitType.Mage:
                    r = "mage"
                    if unit.unit_type == bc.UnitType.Worker:
                        o = "worker"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Knight:
                        o = "knight"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Ranger:
                        o = "ranger"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Mage:
                        o = "mage"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Healer:
                        o = "healer"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Factory:
                        o = "factory"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Rocket:
                        o = "rocket"
                        get_f(robot, r, unit, o)
                    
                    else:
                        print("UNIT NOT FOUND!!!")
                        continue


                elif r_type == bc.UnitType.Healer:
                    r = "healer"
                    if unit.unit_type == bc.UnitType.Worker:
                        o = "worker"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Knight:
                        o = "knight"
                        get_f(robot, r, unit, o)
                
                    elif unit.unit_type == bc.UnitType.Ranger:
                        o = "ranger"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Mage:
                        o = "mage"
                        get_f(robot, r, unit, o)
                
                    elif unit.unit_type == bc.UnitType.Healer:
                        o = "healer"
                        get_f(robot, r, unit, o)

                    elif unit.unit_type == bc.UnitType.Factory:
                        o = "factory"
                        get_f(robot, r, unit, o)
                    
                    elif unit.unit_type == bc.UnitType.Rocket:
                        o = "rocket"
                        get_f(robot, r, unit, o)
                    
                    else:
                        print("UNIT NOT FOUND!!!")
                        continue

        #print("Field: {}".format(f))
        #fe = []
        if len(units.enemies) > 0:
            for enemy in units.enemies:
                if enemy.location.is_on_map():
                    enemy_loc = enemy.location.map_location()

                    if r_type == bc.UnitType.Worker:
                        r = "worker"
                        if enemy.unit_type == bc.UnitType.Worker:
                            o = "worker"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Knight:
                            o = "knight"
                            get_f_enemy(robot, r, unit, o)
                
                        elif enemy.unit_type == bc.UnitType.Ranger:
                            o = "ranger"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Mage:
                            o = "mage"
                            get_f_enemy(robot, r, unit, o)
                
                        elif enemy.unit_type == bc.UnitType.Healer:
                            o = "healer"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Factory:
                            o = "factory"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Rocket:
                            o = "rocket"
                            get_f_enemy(robot, r, unit, o)

                        else:
                            print("UNIT NOT FOUND!!!")
                            continue


                    elif r_type == bc.UnitType.Ranger:
                        r = "ranger"
                        if enemy.unit_type == bc.UnitType.Worker:
                            o = "worker"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Knight:
                            o = "knight"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Ranger:
                            o = "ranger"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Mage:
                            o = "mage"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Healer:
                            o = "healer"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Rocket:
                            o = "rocket"
                            get_f_enemy(robot, r, unit, o)

                        elif enemy.unit_type == bc.UnitType.Factory:
                            o = "factory"
                            get_f_enemy(robot, r, unit, o)
                
                        else:
                            print("UNIT NOT FOUND!!!")
                            continue
                                

                    elif r_type == bc.UnitType.Knight:
                        r = "knight"
                        if enemy.unit_type == bc.UnitType.Worker:
                            o = "worker"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Knight:
                            o = "knight"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Ranger:
                            o = "ranger"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Mage:
                            o = "mage"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Healer:
                            o = "healer"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Rocket:
                            o = "rocket"
                            get_f_enemy(robot, r, unit, o)

                        elif enemy.unit_type == bc.UnitType.Factory:
                            o = "factory"
                            get_f_enemy(robot, r, unit, o)
                
                        else:
                            print("UNIT NOT FOUND!!!")
                            continue


                    elif r_type == bc.UnitType.Mage:
                        r = "mage"
                        if enemy.unit_type == bc.UnitType.Worker:
                            o = "worker"
                            get_f_enemy(robot, r, unit, o)
                    
                        elif enemy.unit_type == bc.UnitType.Knight:
                            o = "knight"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Ranger:
                            o = "ranger"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Mage:
                            o = "mage"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Healer:
                            o = "healer"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Rocket:
                            o = "rocket"
                            get_f_enemy(robot, r, unit, o)

                        elif enemy.unit_type == bc.UnitType.Factory:
                            o = "factory"
                            get_f_enemy(robot, r, unit, o)
                
                        else:
                            print("UNIT NOT FOUND!!!")
                            continue


                    elif r_type == bc.UnitType.Healer:
                        r = "healer"
                        if enemy.unit_type == bc.UnitType.Worker:
                            o = "worker"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Knight:
                            o = "knight"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Ranger:
                            o = "ranger"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Mage:
                            o = "mage"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Healer:
                            o = "healer"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Factory:
                            o = "factory"
                            get_f_enemy(robot, r, unit, o)
                        
                        elif enemy.unit_type == bc.UnitType.Rocket:
                            o = "rocket"
                            get_f_enemy(robot, r, unit, o)
                        
                        else:
                            print("UNIT NOT FOUND!!!")
                            continue

        '''
        #print("Field enemy: {}".format(fe))
        if fe:
            if f == fe:
                print("Fields equal")
            else:
                for i in range(len(f)):
                    for j in range(len(f[i])):
                        #if f[i][j] < fe[i][j]:
                        f[i][j] += fe[i][j]
        #print("{}, {}".format(x,y))
        '''

        d = calc_dir(robot, temp_pf)

        x, y = location.map_location().x, location.map_location().y
        for i in [x-1, x, x+1]:
            for j in [y-1, y, y+1]:
                if i == x and j == y:
                    continue
                if x not in range(map_info.earth_width):
                    continue
                if y not in range(map_info.earth_height):
                    continue
                temp_pf[x][y] = potentials_earth[x][y]

        return d


def calc_dir(robot, field):
    d = {}
    if robot.location.is_on_map():
        m = 8
        loc = robot.location.map_location()
        x, y = loc.x, loc.y
        #print("EARTH X: {}".format(map_info.earth_height))
        #print("EARTH y: {}".format(map_info.earth_width))
        #print("{}, {}".format(x,y))
        if (x in range(1, map_info.earth_width-1)) and (y in range(1, map_info.earth_height-1)):
            #print("In range")
            d[0] = field[x][y+1]
            d[1] = field[x+1][y+1]
            d[2] = field[x+1][y]
            d[3] = field[x+1][y-1]
            d[4] = field[x][y-1]
            d[5] = field[x-1][y-1]
            d[6] = field[x-1][y]
            d[7] = field[x-1][y+1]
            #m = max(d)

        elif x-1 not in range(map_info.earth_width):
            if y-1 not in range(map_info.earth_height):
                d[0] = field[x][y+1]
                d[1] = field[x+1][y+1]
                d[2] = field[x+1][y]
                d[3] = -999
                d[4] = -999
                d[5] = -999
                d[6] = -999
                d[7] = -999
            
            elif y+1 not in range(map_info.earth_height):
                d[0] = -999
                d[1] = -999
                d[2] = field[x+1][y]
                d[3] = field[x+1][y-1]
                d[4] = field[x][y-1]
                d[5] = -999
                d[6] = -999
                d[7] = -999
                    
            else:
                d[0] = field[x][y+1]
                d[1] = field[x+1][y+1]
                d[2] = field[x+1][y]
                d[3] = field[x+1][y-1]
                d[4] = field[x][y-1]
                d[5] = -999
                d[6] = -999
                d[7] = -999

        elif x+1 not in range(map_info.earth_width):
            if y-1 not in range(map_info.earth_height):
                d[0] = field[x][y+1]
                d[1] = -999
                d[2] = -999
                d[3] = -999
                d[4] = -999
                d[5] = -999
                d[6] = field[x-1][y]
                d[7] = field[x-1][y+1]
            
            elif y+1 not in range(map_info.earth_height):
                d[0] = -999
                d[1] = -999
                d[2] = -999
                d[3] = -999
                d[4] = field[x][y-1]
                d[5] = field[x-1][y-1]
                d[6] = field[x-1][y]
                d[7] = -999
            
            else:
                d[0] = field[x][y+1]
                d[1] = -999
                d[2] = -999
                d[3] = -999
                d[4] = field[x][y-1]
                d[5] = field[x-1][y-1]
                d[6] = field[x-1][y]
                d[7] = field[x-1][y+1]
                            
        elif y-1 not in range(map_info.earth_height):
            if x-1 not in range(map_info.earth_width):
                d[0] = field[x][y+1]
                d[1] = field[x+1][y+1]
                d[2] = field[x+1][y]
                d[3] = -999
                d[4] = -999
                d[5] = -999
                d[6] = -999
                d[7] = -999

            elif x+1 not in range(map_info.earth_width):
                d[0] = field[x][y+1]
                d[1] = -999
                d[2] = -999
                d[3] = -999
                d[4] = -999
                d[5] = -999
                d[6] = field[x-1][y]
                d[7] = field[x-1][y+1]
                        
            else:
                d[0] = field[x][y+1]
                d[1] = field[x+1][y+1]
                d[2] = field[x+1][y]
                d[3] = -999
                d[4] = -999
                d[5] = -999
                d[6] = field[x-1][y]
                d[7] = field[x-1][y+1]


        elif y+1 not in range(map_info.earth_height):
            if x-1 not in range(map_info.earth_width):
                d[0] = -999
                d[1] = -999
                d[2] = field[x+1][y]
                d[3] = field[x+1][y-1]
                d[4] = field[x][y-1]
                d[5] = -999
                d[6] = -999
                d[7] = -999
                
            elif x+1 not in range(map_info.earth_width):
                d[0] = -999
                d[1] = -999
                d[2] = -999
                d[3] = -999
                d[4] = field[x][y-1]
                d[5] = field[x-1][y-1]
                d[6] = field[x-1][y]
                d[7] = -999

            else:
                d[0] = -999
                d[1] = -999
                d[2] = field[x+1][y]
                d[3] = field[x+1][y-1]
                d[4] = field[x][y-1]
                d[5] = field[x-1][y-1]
                d[6] = field[x-1][y]
                d[7] = -999
                    
        else:
            print("WEIRD SITUATION!!")
        
        #print(d)
        
        m = max(d, key = d.get)
        #print(m)

#print("DIRECTIONS: {}".format(directions))

        '''
        for i in d:
            if d[i] == m:
                direction = i
        print("Direction: {}".format(direction))
        '''
        '''
        if m == 0:
            print(directions[0])
        elif m == 1:
            print(directions[1])
        elif m == 2:
            print(directions[2])
        elif m == 3:
            print(directions[3])
        elif m == 4:
            print(directions[4])
        elif m == 5:
            print(directions[5])
        elif m == 6:
            print(directions[6])
        elif m == 7:
            print(directions[7])
        elif m == 8:
            print(directions[8])
        '''

#print("BEFORE DIRECTIONS[m]")
        if m in range(8):
            return directions[m]
        else:
            print("WRONG DIRECTIONS!!!")
#print("AFTER DIRECTIONS[m]")

    else:
        print("NOT ON MAP!!!")
