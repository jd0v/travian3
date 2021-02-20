import time
import os
import main_code  # caution: deadlock
# import random
import helper
import string
import selenium.common
# import main.page_elements
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import village_management
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from collections import OrderedDict

STANDARD_FARMING_TROOP_LIST = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0]


class NatureTroops:

    image_identification = {
        "u31": "rat",
        "u32": "spider",
        "u33": "snake",
        "u34": "bat",
        "u35": "wild boar",
        "u36": "wolf",
        "u37": "bear",
        "u38": "crocodile",
        "u39": "tiger",
        "u40": "elephant",
    }

    average_deff = OrderedDict([
        ("rat", 22.5),
        ("spider", 37.5),
        ("snake", 50),
        ("bat", 58),
        ("wild boar", 51.5),
        ("wolf", 75),
        ("bear", 170),
        ("crocodile", 310),
        ("tiger", 210),
        ("elephant", 480),
    ])


class FarmingAI:
    def __init__(self, container):
        self.container = container
        self.driver = self.container.driver
        self.helper = self.container.helper
        self.log = self.container.log

    def get_resources_from_report(self):
        try:
            carry_obj = self.container.driver.find_element_by_class_name("carry")
        except:
            return None, None
        text_str = carry_obj.text.encode('ascii', 'ignore').decode("utf-8")
        [robber_resources, total_capacity] = [int(resources) for resources in text_str.split('/')]
        return robber_resources, total_capacity

    def adjust_troop_amount_to_send(self):
        robber_resources, total_capacity = self.get_resources_from_report()
        if None not in (robber_resources, total_capacity):
            if robber_resources == total_capacity:
                self.log.info("Full bag of resources: troops amount should be increased.")
                return 1
            elif robber_resources/total_capacity < 0.5:
                self.log.info("Less than half a bag of resources: troops amount should be decreased.")
                return -1
            else:
                return 0
        else:
            return 0

    def get_troops_for_next_attack(self, coordinates, troop_type):
        pass


class FarmUnderAttackControl:

    def __init__(self, container, filepath="farms_under_attack.txt"):
        self.container = container
        self.driver = self.container.driver
        self.helper = self.container.helper
        self.log = self.container.log
        self.filepath = filepath

    def read_from_farm_file(self):
        farms_under_attack = []
        with open(self.filepath, 'r') as f:
            while True:
                coords_str = f.readline()
                if coords_str:
                    coords_str_list = coords_str.replace('\n', '').split('|')
                    farms_under_attack.append([int(coord) for coord in coords_str_list])
                else:
                    break
        return farms_under_attack

    def write_to_farm_file(self, farms_under_attack):
        farm_list_str = ["{}|{}\n".format(coordinates[0], coordinates[1]) for coordinates in farms_under_attack]
        str_to_write = ''.join(farm_list_str)
        with open(self.filepath, 'w') as f:
            f.write(str_to_write)

    def add_farm(self, coordinates):
        string_to_write = "{}|{}\n".format(coordinates[0], coordinates[1])
        with open(self.filepath, 'a') as f:
            f.write(string_to_write)

    def remove_farm(self, coordinates):
        farms_under_attack = self.read_from_farm_file()
        try:
            farms_under_attack.remove(coordinates)
        except ValueError:
            self.log.warning("Coordinates {} weren't in the 'farms_under_attack' list.".format(coordinates))
        self.write_to_farm_file(farms_under_attack)

    def check_if_farm_is_under_attack(self, coordinates):
        farms_under_attack = self.read_from_farm_file()
        if coordinates in farms_under_attack:
            return True
        else:
            return False


