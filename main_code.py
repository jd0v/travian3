import os
import time
import selenium
import selenium.common
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import farming
import statistics
import build
import village_management
import troop_manager
import threading


# prevent pc from sleeping class
class WindowsInhibitor:
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self, container):
        self.container = container
        self.log = self.container.log

    def inhibit(self):
        import ctypes
        self.log.info("Preventing Windows from going to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS |
            WindowsInhibitor.ES_SYSTEM_REQUIRED)

    def uninhibit(self):
        import ctypes
        self.log.info("Allowing Windows to go to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS)


class TravianThread(threading.Thread):

    def __init__(self, container):
        threading.Thread.__init__(self)
        self.container = container
        self.log = self.container.log
        # self.nickname = nickname
        # self.password = password

    def preferences_maker(self):
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.cache.memory.capacity", 4000)
        fp.set_preference("browser.sessionhistory.max_entries", 2)
        fp.set_preference("browser.sessionhistory.max_total_viewers", 0)
        return fp

    def logscreen(self):

        # go to the self.log in page
        while True:
            try:
                self.log.info("Connecting to " + self.container.website)
                # self.container.driver.get(self.website)
                self.container.driver.get(self.container.website)
                break
            except selenium.common.exceptions.WebDriverException as ex:
                if 'Reached error page' not in ex.__str__():
                    self.log.error('Unhandled exception')
                    self.log.exception(ex)
                    break
                self.log.warning("Cant access the website. Retrying...")

        # give nickname and password if asked
        try:
            self.log.info("self.logging into account")
            self.login_name_field = self.container.driver.find_element_by_name("name")
            self.login_name_field.clear()
            self.login_name_field.send_keys(self.container.nickname)
            self.login_password_field = self.container.driver.find_element_by_name("password")
            self.login_password_field.clear()
            self.login_password_field.send_keys(self.container.password)
            self.login_button = self.container.driver.find_element_by_name("s1")
            self.login_button.send_keys(Keys.RETURN)
        except selenium.common.exceptions.NoSuchElementException:
            pass

    def main_loop(self):
        last_statistics_scan = -10**6
        last_oasis_info_scan = -10**6
        # farming.FarmingOases(self.container).get_all_oases_list_in_area(15)
        farming_control = farming.Farming(self.container)
        stats = statistics.Statistics(self.container)
        # farming.send_troops_from_file('farmlist.txt')

        # remove cookies
        try:
            self.container.driver.find_element_by_id("CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection").click()
        except:
            pass

        while True:
            try:
                self.container.driver.get(self.container.website + "/dorf1.php")

                # farming_control.perform_failed_attacks()
                # farming_control.farm_from_reports()
                # farming_control.farm_from_farmlist_file()

                if time.perf_counter() - last_oasis_info_scan > 3600:
                    farming.FarmingOases(self.container).get_oases_info()
                    last_oasis_info_scan = time.perf_counter()
                #
                # farming.FarmingOases(self.container).farm_from_oasis_info_file()
                # exit(999)

                # troop_manager.TroopMaker(self.container).make_troops("legionnaire")
                # troop_manager.TroopMaker(self.container).make_troops("equites imperatoris")

                # stats.get_friends_from_allies()
                # stats.get_all_nearby_players_names_list()
                # stats.scan_attack_and_deff_tab_info_of_nearby_players_list_to_file()

                # if time.perf_counter() - last_statistics_scan > 3600:
                #     stats.scan_deff_tab_info_of_nearby_players_list_to_file()
                #     last_statistics_scan = time.perf_counter()

                # for village in village_management.VillageControl(self.container).cycle_an_action_through_villages():
                #     try:  # so that still go through all the cities
                #         build.Build(self.container).start_upgrades()
                #     except Exception as ex:
                #         self.log.exception(ex)

                # if self.container.test_var.get():
                #     print("Success")
                for sleep_left in range(self.container.sleep_time, 0, -10):
                    self.log.info("Left to sleep: {}s".format(sleep_left))
                    time.sleep(10)

            except Exception as ex:
                self.log.exception("Unhandled Exception: {}".format(ex.__str__()))
                self.logscreen()

    def run(self):

        os_sleep = None
        # in Windows, prevent the OS from sleeping while we run
        if os.name == 'nt':
            os_sleep = WindowsInhibitor(self.container)
            os_sleep.inhibit()

        # fp = self.preferences_maker()
        
        # open mozilla ant travian webpage
        # self.container.driver = webdriver.Firefox()
        self.container.driver = webdriver.Chrome()
    
        # self.log in to travian
        self.logscreen()

        self.main_loop()

        if os_sleep:
            os_sleep.uninhibit()
        # driver.close()


if __name__ == "__main__":

    class Container:
        def __init__(self):
            # self.website = "https://tx3.travian.ru"
            self.website = "https://tse.europe.travian.com"
            self.server = self.website.split('.')[0].split("//")[-1]
            self.tx3 = self.server == "tx3"
            self.country = self.website.split('.')[-1]
            self.nickname = "SunTzu"
            self.password = "spreskpats"
            # self.password = "pafkp"
            self.sleep_time = 60
            self.timeout = 10
            # self.reference_coordinates = [3, -49]
            self.reference_coordinates = [-153, 157]
            self.ally = None
            self.stock_fill_up_time_limit = 3
            import logging_make
            self.log = logging_make.Log(self).log
            import helper
            self.helper = helper.Helper(self)
            self.building_names = {
                "academy": "g22",
                "bakery": "g9",
                "barracks": "g19",
                "brickyard": "g6",
                "cranny": "g23",
                "embassy": "g18",
                "grain mill": "g8",
                "granary": "g11",
                "iron foundry": "g7",
                "main building": "g15",
                "marketplace": "g17",
                "rally point": "g16",
                "residence": "g25",
                "stable": "g20",
                "sawmill": "g5",
                "smithy": "g13",
                "wall": "g31",
                "warehouse": "g10"
            }
            # self.building_names = {}

    t = TravianThread(Container())
    t.start()
