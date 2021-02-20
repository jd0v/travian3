import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class VillagesTypes:
    OFF = "JD"


class VillageControl:
    def __init__(self, container):
        self.container = container
        self.log = self.container.log
        self.helper = self.container.helper

        self.build_plan_start_done = False
        self.build_plan_min_done = False
        self.build_plan_med_done = False
        self.build_plan_adv_done = False
        pass

    def get_active_village_name(self):
        try:
            self.helper.fuse()

            village_list_box = self.container.driver.find_element_by_id("sidebarBoxVillagelist")
            active_village = village_list_box.find_element_by_class_name("active")
            return active_village.find_element_by_class_name("name").text
        except:
            self.log.error("Getting the name of current village error")
            return None  # todo: raise?

    def get_all_villages_names(self):
        try:
            try:
                self.helper.fuse()
            except Exception as ex:
                self.log.exception(ex)
            village_list_box = self.container.driver.find_element_by_id("sidebarBoxVillagelist")
            village_names_obj = village_list_box.find_elements_by_class_name("name")
            village_names = [village.text for village in village_names_obj]
            return village_names
        except:
            self.log.error("Getting the names of all villages error")
            return None

    def change_village(self, target):
        self.log.info("Changing village to {}".format(target))
        # todo: change if necessary; not always
        village_list_box = self.container.driver.find_element_by_id("sidebarBoxVillagelist")
        village_list = village_list_box.find_elements_by_class_name("name")
        for village in village_list:
            if village.text == target:
                village.click()
                return
        raise ValueError("No such village: {}".format(target))

    def cycle_an_action_through_villages(self):
        self.helper.fuse()

        village_list_box = self.container.driver.find_element_by_id("sidebarBoxVillagelist")
        village_list = village_list_box.find_elements_by_class_name("name")
        village_count = len(village_list)
        for village_index in range(village_count):
            village_list_box = self.container.driver.find_element_by_id("sidebarBoxVillagelist")
            village_list = village_list_box.find_elements_by_class_name("name")
            new_village_name = village_list[village_index].text
            self.change_village(new_village_name)
            self.log.debug("CURRENT VILLAGE: {}".format(new_village_name))
            yield

