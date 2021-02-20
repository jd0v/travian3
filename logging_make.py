import logging
import time


class Log:
    # def __init__(self, new_container=None):
    def __init__(self, container):
        # if new_container is not None:
        #     container = new_container

        # start logging
        self.log = logging.getLogger("mylog")
        date = time.strftime("%Y-%m-%d")
        # log_config = logging.FileHandler(r"C:\Users\Aidas\PycharmProjects\Travian\logs\TravianLog_" + str(date) + r".log")
        log_config = logging.FileHandler(r"TravianLog_{}_{}_{}.log".format(container.country, container.server, date))
        log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        log_config.setFormatter(log_formatter)
        self.log.addHandler(log_config)
        self.log.setLevel(logging.DEBUG)

        self.log.info("Logging started")
