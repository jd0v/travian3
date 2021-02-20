import time
import os
# import random
import string
import selenium.common
# import main.page_elements
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import OrderedDict
import re


class Statistics:

    def __init__(self, container=None):
        if __name__ != "__main__":
            self.container = container
            self.log = self.container.log
            self.helper = self.container.helper
            self.reference_coordinates = self.container.reference_coordinates
            self.player_attack_tab_info_from_website = {}
            self.player_deff_tab_info_from_website = {}
            self.player_village_tab_info_from_website = {}
            self.player_dict_from_file = {}
            self.new_player_list = []
            self.new_village_list = []
            self.tags_players = None
            self.tags_cities = None

    def scan_attack_tab_info_of_all_players(self):
        self.log.info("Scanning attack tab info of all players")
        self.player_attack_tab_info_from_website = {}
        # try:
        #     WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, "n4")))
        # except selenium.common.exceptions.TimeoutException as ex:
        #     self.log.exception("Exception while accessing statistics:")
        #     # self.log.exception(ex)
        #     raise ex

        # statistics_page = self.container.driver.find_element_by_id("n4")
        # statistics_page.click()

        self.container.driver.get(self.container.website + "/statistiken.php")

        attack_tab = self.container.driver.find_elements_by_class_name("favorKey1")[1]
        attack_tab.click()

        first_page = self.container.driver.find_element_by_class_name("number")
        first_page.click()

        while True:
            players_obj = self.container.driver.find_elements_by_class_name("hover")
            # tags = ["name", "time", "pop", "villages_count"]
            for player_obj in players_obj:
                player = Player(self.container, player_obj.find_element_by_class_name("pla").text)
                player.time = time.strftime("%d-%H")
                player.pop = player_obj.find_element_by_class_name("pop").text
                player.villages_count = player_obj.find_element_by_class_name("vil").text
                player.attack_points = player_obj.find_element_by_class_name("po").text
                # player.data_str = ','.join([player.time, player.pop, player.villages_count])
                self.player_attack_tab_info_from_website[player.player_name] = player
            element_next = self.container.driver.find_element_by_class_name("next")
            if "disabled" in element_next.get_attribute("class"):
                break
            else:
                break
                element_next.click()

    def scan_deff_tab_info_of_all_players(self):
        self.log.info("Scanning deff tab info of all players")
        self.player_deff_tab_info_from_website = {}
        try:
            WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, "n4")))
        except selenium.common.exceptions.TimeoutException as ex:
            self.log.exception("Exception while accessing statistics:")
            # self.log.exception(ex)
            raise ex

        statistics_page = self.container.driver.find_element_by_id("n4")
        statistics_page.click()

        deff_tab = self.container.driver.find_elements_by_class_name("favorKey2")[1]
        deff_tab.click()

        first_page = self.container.driver.find_element_by_class_name("number")
        first_page.click()

        while True:
            players_obj = self.container.driver.find_elements_by_class_name("hover")
            # tags = ["name", "time", "pop", "villages_count"]
            for player_obj in players_obj:
                name = player_obj.find_element_by_class_name("pla").text
                attack_points = player_obj.find_element_by_class_name("po").text
                self.player_deff_tab_info_from_website[name] = attack_points
            element_next = self.container.driver.find_element_by_class_name("next")
            if "disabled" in element_next.get_attribute("class"):
                break
            else:
                break
                element_next.click()

    def scan_village_tab_info_of_all_players(self):
        self.log.info("Scanning village tab info of all players")
        self.player_village_tab_info_from_website = {}
        try:
            WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, "n4")))
        except selenium.common.exceptions.TimeoutException as ex:
            self.log.exception("Exception while accessing statistics:")
            # self.log.exception(ex)
            raise ex
        statistics_page = self.container.driver.find_element_by_id("n4")
        statistics_page.click()

        cities_tab = self.container.driver.find_element_by_class_name("favorKey2")
        cities_tab.click()

        first_page = self.container.driver.find_element_by_class_name("number")
        first_page.click()

        while True:
            village_obj_list = self.container.driver.find_elements_by_class_name("hover")
            for village_obj in village_obj_list:
                village = Village(self.container, village_obj.find_element_by_class_name("pla").text)
                village.time = time.strftime("%d-%H")
                village.hab = village_obj.find_element_by_class_name("hab").text
                village.village_name = village_obj.find_element_by_class_name("vil").text
                village.coords = village_obj.find_element_by_class_name("coords").text
                village.data_str = ','.join([village.village_name, village.hab, village.coords])
                if village.player_name in self.player_village_tab_info_from_website:
                    self.player_village_tab_info_from_website[village.player_name].append(village)
                else:
                    self.player_village_tab_info_from_website[village.player_name] = [village]
            element_next = self.container.driver.find_element_by_class_name("next")
            if "disabled" in element_next.get_attribute("class"):
                break
            else:
                break
                element_next.click()

    def scan_attack_tab_info_single_player(self, name):
        self.log.info("Scanning attack tab info of {}".format(name))

        self.helper.dorf_fuse("n4")

        attack_tab = self.container.driver.find_elements_by_class_name("favorKey1")[1]
        attack_tab.click()

        name_input = self.container.driver.find_elements_by_class_name("text")[1]
        name_input.send_keys(name)
        name_input.send_keys(Keys.ENTER)

        player_obj = self.container.driver.find_element_by_class_name("hl")
        # tags = ["name", "time", "pop", "villages_count"]
        self.player_attack_tab_info_from_website[name].time = time.strftime("%d-%H")
        self.player_attack_tab_info_from_website[name].attack_points = player_obj.find_element_by_class_name("po").text
        self.player_attack_tab_info_from_website[name].pop = player_obj.find_element_by_class_name("pop").text
        self.player_attack_tab_info_from_website[name].villages_count = player_obj.find_element_by_class_name("vil").text

    def scan_deff_tab_info_single_player(self, name):
        self.log.info("Scanning deff tab info of {}".format(name))

        self.helper.dorf_fuse("n4")

        deff_tab = self.container.driver.find_elements_by_class_name("favorKey2")[1]
        deff_tab.click()

        name_input = self.container.driver.find_elements_by_class_name("text")[1]
        name_input.send_keys(name)
        name_input.send_keys(Keys.ENTER)

        player_obj = self.container.driver.find_element_by_class_name("hl")
        # tags = ["name", "time", "pop", "villages_count"]
        self.player_attack_tab_info_from_website[name].deff_points = player_obj.find_element_by_class_name("po").text

    def scan_villages_info_single_player_from_profile(self, name):
        self.log.info("Scanning villages info from the profile of {}".format(name))
        self.player_attack_tab_info_from_website[name].villages = []
        self.helper.dorf_fuse("n4")

        name_input = self.container.driver.find_elements_by_class_name("text")[1]
        name_input.send_keys(name)
        name_input.send_keys(Keys.ENTER)

        # cycle for waiting for the page to load
        start_cycle_time = time.clock()
        while True:
            try:
                player_obj = self.container.driver.find_element_by_class_name("hl")
            except selenium.common.exceptions.NoSuchElementException:
                if time.clock() - start_cycle_time > 31:
                    self.log.critical("The statistics player {} search didn't load".format(name))
                    return False
                if time.clock() - start_cycle_time > 10:
                    name_input = self.container.driver.find_elements_by_class_name("text")[1]
                    name_input.send_keys(name)
                    name_input.send_keys(Keys.ENTER)
                    continue
                time.sleep(0.3)
                continue
            if player_obj.find_element_by_class_name("pla").text == "ciumbalumba":
                time.sleep(0.5)
                continue
            print(player_obj.find_element_by_class_name("pla").text)
            player_rating_obj = player_obj.find_element_by_class_name("ra")
            table_index = int(player_rating_obj.text[:-1]) % 20
            if table_index == 0:
                table_index = 20
            print(name, len(self.container.driver.find_elements_by_xpath("//tr/td/a")), table_index)
            clickable_player_name_obj = self.container.driver.find_elements_by_xpath("//tr["+str(table_index)+"]/td/a")[0]
            clickable_player_name_obj.click()

            try:
                WebDriverWait(self.container.driver, 2).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "mainVillage")))
                break
            except selenium.common.exceptions.TimeoutException as ex:
                if time.clock() - start_cycle_time > 30:
                    self.log.critical("Player's {} profile page didn't load".format(name))
                    return False

        # villages_obj = self.container.driver.find_element_by_id("villages")
        # villages_obj = self.container.driver.find_elements_by_xpath("//table/tbody/tr")
        for i in range(len(self.container.driver.find_elements_by_class_name("oases"))):
            village = Village(self.container, name)
            village.village_name = self.container.driver.find_elements_by_class_name("name")[i].text
            village.hab = self.container.driver.find_elements_by_class_name("inhabitants")[i].text
            village.coords = self.container.driver.find_elements_by_class_name("coords")[i].text
            self.player_attack_tab_info_from_website[name].villages.append(village)
        self.player_attack_tab_info_from_website[name].villages_count = len(self.player_attack_tab_info_from_website[name].villages)
        return True

    def repair_scanned_info(self):
        for name in self.player_deff_tab_info_from_website:
            if name not in self.player_attack_tab_info_from_website:
                self.player_attack_tab_info_from_website[name] = Player(self.container, name)
            self.player_attack_tab_info_from_website[name].deff_points = self.player_deff_tab_info_from_website[name]

        for name in self.player_village_tab_info_from_website:
            if name not in self.player_attack_tab_info_from_website:
                self.player_attack_tab_info_from_website[name] = Player(self.container, name)
            self.player_attack_tab_info_from_website[name].villages.append(self.player_village_tab_info_from_website[name])

        for name in self.player_attack_tab_info_from_website:
            if self.player_attack_tab_info_from_website[name].attack_points is None:
                self.scan_attack_tab_info_single_player(name)
            if self.player_attack_tab_info_from_website[name].deff_points is None:
                self.scan_deff_tab_info_single_player(name)
            if self.player_attack_tab_info_from_website[name].villages_count !=\
                    len(self.player_attack_tab_info_from_website[name].attack_points):
                for i in range(3):
                    if self.scan_villages_info_single_player_from_profile(name):
                        break
                pass

    def read_players_info_from_file(self):
        self.log.info("Reading players' info from file")
        self.player_dict_from_file = {}
        with open("players_info.txt", 'r') as f:
            self.tags_players = None
            while True:
                input = f.readline()
                input = input.replace("\n", "")
                if self.tags_players is None:
                    self.tags_players = input
                elif not input:
                    break
                else:
                    index = input.find(':')
                    self.player_dict_from_file[input[:index]] = input[index+1:]
        self.log.debug("Player info from file: {}".format(self.player_dict_from_file))

    def read_single_player_info_from_file(self, name):
        self.log.info("Reading player's {} info from file".format(name))
        with open("players_info.txt", 'r') as f:
            self.tags_players = None
            while True:
                self.player_dict_from_file = {}
                input = f.readline()
                index = input.find(':')
                if not input:
                    return None
                elif name == input[:index]:
                    input = input.replace("\n", "")
                    return input[index+1:]
                else:
                    continue

    def update_and_write_info_of_all_players(self):
        self.new_player_list.append(self.tags_players + '\n')
        for player_name in self.player_attack_tab_info_from_website:
            current = self.player_attack_tab_info_from_website[player_name]
            current.data_str = "{},{},{}<".format(current.time, current.pop, current.villages_count)
            for village in current.villages:
                current.data_str += village.data_str + r"\/"
            current.data_str = current.data_str[:-2]
            if player_name in self.player_dict_from_file:
                self.new_player_list.append(player_name + ':' + self.player_dict_from_file[player_name] + ';' + self.player_attack_tab_info_from_website[player_name].data_str + '\n')
                del self.player_dict_from_file[player_name]
            else:
                self.new_player_list.append(player_name + ':' + self.player_attack_tab_info_from_website[player_name].data_str + '\n')
        for pl in self.player_dict_from_file:
            self.new_player_list.append(pl + ':' + self.player_attack_tab_info_from_website[player_name].data_str + '\n')

        with open("players_info.txt", 'w') as f:
            info_str = ''.join(self.new_player_list)
            f.write(info_str)

    def update_all_player_info(self):

        self.scan_attack_tab_info_of_all_players()
        self.scan_deff_tab_info_of_all_players()
        self.scan_village_tab_info_of_all_players()

        self.repair_scanned_info()

        try:
            self.read_players_info_from_file()
        except FileNotFoundError:
            self.log.info("No 'player_info.txt' file found. Creating it")
            # create the file
            with open("players_info.txt", 'w') as f:
                f.write("player_name;time;pop;villages_count;village_name;hab;coords\n")
            self.read_players_info_from_file()  # for header. can be changed into smth else
        self.update_and_write_info_of_all_players()

    def plotting(self, name):

        def two_scales(ax1, time, data1, data2, c1, c2):
            ax2 = ax1.twinx()

            ax1.plot(time, data1, color=c1)
            ax1.set_ylabel('population')

            ax2.plot(time, data2, color=c2)
            ax2.set_ylabel('villages')
            return ax1, ax2

        # Change color of each axis
        def color_y_axis(ax, color):
            """Color your axes."""
            for t in ax.get_yticklabels():
                t.set_color(color)
            return None

        data = self.read_nearby_players_info_from_file("nearby_players_info.txt")
        player = data[name]

        timestamp_list = []
        timestamp_values_to_compare_list = []
        population_list = []
        village_count_list = []
        # off_points_list = []
        deff_points_list = []

        for timestamp_str in player:
            timestamp = [int(x) for x in timestamp_str.split('-')]
            timestamp_list.append(timestamp)
            timestamp_values_to_compare_list.append(timestamp[0]*24 + timestamp[1])
            population_list.append(player[timestamp_str][0])
            village_count_list.append(player[timestamp_str][1])
            # off_points_list.append(player[timestamp_str][2])
            deff_points_list.append(player[timestamp_str][2])

        # Create axes
        # X axis label:
        timestamp_list_str = []
        for timestamp in timestamp_list:
            timestamp_list_str.append("{}:{}".format(timestamp[0], timestamp[1]))

        def format_fn(tick_val, tick_pos):
            if int(tick_val) in timestamp_values_to_compare_list:
                index = timestamp_values_to_compare_list.index(int(tick_val))
                return timestamp_list_str[index]
            else:
                return ''

        # fig, ax = plt.subplots(1)
        fig, (ax, ax3) = plt.subplots(2, sharex=True)
        minn = min(timestamp_values_to_compare_list)
        maxx = int((max(timestamp_values_to_compare_list) + 1) * 1.05)
        plt.xticks(range(minn, maxx, 1), rotation=45)
        ax.xaxis.set_major_formatter(FuncFormatter(format_fn))

        # plt.subplot(311)
        ax1, ax2 = two_scales(ax, timestamp_values_to_compare_list, population_list, village_count_list, 'm', 'b')

        color_y_axis(ax1, 'm')
        color_y_axis(ax2, 'b')
        matplotlib.pyplot.suptitle(name)

        # ax3.plot(timestamp_values_to_compare_list, off_points_list, 'r')
        # ax3.set_ylabel('Off points')
        ax3.plot(timestamp_values_to_compare_list, deff_points_list, 'g')
        ax3.set_ylabel("Deff points")
        ax3.set_xlabel('time')

        fig.subplots_adjust(hspace=0)

        plt.show()

    def get_all_nearby_players_names_list(self, max_distance=30):
        self.log.info("Scanning attack tab for nearby players")
        nearby_player_set = set()

        # self.helper.dorf_fuse("n4")
        self.container.driver.get(self.container.website + "/statistiken.php")

        attack_tab = self.container.driver.find_element_by_class_name("favorKey2")
        attack_tab.click()

        # first_page = self.container.driver.find_element_by_class_name("number")
        # first_page.click()

        self.log.info("Scanning for nearby players with a reference coordinates: {}".format(self.reference_coordinates))

        page = 1
        while True:
            self.container.driver.get("{}/statistiken.php?id=2&page={}".format(self.container.website, page))
            village_obj_list = self.container.driver.find_elements_by_class_name("hover")
            if len(village_obj_list) == 0:
                break

            for village_obj in village_obj_list:

                # fucked up unicode
                current_coords_raw = village_obj.find_element_by_class_name("coords").text
                current_coords_str_list = current_coords_raw[1:-1].split('|')
                current_coords_str_list_2 = [current_coords_str_list[k].encode('ascii', 'ignore').decode("utf-8")
                                                 .replace("(", "").replace(")", "") for k in range(2)]

                for i in range(2):
                    if current_coords_str_list[i].count("\u202d") == 2:
                        current_coords_str_list_2[i] = "-" + current_coords_str_list_2[i]

                current_coords = [int(current_coords_str_list_2[k]) for k in range(2)]

                # distance_x = current_coords[0]-self.reference_coordinates[0]
                # distance_y = current_coords[1]-self.reference_coordinates[1]
                # distance = (distance_x**2 + distance_y**2)**0.5
                distance = self.helper.distance_from_reference_point(current_coords)
                if distance <= max_distance:
                    player_name = village_obj.find_element_by_class_name("pla").text
                    nearby_player_set.add(player_name)

            # element_next = self.container.driver.find_element_by_class_name("next")
            # if "disabled" in element_next.get_attribute("class"):
            #     break
            # else:
            #     element_next.click()

            page += 1

        with open("nearby_players_names.txt", 'w', encoding="utf-8") as f:
            info_str = "\n".join(nearby_player_set)
            f.write(info_str)

    def read_nearby_player_names_from_file(self):
        players_list = []
        with open("nearby_players_names.txt", 'r', encoding="utf-8") as f:
            while True:
                input = f.readline().replace("\n", '')
                if input:
                    players_list.append(input)
                else:
                    break
        return players_list

    def scan_attack_and_deff_tab_info_of_nearby_players_list_to_file(self):
        # GET PLAYERS LIST FROM FILE
        players_list = self.read_nearby_player_names_from_file()
        players_to_remove = []

        self.container.driver.get(self.container.website + "/statistiken.php")

        self.log.info("Scanning attack tab info of {}".format(players_list))

        # ATTACK TAB
        attack_tab = self.container.driver.find_elements_by_class_name("favorKey1")[1]
        attack_tab.click()

        players_info = {}
        for idx, name in enumerate(players_list):
            self.log.info("Reading attack tab info of {} ({}/{})".format(name, idx+1, len(players_list)))
            name_input = self.container.driver.find_elements_by_class_name("text")[1]
            name_input.clear()
            name_input.send_keys(name)
            name_input.send_keys(Keys.ENTER)

            player = Player(self.container, name)
            player_obj = self.container.driver.find_element_by_class_name("hl")
            if player_obj.find_element_by_class_name("pla").text == name:
                # tags = ["name", "time", "pop", "villages_count"]
                player.time = time.strftime("%d-%H")
                player.attack_points = player_obj.find_element_by_class_name("po").text
                player.pop = player_obj.find_element_by_class_name("pop").text
                player.villages_count = player_obj.find_element_by_class_name("vil").text

                players_info[name] = player
            else:
                self.log.warning("Player {} not found!".format(name))
                players_to_remove.append(name)

        for name in players_to_remove:
            self.log.info("Removing player {} from 'players_list' in statistics.".format(name))
            players_list.remove(name)

        # DEFF TAB
        self.log.info("Scanning deff tab info of {}".format(players_list))

        deff_tab = self.container.driver.find_elements_by_class_name("favorKey2")[1]
        deff_tab.click()

        for idx, name in enumerate(players_list):
            self.log.info("Reading deff tab info of {} ({}/{})".format(name, idx + 1, len(players_list)))

            name_input = self.container.driver.find_elements_by_class_name("text")[1]
            name_input.clear()
            name_input.send_keys(name)
            name_input.send_keys(Keys.ENTER)

            player_obj = self.container.driver.find_element_by_class_name("hl")
            if player_obj.find_element_by_class_name("pla").text == name:
                players_info[name].deff_points = player_obj.find_element_by_class_name("po").text
            else:
                self.log.warning("Player {} not found!".format(name))
                players_list.remove(name)

        try:
            new_info = self.read_nearby_players_info_from_file("nearby_players_info.txt")
        except FileNotFoundError:
            new_info = {}
            for name in players_list:
                new_info[name] = {}

        for name in players_list:
            pl = players_info[name]
            try:
                new_info[name]
            except KeyError:
                new_info[name] = {}
            new_info[name][pl.time] = [int(pl.pop), int(pl.villages_count), int(pl.attack_points), int(pl.deff_points)]

        # WRITE INFO TO FILE
        with open("nearby_players_info.txt", 'wb') as f:
            final_str = ''
            for name in players_list:
                player_str = "{}:::".format(name)
                for timestamp in new_info[name]:
                    time_str_list = [str(x) for x in new_info[name][timestamp]]
                    player_str += "{},{};".format(timestamp, ','.join(time_str_list))
                final_str += player_str[:-1] + '\n'
            final_str = final_str.encode('utf8')
            f.write(final_str)

    def scan_deff_tab_info_of_nearby_players_list_to_file(self):
        # GET PLAYERS LIST FROM FILE
        players_list = self.read_nearby_player_names_from_file()
        players_to_remove = []

        self.helper.dorf_fuse("n4")

        self.log.info("Scanning deff tab info of {}".format(players_list))

        # DEFF TAB
        deff_tab = self.container.driver.find_elements_by_class_name("favorKey2")[1]
        deff_tab.click()

        players_info = {}
        for idx, name in enumerate(players_list):
            self.log.info("Reading deff tab info of {} ({}/{})".format(name, idx+1, len(players_list)))
            name_input = self.container.driver.find_elements_by_class_name("text")[1]
            name_input.clear()
            name_input.send_keys(name)
            name_input.send_keys(Keys.ENTER)

            player = Player(self.container, name)
            player_obj = self.container.driver.find_element_by_class_name("hl")
            if player_obj.find_element_by_class_name("pla").text == name:
                # tags = ["name", "time", "pop", "villages_count"]
                player.time = time.strftime("%d-%H")
                player.deff_points = player_obj.find_element_by_class_name("po").text
                player.pop = player_obj.find_element_by_class_name("pop").text
                player.villages_count = player_obj.find_element_by_class_name("vil").text

                players_info[name] = player
            else:
                self.log.warning("Player {} not found!".format(name))
                players_to_remove.append(name)

        # delete not found names
        for name in players_to_remove:
            self.log.info("Removing player {} from 'players_list' in statistics.".format(name))
            players_list.remove(name)

        # get old data
        try:
            new_info = self.read_nearby_players_info_from_file("nearby_players_info.txt")
        except FileNotFoundError:
            new_info = {}
            for name in players_list:
                new_info[name] = {}

        # add new data
        for name in players_list:
            pl = players_info[name]
            if name not in new_info:
                new_info[name] = {}
            new_info[name][pl.time] = [int(pl.pop), int(pl.villages_count), int(pl.deff_points)]

        # WRITE INFO TO FILE
        with open("nearby_players_info.txt", 'w', encoding="utf-8") as f:
            final_str = ''
            for name in players_list:
                player_str = "{}:::".format(name)
                for timestamp in new_info[name]:
                    time_str_list = [str(x) for x in new_info[name][timestamp]]
                    player_str += "{},{};".format(timestamp, ','.join(time_str_list))
                final_str += player_str[:-1] + '\n'
            f.write(final_str)

    def read_nearby_players_info_from_file(self, filepath):
        """
        DICT:
              PLAYER:
                      timestamp
                      timestamp
                      timestamp

              PLAYER:
                      timestamp
                      timestamp
        :return:
        """
        players_dict = OrderedDict([])
        with open(filepath, 'r') as f:
            while True:
                input = f.readline().replace("\n", '')
                if input:
                    name, raw_info_str = input.split(":::")
                    raw_info_list = raw_info_str.split(";")
                    records_dict = OrderedDict([])
                    for single_record in raw_info_list:
                        time, pop, villages_count, deff = single_record.split(',')
                        records_dict[time] = [int(pop), int(villages_count), int(deff)]
                    players_dict[name] = records_dict
                else:
                    break
        return players_dict

    def sort_players_dict(self, players_dict):
        # sorted_names = []
        players_to_sort = []
        for name in players_dict:
            last_timestamp = list(players_dict[name].keys())[-1]
            players_to_sort.append([name, players_dict[name][last_timestamp][0], players_dict[name][last_timestamp][2]])
        sorted_names = sorted(players_to_sort, key=lambda timestamp: (timestamp[2], timestamp[1]))

        print("Total zero deff points players: {}".format([player[2] for player in sorted_names].count(0)))
        with open("zero_deff_player_names.txt", 'w') as f:
            str_to_write = ''
            for player in sorted_names:
                if player[2] == 0:
                    str_to_write += "{}\n".format(player[0])
            f.write(str_to_write)

        return [name[0] for name in sorted_names]

    def get_friends_from_allies(self):
        allies = [29, 31, 47, 108]
        friends = []
        for ally in allies:
            self.container.driver.get("{}/allianz.php?aid={}&action=members".format(self.container.website, ally))
            total_members = int(self.container.driver.find_element_by_class_name("allianceMembers")
                                .find_elements_by_class_name("counter")[-1].text.replace('.', ''))
            for idx in range(2, total_members+1):
                friend = self.container.driver.find_element_by_xpath(
                    "//table[contains(@class, 'allianceMembers')]/tbody/tr[{}]/td[contains(@class, 'player')]/a".format(idx)).text
                friends.append(friend)

        with open("friends_list.txt", 'w') as f:
            str_to_write = '\n'.join(friends)
            f.write(str_to_write)


class Player(Statistics):

    def __init__(self, container, name):
        super().__init__(container)
        self.player_name = name
        self.time = None
        self.pop = None
        self.attack_points = None
        self.deff_points = None
        self.villages_count = None
        self.data_str = ""
        self.villages = []


class Village(Statistics):

    def __init__(self, container, name):
        super().__init__(container)
        self.player_name = name
        self.time = None
        self.hab = None
        self.village_name = None
        self.coords = None
        self.data_str = ""


if __name__ == "__main__":

    # players_list = Statistics().read_nearby_players_info_from_file("nearby_players_info.txt")
    # sorted_players_list = Statistics().sort_players_dict(players_list)
    #
    # for idx, name in enumerate(sorted_players_list):
    #     print("Player: {} {}/{}".format(name, idx+1, len(sorted_players_list)))
    #     Statistics().plotting(name)

    # Statistics().plotting('rob')
    Statistics().plotting('Back')
