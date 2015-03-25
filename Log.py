
import logging

import Session

class Log:
    @staticmethod
    def format(msg):
        return("%s %s" % (Session.id, msg))

    @staticmethod
    def info(msg):
        logging.info(Log.format(msg))

    @staticmethod
    def warning(msg):
        logging.warning(Log.format(msg))

    @staticmethod
    def error(msg):
        logging.error(Log.format(msg))

    @staticmethod
    def critical(msg):
        logging.critical(Log.format(msg))

