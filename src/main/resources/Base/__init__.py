class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Base():


    @staticmethod
    def error(msg):
        print bcolors.FAIL + "ERROR: %s " % msg  + bcolors.ENDC

    @staticmethod
    def info(msg):
        print bcolors.OKBLUE + "INFO: %s" % msg + bcolors.ENDC

    @staticmethod
    def warning(msg):
        print bcolors.WARNING + "WARNING: %s" % msg + bcolors.ENDC

    @staticmethod
    def fatal(msg):
        print bcolors.FAIL + "FAIL: %s" %  msg + bcolors.ENDC