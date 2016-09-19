import logging
import os
import time
import subprocess
import datetime

class Poller(object):
    FILE_DOES_NOT_EXIST = -1
    FILES_NOT_READY = 0
    FILES_COMPLETE = 1

    def __init__(self, property_file='/Users/jaska/Work/JDA_Guess/test/Guess.properties'):

        import ConfigParser
        cfg = ConfigParser.ConfigParser()
        cfg.read(property_file)

        logging.basicConfig(level=eval("logging.%s" % cfg.get("POLLER", "log_level")))
        fh = logging.FileHandler(cfg.get("POLLER", "log_file"))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        self.logger = logging.getLogger("poller")
        self.logger.addHandler(fh)
        self.logger.info("Reading configuration from %s" % property_file)

        self.filename = cfg.get("POLLER", "status_file")
        self.import_status_file = cfg.get("POLLER", "import_status_file")

        self.script = cfg.get("POLLER", "script")
        self.sleep_time = int(cfg.get("POLLER", "sleep_time"))
        self.msg_complete = cfg.get("POLLER", "msg_complete")
        self.next_run_time = None

        self.start_time = time.strptime(cfg.get("POLLER", "start_time"), '%H:%M')
        self.start_time = datetime.time(self.start_time.tm_hour, self.start_time.tm_min)
        self.duration = int(cfg.get("POLLER", "duration"))

    @property
    def is_active(self):
        start_time = datetime.datetime.combine(datetime.datetime.today(), self.start_time)
        end_time = start_time + datetime.timedelta(hours=self.duration)
        now = datetime.datetime.now()
        logging.debug("Start time: %s" % self.start_time)
        logging.debug("End time: %s (duration: %s hours)" % (end_time, self.duration))
        logging.debug("Current time: %s" % now)

        active = start_time <= now <= end_time
        logging.debug("Is active: %s" % active)

        if not active:
            if now < start_time:
                self.next_run_time = start_time
            else:
                self.next_run_time = start_time + datetime.timedelta(days=1)

        return active

    def poll(self):
        if not os.path.exists(self.filename):
            logging.info("Guess status file does not exist: %s" % self.filename)
            return self.FILE_DOES_NOT_EXIST

        if os.path.exists(self.import_status_file) and \
                        os.path.getmtime(self.import_status_file) > os.path.getmtime(self.filename):
            logging.info("Guess status file has not been updated since last import. Waiting for next update.")
            return self.FILES_NOT_READY

        with open(self.filename, 'r') as f:
            message = f.readline().rstrip().lower()
            if message == self.msg_complete:
                logging.info("Guess status file indicates file upload is complete.")
                return self.FILES_COMPLETE

            logging.info("Guess status file indicates files are not ready.")
            return self.FILES_NOT_READY

    def run(self, my_scheduler=None):
        if my_scheduler is None:
            import sched
            my_scheduler = sched.scheduler(time.time, time.sleep)
            my_scheduler.enter(self.sleep_time, 0, self.run, [my_scheduler])
            my_scheduler.run()

        if self.is_active:
            logging.info("Poller is active, monitoring file: %s" % self.filename)

            rv = self.poll()
            logging.debug("Poll returned value %d" % rv)
            if rv == self.FILES_COMPLETE:
                logging.info("Guess file upload complete -> start pricer import")
                self.run_script()
                with open(self.import_status_file, 'a') as f:
                    f.write("Import script finished at %s" % time.asctime( time.localtime(time.time())))
            else:
                logging.info("Poller sleeping for %d seconds" % self.sleep_time)

                my_scheduler.enter(self.sleep_time, 0, self.run, [my_scheduler])
        else:
            logging.info("Poller not active, next round at %s" % self.next_run_time)
            my_scheduler.enterabs(time.mktime(self.next_run_time.timetuple()), 0, self.run, [my_scheduler])

    def run_script(self):
        logging.info("Running command/script: %s" % self.script)
        start_time = time.time()
        rv = subprocess.call(self.script.split(" "))
        logging.info("Completed script in %d seconds with return value: %s" % ((time.time() - start_time), rv))

if __name__ == '__main__':
    import sys
    if len(sys.argv) <> 2:
        print "Usage: %s <property file>" % sys.argv[0]
        raise SystemExit

    p = Poller(sys.argv[1])
    try:
        p.run()
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")