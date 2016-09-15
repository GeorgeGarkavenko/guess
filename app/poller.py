import logging
import os
import time

import subprocess

logging.basicConfig(level=logging.INFO)

class Poller(object):
    FILE_DOES_NOT_EXIST = -1
    FILES_NOT_READY = 0
    FILES_COMPLETE = 1

    def __init__(self, property_file='/Users/jaska/Work/JDA_Guess/test/Guess.properties'):
        import ConfigParser
        cfg = ConfigParser.ConfigParser()
        cfg.read(property_file)

        self.filename = cfg.get("POLLER", "status_file")
        self.script = cfg.get("POLLER", "script")
        self.sleep_time = int(cfg.get("POLLER", "sleep_time"))
        self.msg_complete = cfg.get("POLLER", "msg_complete")


    def poll(self):
        if not os.path.exists(self.filename):
            logging.info("Guess status file does not exist: %s" % self.filename)
            return self.FILE_DOES_NOT_EXIST

        with open(self.filename, 'r') as f:
            message = f.readline().rstrip().lower()
            if message == self.msg_complete:
                return self.FILES_COMPLETE
            return self.FILES_NOT_READY

    def run(self):
        logging.info("Starting to monitor file: %s" % self.filename)
        while True:
            rv = self.poll()
            if rv == self.FILES_COMPLETE:
                logging.info("Guess file upload complete -> start pricer import")
                break
            logging.info("Guess file upload not complete, sleeping for %d seconds" % self.sleep_time)
            time.sleep(self.sleep_time)

        self.run_script()

    def run_script(self):
        logging.info("Running command/script: %s" % self.script)
        start_time = time.time()
        rv = subprocess.call(self.script.split(" "))
        logging.info("Completed script in %d seconds with return value: %s" % ((time.time() - start_time), rv))
        print "RV = %s" % rv

if __name__ == '__main__':
    import sys
    p = Poller(sys.argv[1])
    try:    p.run()
    except KeyboardInterrupt:
        print "STOPPED"