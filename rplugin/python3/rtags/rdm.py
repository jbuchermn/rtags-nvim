import os
import pty
from threading import Thread
from subprocess import Popen
from rtags.util import vim_log
from rtags.rc import rc_check_rdm


class Daemon(Thread):
    def __init__(self, cmd, output_lines=10):
        super().__init__()
        self._cmd = cmd
        self._process = None
        self.output = ["" for i in range(output_lines)]

    def run(self):
        master, slave = pty.openpty()
        self._process = Popen(self._cmd.split(" "), stderr=slave, stdout=slave, close_fds=True)
        for line in os.fdopen(master):
            self.output += [line]

    def terminate(self):
        self._process.terminate()


class Rdm:
    def __init__(self, vim):
        self._vim = vim
        self._daemon = None

    def ensure_running(self):
        if not rc_check_rdm():
            self.start()

    def start(self):
        if self._daemon is not None and self._daemon.isAlive():
            return

        vim_log(self._vim, "Starting rdm...")
        self._daemon = Daemon("rdm")
        self._daemon.start()

    def finish(self):
        if self._daemon is None:
            return

        vim_log(self._vim, "Stopping rdm...")
        self._daemon.terminate()

    def show_log(self):
        if self._daemon is None:
            vim_log(self._vim, "Can't read log from unmanaged rdm")
        else:
            for line in self._daemon.output:
                vim_log(self._vim, line)