class Farming:
    def __init__(self, container):
        self.container = container
        self.driver = self.container.driver
        self.helper = self.container.helper
        self.log = self.container.log
        self.village_control = village_management.VillageControl(self.container)
        self.off_city_name = village_management.VillagesTypes().OFF
        self.farms_under_attack_control = FarmUnderAttackControl(self.container)
        self.farming_ai = FarmingAI(self.container)

    def total_unread_reports(self):
        reports_element = self.driver.find_element_by_class_name("reports")
        try:
            return reports_element.find_element_by_class_name("indicator").text
        except:
            self.log.info('No unread reports')
            return 0

    def perform_failed_attacks(self):
        try:
            self.farm_from_file('failed_attacks.txt', delete=True)
        except FileNotFoundError as ex:  # file not found
            if "failed_attacks.txt" in ex.__str__():
                self.log.info("'failed_attacks.txt' file not found. Creating it")
                with open("failed_attacks.txt", 'w') as f:
                    # f.write("active;nickname;coordinates;troops;attack_type\n")
                    f.write("coordinates;troops\n")
            else:
                raise

    def go_to_reports(self):
        self.driver.find_element_by_class_name("reports").click()

    def farm_from_reports(self):
        # reports_element = self.driver.find_element_by_class_name("reports").click()

        while True:
            total_unread_reports = self.total_unread_reports()
            if not total_unread_reports:
                return

            self.log.debug("Total unread reports: " + str(total_unread_reports))

            # self.log.debug("Going to reports page")

            # iterate through pages while unread message is found
            # while True:
            self.go_to_reports()
            unread_messages = self.driver.find_elements_by_class_name('newMessage')
            if not unread_messages:
                next_button = self.driver.find_element_by_class_name("next")
                if "disabled" in next_button.get_attribute("class"):
                    self.go_to_reports()
                else:
                    ActionChains(self.container.driver).move_to_element(next_button).click(next_button).perform()
                continue

            losses_present = False
            # while True:
            new_msg = unread_messages[0]
            # new_msg = self.container.driver.find_element_by_class_name("newMessage")
            send_troops = False
            if new_msg.find_elements_by_class_name("iReport1"):
                msg_to_farm_again = self.container.driver.find_element_by_xpath("//td[contains(@class, 'newMessage')]/div/a")
                msg_to_farm_again.click()
            # ActionChains(self.container.driver).move_to_element(msg_to_farm_again).click(msg_to_farm_again).perform()
                send_troops = True
            elif new_msg.find_elements_by_class_name("iReport2") or new_msg.find_elements_by_class_name("iReport3"):
                msg_to_farm_again = self.container.driver.find_element_by_xpath("//td[contains(@class, 'newMessage')]/div/a")
                # ActionChains(self.container.driver).move_to_element(msg_to_farm_again).click(msg_to_farm_again).perform()
                msg_to_farm_again.click()
                losses_present = True
            else:
                unread_status = new_msg.find_element_by_class_name("messageStatusUnread")  # make report look like read
                ActionChains(self.container.driver).move_to_element(unread_status).click(unread_status).perform()
                continue

            # IN THE REPORT:
            try:
                troops = self.driver.find_element_by_id('attacker')
                troops = troops.find_elements_by_class_name('units')[1]
                troop_count_elements = troops.find_elements_by_class_name("unit")
                attacker_troop_list_from_report = []
                target_troops = ''
                hero_present = False
                for idx, troop in enumerate(troop_count_elements):
                    if idx == 10:
                        if troop.text == "1":
                            hero_present = True
                    else:
                        attacker_troop_list_from_report.append(int(troop.text))
                        target_troops += troop.text + ','
                target_troops = target_troops[:-1]

                if hero_present:
                    self.go_to_reports()
                    continue

                # if sum([int(x) for x in attacker_troop_list_from_report]) >= 40:
                #     self.go_to_reports()
                #     continue

                adjust_troop_amount = self.farming_ai.adjust_troop_amount_to_send()

                farm = {"attack_type": "raid", "troops": attacker_troop_list_from_report}

                # GO to the village of a farm
                self.log.debug("Going to the village of a farm")
                # TODO: sitoj vietoj gali buti fucked up, kai besiginantis turi pastiprinimu
                defender = self.driver.find_elements_by_class_name("troopHeadline")[1]
                village = defender.find_element_by_class_name("village")
                village_url = village.get_attribute("href")
                self.container.driver.get(village_url)
                # village.click()
                # troop_headline_of_defender = self.driver.find_elements_by_xpath("//td/p/a")
                # target_name = troop_headline_of_defender[2].text  # might cause a problem if I'm also included (attacker)
                # target_name = target_name[:target_name.rfind(' ')]
                #
                # ActionChains(self.container.driver).move_to_element(village).click(village).perform()

                # get coords if an error occurs
                self.log.debug("Getting coords of the farm village")
                coordinateX = self.driver.find_element_by_class_name("coordinateX").text[1:][1:-1]
                if '?' in coordinateX.replace("\u202d", "").replace("\u202c", "").encode('ascii', 'replace').decode("utf-8"):
                    coordinateX = "-" + coordinateX.encode('ascii', 'ignore').decode("utf-8")
                else:
                    coordinateX = coordinateX.encode('ascii', 'ignore').decode("utf-8")
                coordinateY = self.driver.find_element_by_class_name("coordinateY").text[:-1][1:-1]
                if '?' in coordinateY.replace("\u202d", "").replace("\u202c", "").encode('ascii', 'replace').decode("utf-8"):
                    coordinateY = "-" + coordinateY.encode('ascii', 'ignore').decode("utf-8")
                else:
                    coordinateY = coordinateY.encode('ascii', 'ignore').decode("utf-8")
                target_coordinates = [int(coordinateX), int(coordinateY)]
                farm["coordinates"] = target_coordinates

                if losses_present:
                    with open("attacks_with_losses.txt", "a") as f:
                        f.write('{}|{}\n'.format(farm["coordinates"][0], farm["coordinates"][1]))
                    continue

                self.farms_under_attack_control.remove_farm(target_coordinates)
                if not send_troops:
                    self.go_to_reports()
                    continue

                # if it's an oasis, check if no animals are present
                if FarmingOases(self.container).check_if_oasis_exists_at_coordinates():
                    troop_info_id = self.driver.find_element_by_id("troop_info")
                    if troop_info_id.find_elements_by_class_name("val"):
                        self.log.info("Skipping {} oasis, because it has some animals.".format(target_coordinates))
                        self.go_to_reports()
                        continue

                # GO to the attack page for selecting troops
                self.log.debug("Going to the troop selection page")
                troop_headline_list = self.driver.find_elements_by_class_name('arrow')
                # website = troop_headline_list[2].find_element_by_xpath("//div/a").get_attribute("href")
                index = 1
                if len(troop_headline_list) == 5:
                    index = 2
                website = troop_headline_list[index].get_attribute("href")
                self.log.info("Going to the website: {}".format(website))
                self.container.driver.get(website)
                # ActionChains(self.container.driver).move_to_element(troop_headline_list[1]).click(troop_headline_list[1]).perform()

                # make sure, that self.off_city_name is selected
                # self.village_control.change_village(self.off_city_name)

                if not self.send_troops_tab_management(farm, adjust_troop_amount=adjust_troop_amount):
                    self.log.debug("Not enough troops to send.")
                    self.append_failed_attack_to_file(target_coordinates, target_troops)
                    return

                self.go_to_reports()

            except Exception as ex:
                self.log.exception("Farming from a report failed:\n{}".format(ex))
                self.append_failed_attack_to_file(target_coordinates, target_troops)
                return

    def append_failed_attack_to_file(self, target_coords, target_troops):
        self.log.debug("Appending failed attack to a file")
        with open("failed_attacks.txt", 'a') as file:
            failed_attack_str = "{}|{};{}\n".format(target_coords[0], target_coords[1], target_troops)
            self.log.debug("Appending to 'failed_attacks': {}".format(failed_attack_str))
            file.write(failed_attack_str)

    def send_troops_tab_management(self, farm, adjust_troop_amount=0):
        try:
            farm["attack_type"]
        except KeyError:
            farm["attack_type"] = "raid"
        self.log.info("Sending troops to {} as {}: {}; adjusted troop amount is {}".format(farm["coordinates"], farm["attack_type"],
                                                                                           farm["troops"],adjust_troop_amount))

        # choosing troops
        for i in range(10):
            if int(farm["troops"][i]):
                # try:
                troop = self.driver.find_element_by_name("troops[0][{}]".format("t" + str(i + 1)))
                if "disabled" not in troop.get_attribute("class"):  # if at least single troop can be send
                    adjusted_troops = farm["troops"][i] + adjust_troop_amount
                    if adjusted_troops > 1:
                        farm["troops"][i] = adjusted_troops
                    troop.send_keys(farm["troops"][i])
                else:
                    self.log.info("Not enough troops.")
                    return False

        # choosing attack type
        raid_mode = self.driver.find_elements_by_class_name("radio")
        if farm["attack_type"] == "reinforcement":
            raid_mode[0].click()
        elif farm["attack_type"] == "attack":
            raid_mode[1].click()
        elif farm["attack_type"] == "raid":
            raid_mode[2].click()
        else:
            self.log.error("Attack type error: no such attack type")

        # choosing coordinates
        coord_x = self.driver.find_element_by_id("xCoordInput")
        coord_y = self.driver.find_element_by_id("yCoordInput")
        coord_x.clear()
        coord_y.clear()
        coord_x.send_keys(farm["coordinates"][0])
        coord_y.send_keys(farm["coordinates"][1])

        # confirm troop and attack type selection
        button = self.driver.find_element_by_id("btn_ok")
        self.container.driver.execute_script("arguments[0].click();", button)

        # confirm the attack
        try:
            troops_obj = self.container.driver.find_element_by_xpath("//tbody[contains(@class, 'units')]/tr[2]")
            troops_list = [int(troop) for troop in troops_obj.text.split(' ')[1:]]
            for idx in range(len(troops_list)):
                if troops_list[idx] != farm["troops"][idx]:
                    if adjust_troop_amount == 1:
                        farm["troops"][idx] -= 1
                        continue
                    self.log.info("Not enough troops. Need {}; currently have {}".format(troops_list, farm["troops"]))
                    return False

            self.driver.find_element_by_class_name("rallyPointConfirm").click()
        except selenium.common.exceptions.NoSuchElementException as ex:
            if "Unable to locate element: .rallyPointConfirm" in ex.__str__():
                self.log.warning("Not enough troops to send")
            else:
                self.log.exception(ex)
                raise ex

        self.farms_under_attack_control.add_farm(farm["coordinates"])
        self.log.info("Troops were sent: {}".format(farm["troops"]))
        return True
        # village_resources = self.driver.find_element_by_id('n1')
        # village_resources.click()

    def send_troops(self, farm):
        #
        # self.helper.dorf_fuse("n2")
        #
        # # go to rally point
        # rally_point = self.driver.find_element_by_class_name("aid39")
        # # rally_point.click()
        # ActionChains(self.container.driver).move_to_element(rally_point).click(rally_point).perform()
        #
        # # go to "send troops"
        # send_troops_page = self.driver.find_element_by_class_name("favorKey2")
        # # send_troops_page.click()
        # ActionChains(self.container.driver).move_to_element(send_troops_page).click(send_troops_page).perform()

        # go to the send troops page in rally point
        self.container.driver.get("{}{}".format(self.container.website, "/build.php?tt=2&id=39"))

        # make sure, that self.off_city_name is selected
        # self.village_control.change_village(self.off_city_name)

        # SETTING THE ATTACK
        if not self.send_troops_tab_management(farm):
            self.log.info("Not enough troops to send.")
            return False
        return True

    def farm_from_farmlist_file(self):
        # tags: nickname;coordinates;troops
        # read the farmlist from a file
        farmlist = []
        self.log.info("Reading villages to attack from a file")
        with open("farmlist.txt", 'r') as f:
            tags = None
            while True:
                farm = {}
                input = f.readline()
                input = input.replace("\n", "")
                input = input.split(';')
                if input != ['']:  # because it's a list and the last line would look like ['']
                    farm["nickname"] = input[0]
                    farm["coordinates"] = [int(coord) for coord in input[1].split('|')]
                    # farm["troops"] = self.farming_ai.get_troops_for_next_attack(coordinates=input[1], troop_type=input[2])
                    farm["troops"] = [int(troop) for troop in input[2].split(',')]
                    farm["attack_type"] = "raid"
                    farmlist.append(farm)
                else:
                    break

        # self.log.debug("Reading done. Total villages to attack found: {}".format(len(farmlist)))
        # self.log.debug("Village list: {}".format(farmlist))
        farms_already_under_attack = self.farms_under_attack_control.read_from_farm_file()
        for farm in farmlist:
            if farm["coordinates"] not in farms_already_under_attack:
                try:
                    if not self.send_troops(farm):
                        troop_string = str(farm['troops'][0])
                        for single_troop in farm['troops'][1:]:
                            troop_string += ',' + single_troop
                        self.append_failed_attack_to_file(farm['nickname'], farm['coordinates'], troop_string)
                except Exception as ex:
                    self.log.exception(ex)
                    troop_str_list = [str(troop) for troop in farm["troops"]]
                    troop_str = ','.join(troop_str_list)
                    self.append_failed_attack_to_file(farm['nickname'], farm['coordinates'], troop_str)
                    return

    def farm_from_file(self, file, delete=False):
        # tags: nickname;coordinates;troops
        # read the farmlist from a file
        farmlist = []
        self.log.info("Reading villages to attack from a file")
        with open(file, 'r') as f:
            tags = None
            while True:
                farm = {}
                input = f.readline()
                input = input.replace("\n", "")
                input = input.split(';')
                if tags is None:
                    tags = input
                elif input != ['']:  # because it's a list and the last line would look like ['']
                    for i in range(len(tags)):
                        if tags[i] == "coordinates":
                            input[i] = input[i].split('|')
                        elif tags[i] == "troops":
                            input[i] = input[i].split(',')
                            input[i] = [int(troop) for troop in input[i]]
                        farm[tags[i]] = input[i]
                    # farm["attack_type"] = "raid"
                    farmlist.append(farm)
                else:
                    break

        self.log.debug("Reading done. Total villages to attack found: {}".format(len(farmlist)))
        self.log.debug("Village list: {}".format(farmlist))

        if delete:
            # delete everything
            with open(file, 'w') as f:
                line_to_write = ""
                for tag in tags:
                    line_to_write += tag + ';'
                f.write(line_to_write[:-1] + '\n')

        for farm in farmlist:
            try:
                if not self.send_troops(farm):
                    troop_string = str(farm['troops'][0])
                    for single_troop in farm['troops'][1:]:
                        troop_string += ',' + single_troop
                    self.append_failed_attack_to_file(farm['coordinates'], troop_string)
            except Exception as ex:
                self.log.exception(ex)
                troop_str_list = [str(troop) for troop in farm["troops"]]
                troop_str = ','.join(troop_str_list)
                # troop_string = str(farm['troops'][0])
                # for single_troop in farm['troops'][1:]:
                #     troop_string += ',' + single_troop
                self.append_failed_attack_to_file(farm['coordinates'], troop_str)


