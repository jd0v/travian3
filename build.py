import time
import os
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import village_management
import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


class Building:

    def __init__(self, name_label, name_class, name_location):
        self.name_label = name_label
        self.name_class = name_class
        self.name_location = name_location


# class Build(village_management.Village()):
class Build:
    def __init__(self, container):
        self.container = container
        self.log = self.container.log
        self.helper = self.container.helper
        self.village_name = village_management.VillageControl(self.container).get_active_village_name()
        self.buildings_dict = {}
        self.upgrade_plan_res = {"sawmill": 4,
                                 "brickyard": 4,
                                 "iron foundry": 4,
                                 "grain mill": 2}
        self.upgrade_plan_start = {"rally point": 1,
                                   "warehouse": 1,
                                   "granary": 1,
                                   "marketplace": 1,
                                   "cranny": 1,
                                   "main building": 5, }
        self.upgrade_plan_sirvys = {"warehouse": 5,
                                    "granary": 5}
        self.upgrade_plan_min = {"main building": 10,
                                 "hero's mansion": 1,
                                 "rally point": 3, }
        # "wall": 5,
        # "marketplace": 5}
        self.upgrade_plan_storage = {"warehouse": 10,
                                     "granary": 10}
        self.upgrade_plan_test = {"brickyard": 5}
        self.upgrade_plan_med = {"sawmill": 5,
                                 "brickyard": 5,
                                 "iron foundry": 5,
                                 "grain mill": 3,
                                 "bakery": 3,
                                 "main building": 15,
                                 "residence": 10,
                                 # "stonemason": 10,
                                 "wall": 10,
                                 "marketplace": 10,
                                 "barracks": 3,
                                 "academy": 10,
                                 "town hall": 1}
        self.upgrade_plan_adv = {"main building": 15,
                                 "grain mill": 5,
                                 "bakery": 4,
                                 "stonemason": 15,
                                 "wall": 16,
                                 "marketplace": 16}
        self.upgrade_plan_max = {"bakery": 5,
                                 "warehouse": 20,
                                 "granary": 20,
                                 "stonemason": 20,
                                 "wall": 20,
                                 "marketplace": 20,
                                 "town hall": 10}
        self.upgrade_plan_war = None
        self.upgrade_plan_hero = {"hero's mansion": 10}

        self.building_names = {
            "academy": "g22",
            "bakery": "g9",
            "barracks": "g19",
            "brickyard": "g6",
            "cranny": "g23",
            "embassy": "g18",
            "grain mill": "g8",
            "granary": "g11",
            "hero's mansion": "g37",
            "iron foundry": "g7",
            "main building": "g15",
            "marketplace": "g17",
            "rally point": "g16",
            "residence": "g25",
            "sawmill": "g5",
            "smithy": "g13",
            "stable": "g20",
            "stonemason": "g34",
            "town hall": "g24",
            "treasury": "g27",
            "wall": "g31Top",
            "warehouse": "g10",
            "workshop": "g21"
        }
        self.building_names_inverse = {}
        for key in self.building_names:
            self.building_names_inverse[self.building_names[key]] = key

    def parser(self, el_id, unicode=False):
        current_resource_raw = self.container.driver.find_element_by_id(el_id).text
        if unicode:
            current_resource_raw = current_resource_raw[1:][:-1]
        if '.' in current_resource_raw:
            current_resource = current_resource_raw.split('.')
        elif ' ' in current_resource_raw:
            current_resource = current_resource_raw.split(' ')
        else:
            current_resource = [current_resource_raw]
        current_resource_value = 0
        for i in current_resource:
            current_resource_value += int(i) * 10 ** (3 * (len(current_resource) - (current_resource.index(i) + 1)))
        return int(current_resource_value)

    # def check_building_info(self):
    #     # single building
    #     self.log.debug("Checking building info")
    #     self.helper.dorf_fuse("n2")
    #
    #     # no elements case
    #     if not len(self.buildings_dict):
    #         self.set_buildings_info_to_file_current_village()
    #
    #     current_buildings_obj = self.container.driver.find_elements_by_class_name("colorLayer")
    #     # current_buildings_locations =

    def get_building_name_from_class(self, name_class):
        # self.log.debug("Getting building's name of class {}".format(name_class))
        for building_name in self.buildings_dict:
            if name_class == self.buildings_dict[building_name].name_class:
                return building_name
        self.log.debug("No name found for class {}".format(name_class))

    def get_building_name_from_location(self, name_location):
        # self.log.debug("Getting building's name of location {}".format(name_location))
        for building_name in self.buildings_dict:
            if name_location == self.buildings_dict[building_name].name_location:
                return building_name
        self.log.debug("No name found for location {}".format(name_location))

    def read_buildings_str_list_from_file(self):
        self.log.debug("Reading buildings from a file")
        villages_buildings_list = []
        with open("buildings_{}_{}.txt".format(self.container.country, self.container.server), 'r') as file:
            while True:
                village_str = file.readline().replace('\n', '')
                if village_str:
                    villages_buildings_list.append(village_str)
                else:
                    return villages_buildings_list

    def set_buildings_info_to_file_current_village(self, building=None, file_exists=True):
        self.log.debug("Setting buildings' info to a file")
        if file_exists:
            villages_buildings_list = self.read_buildings_str_list_from_file()
            self.log.debug("Buildings list from file: \n{}".format('\n'.join(villages_buildings_list)))
        else:
            villages_buildings_list = None
            self.log.debug("No buildings list file yet.")

        self.helper.dorf_fuse("n2")
        str_current_village_to_write = "{}:".format(self.village_name)
        all_buildings = self.container.driver.find_elements_by_class_name("colorLayer")
        buildings_full_class = [x.get_attribute("class").split(' ')[-1] for x in all_buildings]
        self.log.debug("Full classes of buildings: {}".format(buildings_full_class))
        buildings_locations = [x.split(' ')[-1] for x in buildings_full_class]
        self.log.debug("Buildings locations: {}".format(buildings_locations))
        building_websites = ["{}/build.php?id={}".format(self.container.website, location[3:]) for location in
                             buildings_locations]
        for index in range(len(building_websites)):
            self.container.driver.get(building_websites[index])
            building_class_name = self.container.driver.find_element_by_id("build").get_attribute("class").split(' ')[0]
            building_class_name = building_class_name.replace("id", '')
            # in case it is a wall
            if building_class_name == "g31":  # OR MAYBE g31Top?????
                # building_class_name = self.buildings_dict["wall"].name_class
                building_class_name = "g31Top"
            str_current_village_to_write += "{},{},{};".format(self.building_names_inverse[building_class_name],
                                                               building_class_name,
                                                               buildings_locations[index])
        str_current_village_to_write = str_current_village_to_write[:-1] + '\n'

        found = False
        if villages_buildings_list is not None:
            for index in range(len(villages_buildings_list)):
                if self.village_name in villages_buildings_list[index]:
                    villages_buildings_list[index] = str_current_village_to_write
                    with open("buildings_{}_{}.txt".format(self.container.country, self.container.server), 'w') as file:
                        almost_final_str = '\n'.join(villages_buildings_list) + '\n'
                        final_str = almost_final_str.replace("\n\n", "\n")
                        file.write(final_str)
                    found = True
                    self.log.debug("The new building list file: \n{}".format(final_str))
        if not found:
            with open("buildings_{}_{}.txt".format(self.container.country, self.container.server), 'a') as file:
                file.write(str_current_village_to_write)

    # def set_buildings_info_all_villages(self, building=None):
    #     self.log.debug("Setting buildings' info to a file")
    #     with open("buildings_{}_{}.txt".format(self.container.country, self.container.server), 'w') as file:
    #         for village in village_management.Village().cycle_an_action_through_villages():
    #             file.write("{}:".format(self.village_name))
    #             self.helper.dorf_fuse("n2")
    #             all_buildings = self.container.driver.find_elements_by_class_name("colorLayer")
    #             buildings_locations = [x.get_attribute("class").split(' ')[-1] for x in all_buildings]
    #             self.log.debug("Buildings locations: {}".format(buildings_locations))
    #             building_websites = ["{}/build.php?id={}".format(self.container.website, location[3:]) for location in buildings_locations]
    #             for index in range(len(building_websites)):
    #                 self.container.driver.get(building_websites[index])
    #                 building_class_name = self.container.driver.find_element_by_id("build").get_attribute("class").split(' ')[0]
    #                 building_class_name = building_class_name.replace("id", '')
    #                 # in case it is a wall
    #                 if building_class_name == "g31":
    #                     building_class_name = self.building_names["wall"]
    #                 file_input_str = "{},{},{}".format(self.building_names_inverse[building_class_name], building_class_name,
    #                                                    buildings_locations[index])
    #                 file.write(file_input_str)
    #                 self.log.debug(file_input_str)
    #                 if index + 1 != len(building_websites):
    #                     file.write(';')
    #             file.write('\n')

    def get_building_info_from_file(self, building=None):
        self.log.debug("Getting building info from a file")

        try:
            villages_buildings_list = self.read_buildings_str_list_from_file()
            for village_str in villages_buildings_list:
                # print("cur vill name: {}; village str: {}".format(self.village_name, village_str))
                if self.village_name in village_str:
                    buildings_str = village_str.split(':')[1].split(';')

                    # now lets split each building from "... , ... , ..." to [... , ... , ...]
                    buildings_list = [[buildings_str[i].split(',')[j] for j in range(len(buildings_str[i].split(',')))]
                                      for i in range(len(buildings_str))]
            try:
                buildings = [Building(buildings_list[i][0], buildings_list[i][1], buildings_list[i][2]) for i in
                             range(len(buildings_list))]
            except Exception as ex:
                self.log.exception(ex)
                self.log.error(
                    "Error while reading 'buildings_{}_{}.txt'. Updating this file".format(self.container.country,
                                                                                           self.container.server))
                self.set_buildings_info_to_file_current_village()
                self.log.info("Starting over with new file 'buildings_{}_{}.txt'".format(self.container.country,
                                                                                         self.container.server))
                raise
            for building in buildings:
                self.buildings_dict[building.name_label] = building
        except FileNotFoundError:
            self.log.error("No such village {} in {}".format(self.village_name,
                                                             "buildings_{}_{}.txt".format(self.container.country,
                                                                                          self.container.server), 'r'))
            self.set_buildings_info_to_file_current_village(file_exists=False)

    def get_current_amount_of_resources(self):
        self.log.debug("Getting current amount of resources")
        # self.helper.dorf_fuse("n1")

        self.current_wood = self.parser("l1")
        self.current_clay = self.parser("l2")
        self.current_iron = self.parser("l3")
        self.current_grain = self.parser("l4")
        self.current_resources = [self.current_wood, self.current_clay, self.current_iron, self.current_grain]
        self.log.debug("Current resources: {}".format(self.current_resources))

    def get_current_production(self):
        self.log.debug("Getting current amount of production")
        # self.helper.dorf_fuse("n1")

        production_table = self.container.driver.find_element_by_id("production")
        current_production_obj = production_table.find_elements_by_class_name("num")
        self.production_wood = int(current_production_obj[0].text[1:][:-1])
        self.production_clay = int(current_production_obj[1].text[1:][:-1])
        self.production_iron = int(current_production_obj[2].text[1:][:-1])
        self.production_grain = int(current_production_obj[3].text[1:][:-1])
        self.current_production = [self.production_wood, self.production_clay, self.production_iron,
                                   self.production_grain]
        self.log.debug("Current production: {}".format(self.current_production))

    def get_warehouse_granary_attributes(self):
        self.log.debug("Getting warehouse and granary attributes")
        self.helper.dorf_fuse("n2")
        self.stock_warehouse = self.parser("stockBarWarehouse", True)
        self.stock_granary = self.parser("stockBarGranary", True)

        if self.get_building_level('warehouse') != 20:
            # go to warehouse
            warehouse = self.container.driver.find_element_by_class_name(self.buildings_dict["warehouse"].name_class)
            warehouse.click()

            WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((
                By.CLASS_NAME, "clocks")))

            self.build_time_warehouse_str = self.container.driver.find_element_by_class_name("clocks").text
            self.build_time_warehouse_list = self.build_time_warehouse_str.split(':')
            self.build_time_warehouse = [int(x) for x in self.build_time_warehouse_list]
            self.build_time_warehouse_seconds = self.build_time_warehouse[0] * 3600 + self.build_time_warehouse[1] * 60 \
                                                + self.build_time_warehouse[2]

        # wait until the page (villageBuildings element) loads
        self.helper.dorf_fuse("n2")

        if self.get_building_level('granary') != 20:
            # go to granary
            granary = self.container.driver.find_element_by_class_name(self.buildings_dict["granary"].name_class)
            granary.click()

            WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((
                By.CLASS_NAME, "clocks")))

            self.build_time_granary_str = self.container.driver.find_element_by_class_name("clocks").text
            self.build_time_granary_list = self.build_time_granary_str.split(':')
            self.build_time_granary = [int(x) for x in self.build_time_granary_list]
            self.build_time_granary_seconds = self.build_time_granary[0] * 3600 + self.build_time_granary[1] * 60 \
                                              + self.build_time_granary[2]

    def upgrade_stock(self, building):
        self.log.debug("Upgrading stock: {}".format(building))
        # wait until the page (villageBuildings element) loads
        self.helper.dorf_fuse("n2")

        stock_building_current = self.container.driver.find_element_by_class_name(
            self.buildings_dict[building].name_location)
        if 'good' in stock_building_current.get_attribute("class"):
            stock_building_current.click()
        else:
            return

        self.log.debug("Upgrading {}".format(building))
        self.helper.press_upgrade_button()

    def check_if_stock_needs_an_upgrade(self):
        try:
            self.stock_warehouse
        except AttributeError:
            self.get_warehouse_granary_attributes()

        try:
            self.current_resources
        except AttributeError:
            self.get_current_amount_of_resources()

        try:
            self.current_production
        except AttributeError:
            self.get_current_production()

        self.log.debug("Checking if stock needs an upgrade")
        # max_warehouse_resource_type = max(self.current_production[:3])
        # max_warehouse_resource_type_index = self.current_production.index(max_warehouse_resource_type)
        if self.get_building_level('warehouse') != 20:
            if (self.current_production[0] * self.container.stock_fill_up_time_limit > self.stock_warehouse or
                self.current_production[0] * (self.build_time_warehouse_seconds + self.container.sleep_time) / 3600 +
                self.current_resources[0] > self.stock_warehouse) \
                    or (self.current_production[1] * self.container.stock_fill_up_time_limit > self.stock_warehouse or
                        self.current_production[1] * (
                                self.build_time_warehouse_seconds + self.container.sleep_time) / 3600 +
                        self.current_resources[1] > self.stock_warehouse) \
                    or (self.current_production[2] * self.container.stock_fill_up_time_limit > self.stock_warehouse or
                        self.current_production[2] * (
                                self.build_time_warehouse_seconds + self.container.sleep_time) / 3600 +
                        self.current_resources[2] > self.stock_warehouse):
                self.upgrade_stock('warehouse')
        # if currently not upgrading
        if self.get_building_level('granary') != 20:
            if self.current_production[3] * self.container.stock_fill_up_time_limit > self.stock_granary or \
                    self.current_production[3] * (self.build_time_granary_seconds + self.container.sleep_time) / 3600 + \
                    self.current_resources[3] > self.stock_granary:
                self.upgrade_stock('granary')

    def upgrade_resource_field(self, kind):
        self.log.debug("Upgrading resource field of {}".format(kind))
        # self.helper.dorf_fuse("n1")

        all_resource_fields = self.container.driver.find_elements_by_class_name(kind)
        all_upgradable_resource_fields = []
        for field in all_resource_fields:
            if "good" in field.get_attribute("class"):
                all_upgradable_resource_fields.append(field)
        least_lvl_field = None
        for good_field in all_upgradable_resource_fields:
            if good_field.find_element_by_class_name("labelLayer").text == '':
                least_lvl_field = good_field
                break
            if least_lvl_field is None:
                least_lvl_field = good_field
            else:
                if int(good_field.find_element_by_class_name("labelLayer").text) < \
                        int(least_lvl_field.find_element_by_class_name("labelLayer").text):
                    least_lvl_field = good_field
        if least_lvl_field is not None:
            # if least_lvl_field.find_element_by_class_name("labelLayer").text != '10':
            self.log.debug("Upgrading resource field of kind {}".format(kind))
            # self.container.driver.execute_script("window.scrollTo(0, 0)")
            # time.sleep(1)
            # least_lvl_field.click()
            ActionChains(self.container.driver).move_to_element(least_lvl_field).click(least_lvl_field).perform()
            self.helper.press_upgrade_button()

    def upgrade_resource(self, all_to_max=False, max_level=10):
        self.log.debug("Checking if resources needs to be upgraded")
        try:
            self.current_resources
        except AttributeError:
            self.get_current_amount_of_resources()
        try:
            self.current_production
        except AttributeError:
            self.get_current_production()
        # self.helper.dorf_fuse("n1")

        resource_class_obj = ["gid1", "gid2", "gid3", "gid4"]
        resource_class_dict = {}
        for i in range(4):
            resource_class_dict[resource_class_obj[i]] = self.current_resources[i]
        upgradable_fields = self.container.driver.find_elements_by_class_name("good")
        good_fields = {}
        for res_type in resource_class_obj:
            # hold grain production low
            if res_type == "gid4":
                if not all_to_max:
                    if (self.current_production[0] + self.current_production[1] + self.current_production[2]) \
                            / self.current_production[3] < 2 * 3:
                        continue

            for field_element in upgradable_fields:
                if res_type in field_element.get_attribute("class"):
                    field_level = int(field_element.get_attribute("class").split(' ')[-1].replace("level", ''))
                    if field_level < max_level:
                        good_fields[res_type] = self.current_resources[int(res_type[-1]) - 1]
                        break

        # upgrade a kind with least resources present
        if good_fields:
            name = min(good_fields, key=good_fields.get)
            self.upgrade_resource_field(name)

    def get_building_level(self, building, already_in_dorf2=False):
        self.log.debug("Getting level of {}".format(building))
        if not already_in_dorf2:
            self.helper.dorf_fuse("n2")
        try:
            target_obj = self.container.driver.find_element_by_class_name(self.buildings_dict[building].name_class)
        except (selenium.common.exceptions.NoSuchElementException, KeyError):  # building is not present yet
            return 0
            # self.build_new_building(building)
        alt = target_obj.get_attribute("alt")
        alt_parse = alt.split("span")[1]
        current_level = ""
        for char in alt_parse:
            if char in string.digits:
                current_level += char
        return int(current_level)

    def get_all_building_levels(self):
        self.log.debug("Getting level of all buildings in {}".format(self.village_name))
        self.helper.dorf_fuse("n2")
        target_objs = self.container.driver.find_elements_by_class_name("building")
        targets_classes = []
        for target in target_objs:
            targets_classes.append(target.get_attribute("class").split(' ')[1].replace('b', '').replace('e', ''))
        targets_classes = [target_class for target_class in targets_classes if target_class != "iso"]
        wall = self.container.driver.find_elements_by_class_name("aid40")
        wall_level = int(wall.find_elements_by_class_name("labelLayer").text)
        # if iso: continue
        if wall_level:
            pass

            alt = target.get_attribute("alt")
            alt_parse = alt.split("span")[1]
            current_level = ""
            for char in alt_parse:
                if char in string.digits:
                    current_level += char
        return int(current_level)

    def build_new_building(self, building_label):
        self.log.debug("Trying to build a new building: {}".format(building_label))
        self.helper.dorf_fuse("n2")
        # TODO: implement empty place elswhere
        # new_place = self.container.driver.find_element_by_xpath("//area[@alt='Byggeplass']").get_attribute("href")  # .no
        # new_place = self.container.driver.find_element_by_xpath("//area[@alt='Gradbeno mesto']").get_attribute("href")  # .si

        if building_label == "wall":
            try:
                self.container.driver.get(self.container.website + "/build.php?id=40").click()
                self.helper.press_upgrade_button(new=True)
            except Exception as ex:
                self.log.exception(ex)
                return False
        elif building_label == "rally point":
            try:
                self.container.driver.get(self.container.website + "/build.php?id=39").click()
                self.helper.press_upgrade_button(new=True)
            except Exception as ex:
                self.log.exception(ex)
                return False
        else:
            empty_place_name = self.container.driver.find_element_by_xpath("//img[@class='iso']").get_attribute("alt")  # .si
            new_place = self.container.driver.find_element_by_xpath("//area[@alt='{}']".format(empty_place_name)).get_attribute("href")  # .si
            self.container.driver.get(new_place)
            try:
                new_building = self.container.driver.find_element_by_id(
                    "contract_building{}".format(self.buildings_dict[building_label].name_class[1:]))
                self.helper.press_upgrade_button(new=new_building)
            except:
                self.container.driver.find_element_by_class_name("military").click()
                try:
                    new_building = self.container.driver.find_element_by_id(
                        "contract_building{}".format(self.buildings_dict[building_label].name_class[1:]))
                    self.helper.press_upgrade_button(new=new_building)
                except:
                    self.container.driver.find_element_by_class_name("resources").click()
                    try:
                        new_building = self.container.driver.find_element_by_id(
                            "contract_building{}".format(self.buildings_dict[building_label].name_class[1:]))
                        self.helper.press_upgrade_button(new=new_building)
                    except:
                        self.log.info("Can't build new building - {}".format(building_label))
                        return False
        return True

    def upgrade_building(self, building_label):
        self.log.debug("Upgrading {}".format(building_label))
        self.helper.dorf_fuse("n2")
        building = self.container.driver.find_element_by_class_name(self.buildings_dict[building_label].name_location)
        ActionChains(self.container.driver).move_to_element(building).click(building).perform()

        self.helper.press_upgrade_button()

    def scan_for_allowed_new_buildings(self):

        def check_buildings_obj_at_current_page():
            for building_obj in all_buildings_at_page:
                if len(building_obj.find_elements_by_class_name("green")):
                    building_class = 'g' + ''.join(
                        [char for char in building_obj.get_attribute("id") if char.isdigit()])
                    self.buildings_allowed_to_create.append(self.building_names_inverse[building_class])
                    # self.buildings_allowed_to_create.append(self.get_building_name_from_class(building_class))

        self.log.debug("Scanning allowed to build new buildings in the village {}".format(self.village_name))
        self.helper.dorf_fuse("n2")
        self.buildings_allowed_to_create = []
        # new_place = self.container.driver.find_element_by_xpath("//area[@alt='Gradbeno mesto']").get_attribute("href")  # .si
        new_place = self.container.driver.find_element_by_xpath("//area[@alt='Spazio edificabile']").get_attribute(
            "href")  # .it
        self.container.driver.get(new_place)
        for i in range(3):
            try:
                all_buildings_at_page = self.container.driver.find_elements_by_class_name("contractWrapper")
                check_buildings_obj_at_current_page()
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                self.log.exception("Got stale exception in {}".format(self.village_name))
        self.container.driver.find_element_by_class_name("military").click()
        for i in range(3):
            try:
                all_buildings_at_page = self.container.driver.find_elements_by_class_name("contractWrapper")
                check_buildings_obj_at_current_page()
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                self.log.exception("Got stale exception in {}".format(self.village_name))
        self.container.driver.find_element_by_class_name("resources").click()
        for i in range(3):
            try:
                all_buildings_at_page = self.container.driver.find_elements_by_class_name("contractWrapper")
                check_buildings_obj_at_current_page()
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                self.log.exception("Got stale exception in {}".format(self.village_name))

    def build_plan(self, building_level_dict):
        all_built = True
        self.log.debug("Using building plan: {}".format(building_level_dict))
        if self.ongoing_build_in_dorf2():
            return False
        for building in building_level_dict:
            current_building_level = self.get_building_level(building, already_in_dorf2=True)
            self.log.debug("Current level of {} is {}".format(building, current_building_level))
            if building_level_dict[building] > current_building_level:
                all_built = False
                if current_building_level:
                    if building not in self.buildings_dict:
                        # either not yet built or buildings' file needs to be upgraded
                        if self.build_new_building(building):
                            break
                        else:
                            self.set_buildings_info_to_file_current_village()
                            self.get_building_info_from_file()
                    building_location = self.buildings_dict[building].name_location
                    building_obj = self.container.driver.find_element_by_class_name(building_location)
                    building_class = building_obj.get_attribute("class")
                    if "good" in building_class:
                        self.upgrade_building(building)
                        break
                else:
                    try:
                        self.buildings_allowed_to_create
                    except AttributeError:
                        self.scan_for_allowed_new_buildings()
                    finally:
                        if building in self.buildings_allowed_to_create:
                            if self.build_new_building(building):
                                break
        return all_built

    def current_builds(self):
        self.helper.dorf_fuse("n1")
        total_builds = len(self.container.driver.find_elements_by_class_name("buildDuration"))
        self.log.debug("Current builds: {}".format(total_builds))
        return total_builds

    def ongoing_build_in_dorf2(self):
        self.helper.dorf_fuse("n2")
        return len(self.container.driver.find_elements_by_class_name("underConstruction"))

    def start_upgrades(self):
        # self.set_buildings_info_current_village()
        if self.current_builds() < 3:  # TODO: tikrinti atskirai resus ir kaima, nes su pliusu galima statyti 3 pastatus

            # self.upgrade_resource(all_to_max=True)
            # RESOURCES:
            self.helper.dorf_fuse("n1")
            self.get_current_amount_of_resources()
            self.get_current_production()
            # if village_management.VillageControl(self.container).get_active_village_name() == "sirvys":
            self.upgrade_resource()

            if not self.ongoing_build_in_dorf2():

                #############################################
                self.helper.dorf_fuse("n2")
                self.get_building_info_from_file()
                # current buildings and buildings got from file must match
                current_buildings_obj = self.container.driver.find_elements_by_class_name("building")
                current_buildings_g_class = [building.get_attribute("class").split(' ')[1].replace('b', '') for building
                                             in current_buildings_obj]
                # wall
                if self.container.driver.find_elements_by_class_name("g31Top"):
                    current_buildings_g_class.append("g31Top")

                #
                current_buildings_filtered = []
                for building_class in current_buildings_g_class:
                    if building_class != "iso":
                        current_buildings_filtered.append(self.building_names_inverse[building_class])

                #
                current_buildings = []
                for building_class in current_buildings_g_class:
                    if building_class != "iso":
                        # self.log.debug("{}: {}".format(self.village_name, building_class))
                        current_buildings.append(self.building_names_inverse[building_class])
                        # current_buildings.append(self.get_building_name_from_class(building_class))
                #
                for i in self.buildings_dict:
                    if i not in current_buildings:
                        self.set_buildings_info_to_file_current_village()
                        return
                for i in current_buildings:
                    if i not in self.buildings_dict:
                        self.set_buildings_info_to_file_current_village()
                        return
                # #############################################
                #
                done_start = self.build_plan(self.upgrade_plan_start)
                if done_start:
                    done_min = self.build_plan(self.upgrade_plan_sirvys)
                #     if done_min:
                #         done_storage = self.build_plan(self.upgrade_plan_storage)
                #         if done_storage:
                #             done_med = self.build_plan(self.upgrade_plan_med)
                pass
