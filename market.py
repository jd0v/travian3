import time
import os
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import village_management
import selenium
from selenium.common.exceptions import NoSuchElementException
import build


class Market:
    def __init__(self, container):
        self.container = container
        self.log = self.container.log
        self.helper = self.container.helper
        self.village_control = village_management.VillageControl(self.container)
        self.build = build.Build(self.container)
        self.troop_villages = ["JD",]
        self.villages_under_development = ["nps",]
        self.farms = ["sirvys",]
    
    def send_resources(self, amount_list):
        village_name = self.village_control.get_active_village_name()
        # 1. find village with enough resources
        resources_of_the_farms = []
        leftover = amount_list[:]
        for farm in self.farms:
            self.village_control.change_village(farm)

            #get resources
            self.build.get_current_amount_of_resources()
            resources_of_the_farms.append(self.build.current_resources)
            leftover -= self.build.current_resources

            #if enough resources
            enough_resources_in_this_farm = True
            for idx in range(4):
                leftover[idx] -= self.build.current_resources[idx]
                if leftover[idx] > 0:
                    enough_resources_in_this_farm = False

            if enough_resources_in_this_farm:
                break

        if enough_resources_in_this_farm:
            pass
            #do
            #else
            #count the amount missing and go to the other village
        # 2. send from it
        pass
