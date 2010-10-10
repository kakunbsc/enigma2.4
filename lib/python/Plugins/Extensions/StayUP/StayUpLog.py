########################
# SubRoutine Log Write #
########################
from time import strftime, time, localtime

def writeLog(message):
                log_file = "/tmp/StayUpPlugin.log"

                try:
                        f = open(log_file, "r")
                        log = f.read()
                        f.close()
                except:
                        log = ""

                log = log + strftime("%c", localtime(time())) + " - " + message + "\n"

                try:
                        f = open(log_file, "w")
                        f.write(log)
                        f.close()
                except:
                        pass

