from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import village_management
from selenium.webdriver.common.action_chains import ActionChains


class TroopMaker:

    def __init__(self, container):
        self.troops = {
            "legionnaire": "t1",
            "praetorian": "t2",
            "imperian": "t3",
            "equites legati": "t4",
            "equites imperatoris": "t5",
            "equites caesaris": "t6",
            "battering ram": "t7",
            "fire catapult": "t8",
            "senator": "t9",
            "settler": "t10",
        }
        self.container = container
        self.log = self.container.log
        self.helper = self.container.helper
        self.village_control = village_management.VillageControl(self.container)
        self.min_time = 1200

    def make_troops(self, troop_kind):
        # self.helper.dorf_fuse("n2")
        self.container.driver.get(self.container.website + "/dorf2.php")

        building = "barracks" if troop_kind in ["legionnaire", "praetorian", "imperian"] else "stable"

        # self.village_control.change_village(village_management.VillagesTypes().OFF)
        barracks_obj = self.container.driver.find_element_by_class_name(self.container.building_names[building])
        ActionChains(self.container.driver).move_to_element(barracks_obj).click(barracks_obj).perform()

        try:
            under_progress = self.container.driver.find_element_by_class_name("under_progress")
            time_left_list = under_progress.find_elements_by_class_name("timer")
            time_left_obj = time_left_list[-2]
            time_left_str = time_left_obj.get_attribute("value")
            time_left = int(time_left_str)
        except:
            time_left = 0

        if time_left < self.min_time:
            self.log.debug("Need to make more troops in {}".format(building))
            single_troop_build_time_tmp = self.container.driver.find_elements_by_class_name("duration")
            single_troop_build_time_tmp = single_troop_build_time_tmp[2].text
            single_troop_build_time_tmp = single_troop_build_time_tmp.split(':')
            single_troop_build_time_tmp = [int(x) for x in single_troop_build_time_tmp]
            single_troop_build_time = 0
            single_troop_build_time += single_troop_build_time_tmp[0] * 3600 + single_troop_build_time_tmp[1] * 60 + \
                                       single_troop_build_time_tmp[2]
            number_to_build = int((self.min_time - time_left)/single_troop_build_time) + 1
            input = self.container.driver.find_element_by_name(self.troops[troop_kind])
            input.clear()
            input.send_keys(number_to_build)
            start_training_button = self.container.driver.find_element_by_class_name("startTraining")
            ActionChains(self.container.driver).move_to_element(start_training_button).click(start_training_button).perform()

            # CHECKING IF TROOPS WERE BUILT
            under_progress = self.container.driver.find_element_by_class_name("under_progress")
            time_left_list = under_progress.find_elements_by_class_name("timer")
            time_left_obj = time_left_list[-2]
            time_left_str = time_left_obj.get_attribute("value")
            time_left = int(time_left_str)
            if time_left < self.min_time:
                number_to_build = 1
                # number_to_build = self.container.driver.find_element_by_xpath('//a[@href="https://tx3.czsk.travian.com/build.php?id=20#"]').text
                input = self.container.driver.find_element_by_name(self.troops[troop_kind])
                input.clear()
                input.send_keys(number_to_build)
                start_training_button = self.container.driver.find_element_by_class_name("startTraining")
                ActionChains(self.container.driver).move_to_element(start_training_button).click(
                    start_training_button).perform()

    # def make_in_stable(self):
    #     self.helper.dorf_fuse("n2")
    #
    #     village_management.VillageControl(self.container).change_village(village_management.VillagesTypes.OFF)
    #
    #     stable_building = self.container.driver.find_element_by_class_name(self.container.building_names["stable"])
    #     ActionChains(self.container.driver).move_to_element(stable_building).click(stable_building).perform()
    #
    #     try:
    #         under_progress = self.container.driver.find_element_by_class_name("under_progress")
    #         time_left_list = under_progress.find_elements_by_class_name("timer")
    #         time_left_obj = time_left_list[-2]
    #         time_left_str = time_left_obj.get_attribute("value")
    #         time_left = int(time_left_str)
    #     except:
    #         time_left = 0
    #
    #     if time_left < 2222:
    #         self.log.debug("Need to make more troops in stable")
    #         single_troop_build_time_tmp = self.container.driver.find_elements_by_class_name("clocks")
    #         single_troop_build_time_tmp = single_troop_build_time_tmp[-1].text
    #         single_troop_build_time_tmp = single_troop_build_time_tmp.split(':')
    #         single_troop_build_time_tmp = [int(x) for x in single_troop_build_time_tmp]
    #         single_troop_build_time = 0
    #         single_troop_build_time += single_troop_build_time_tmp[0] * 3600 + single_troop_build_time_tmp[1] * 60 + \
    #                                    single_troop_build_time_tmp[2]
    #         number_to_build = int((2222 - time_left)/single_troop_build_time) + 1
    #
    #         max_allowed_number_to_build = int(self.container.driver.find_elements_by_xpath("//a[@href='#']")[-1].text)
    #
    #         input = self.container.driver.find_element_by_name("t5")
    #         input.clear()
    #         input.send_keys(min(number_to_build, max_allowed_number_to_build))
    #         start_training_button = self.container.driver.find_element_by_class_name("startTraining")
    #         ActionChains(self.container.driver).move_to_element(start_training_button).click(start_training_button).perform()
