import os
from rtags.util import vim_log

POSSIBLE_LOGFILE_LOCATIONS = [
    "/var/log/rtags",
    "/usr/local/var/log"
]

POSSIBLE_LOGFILE_NAMES = [
    "rtags.log"
]


class RdmLog:
    def __init__(self, vim):
        self._vim = vim

    def show(self):
        log = None
        for loc in POSSIBLE_LOGFILE_LOCATIONS:
            for name in POSSIBLE_LOGFILE_NAMES:
                if(os.path.isfile(os.path.join(loc, name))):
                    log = os.path.join(loc, name)

        if log is None:
            vim_log(self._vim, "Couldn't find log file")
        else:
            content = []
            with open(log, 'r') as logfile:
                for line in logfile:
                    content += [line]

            if len(content) > 10:
                content = content[-10:]

            for line in content:
                vim_log(self._vim, line)

