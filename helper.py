from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class Helper:
    def __init__(self, container):
        self.container = container
        self.log = self.container.log
        self.reference_coordinates = self.container.reference_coordinates

    def get_current_dorf_id(self):
        for dorf in ["n{}".format(i) for i in range(1,8)]:
            dorf_obj = self.container.driver.find_element_by_id(dorf)
            if len(dorf_obj.find_elements_by_class_name("active")):
                return dorf

    def fuse(self, element="n1", by="id"):
        if by == "id":
            WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, element)))
        elif by == "class":
            WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, element)))
        else:
            raise ValueError("Wrong 'by' type.")

    def dorf_fuse(self, dorf):
        self.log.debug("Loading dorf: {}".format(dorf))
        abbreviations = {
            "n1":"/dorf1.php",
            "n2":"/dorf2.php",
            "n3":"/karte.php",
            "n4":"/statistiken.php",
        }
        website = self.container.website+abbreviations[dorf]
        self.container.driver.get(website)
        # WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, dorf)))
        # target = self.container.driver.find_element_by_id(dorf)
        # target.click()
        # WebDriverWait(self.container.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, dorf)))

    def press_upgrade_button(self, new=None):
        if new is not None:
            green = new.find_element_by_class_name("green")
        else:
            section1 = self.container.driver.find_element_by_class_name("section1")
            green = section1.find_element_by_class_name("green")
        green.find_element_by_class_name("addHoverClick").click()

    def distance_from_reference_point(self, coords):
        distance_x = coords[0] - self.reference_coordinates[0]
        distance_y = coords[1] - self.reference_coordinates[1]
        return (distance_x ** 2 + distance_y ** 2) ** 0.5

    # def unicode_parser(self, list):
    #     return [element for element in list]