class FarmingOases:

    def __init__(self, container):
        self.container = container
        self.driver = self.container.driver
        self.helper = self.container.helper
        self.log = self.container.log
        self.reference_coordinates = self.container.reference_coordinates
        self.village_control = village_management.VillageControl(self.container)
        self.off_city_name = village_management.VillagesTypes().OFF
        self.farms_under_attack_control = FarmUnderAttackControl(self.container)

    def go_to_page_of_coordinates(self, coords):
        self.driver.get("{}/position_details.php?x={}&y={}".format(self.container.website, coords[0], coords[1]))

    def check_if_oasis_exists_at_coordinates(self, coords=[]):
        if coords:
            self.go_to_page_of_coordinates(coords)

        try:
            self.driver.find_element_by_class_name("oasis")
        except:
            return False
        return True

    def check_if_oasis_is_free(self, coords, goto_page=True):
        if goto_page:
            self.go_to_page_of_coordinates(coords)
        if self.container.driver.find_elements_by_id("village_info"):
            return False
        return True

    def get_all_oases_list_in_area(self, radius):
        allowed_coords_list = []
        min_max_coords = [[self.reference_coordinates[0]-radius, self.reference_coordinates[1]-radius],
                          [self.reference_coordinates[0]+radius, self.reference_coordinates[1]+radius]]

        for x in range(min_max_coords[0][0], min_max_coords[1][0]+1):
            for y in range(min_max_coords[0][1], min_max_coords[1][1]+1):
                if self.helper.distance_from_reference_point([x, y]) <= radius:
                    if self.check_if_oasis_exists_at_coordinates([x, y]):
                        allowed_coords_list.append([x, y])

        with open("oases_coordinates.txt", 'w') as f:
            str_to_write = ""
            for coords in allowed_coords_list:
                str_to_write += "{}|{}\n".format(coords[0], coords[1])
            f.write(str_to_write)

    def get_oases_info(self):
        nearby_oases_coords_list = []
        with open("oases_coordinates.txt", 'r') as f:
            while True:
                input = f.readline().replace("\n", '')
                if input:
                    nearby_oases_coords_list.append([int(x) for x in input.split("|")])
                else:
                    break

        nature_info = NatureTroops()
        oases_info_list = []
        for idx, coords in enumerate(nearby_oases_coords_list):
            self.log.info("Reading oasis troops info ({}/{})".format(idx + 1, len(nearby_oases_coords_list)))
            self.go_to_page_of_coordinates(coords)

            free_oasis = self.check_if_oasis_is_free(coords, goto_page=False)

            troop_info = self.driver.find_element_by_id("troop_info")

            oasis_troops_types_obj = troop_info.find_elements_by_class_name("unit")
            oasis_troops_images_list = [type_obj.get_attribute("class").split(' ')[1] for type_obj in oasis_troops_types_obj]
            oasis_troops_types_list = [nature_info.image_identification[img] for img in oasis_troops_images_list]

            oasis_troops_amount_obj = troop_info.find_elements_by_class_name("val")
            oasis_troops_amount_list = [int(val.text) for val in oasis_troops_amount_obj]

            oasis_troops = []
            for animal in nature_info.average_deff:
                if animal in oasis_troops_types_list:
                    idx = oasis_troops_types_list.index(animal)
                    oasis_troops.append(oasis_troops_amount_list[idx])
                else:
                    oasis_troops.append(0)

            oasis_average_deff = 0
            for idx, animal in enumerate(nature_info.average_deff):
                oasis_average_deff += oasis_troops[idx] * nature_info.average_deff[animal]

            oases_info_list.append([free_oasis, coords, oasis_troops, oasis_average_deff])
            oases_info_list.sort(key=lambda oasis: (not oasis[0], oasis[3]))

        with open("oasis_info.txt", 'w') as f:
            str_to_write = ''
            for oasis in oases_info_list:
                free_oasis_str = 'T' if oasis[0] else 'N'
                coords_str = "|".join([str(coord) for coord in oasis[1]])
                troops_str = ",".join([str(troop) for troop in oasis[2]])
                str_to_write += "{};{};{};{}\n".format(free_oasis_str, coords_str, troops_str, oasis[3])
            f.write(str_to_write)

    def farm_from_oasis_info_file(self):
        oases_info_list = []
        with open("oasis_info.txt", 'r') as f:
            while True:
                input = f.readline().replace("\n", '')
                if input:
                    free_oasis_str, coords, troops, average_deff = input.split(';')
                    free_oasis = True if free_oasis_str == 'T' else False
                    coords = [int(coord) for coord in coords.split('|')]
                    troops = [int(troop) for troop in troops.split(',')]
                    average_deff = float(average_deff)
                    oases_info_list.append(OrderedDict([('free_oasis', free_oasis), ("coordinates", coords),
                                                        ("troops", troops), ("average_deff", average_deff)]))
                else:
                    break

        farming = Farming(self.container)
        oases_under_attack = self.farms_under_attack_control.read_from_farm_file()
        for oasis in oases_info_list:
            if oasis["average_deff"] == 0 and oasis["free_oasis"]:
                if oasis["coordinates"] not in oases_under_attack:
                    farm = OrderedDict([
                        ("coordinates", oasis["coordinates"]),
                        ("troops", STANDARD_FARMING_TROOP_LIST),
                        ("attack_type", "raid"),
                    ])
                    # for debugging:
                    if farm["coordinates"] == [-5, 35]:
                        self.log.debug("Wanting to attack unallowed oasis: {}. 'oasis[free_oasis]' = {}".format(farm["coordinates"], oasis["free_oasis"]))
                        continue
                    if not farming.send_troops(farm):
                        return


if __name__ == "__main__":
    pass
