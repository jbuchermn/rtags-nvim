from threading import Timer
from rtags.rc import rc_is_indexing, rc_in_index
from rtags.util import log


class RcStatus:
    def __init__(self, callback):
        self._filename = None
        self._callback = callback
        self._in_index = False
        self._indexing = True

        self._enabled = False

    def enable(self, enabled):
        if(not self._enabled and enabled):
            self._enabled = enabled
            self._get()

        self._enabled = enabled

    def _get(self):
        try:
            if(self._filename is not None):
                in_index = rc_in_index(self._filename)
                indexing = rc_is_indexing()

                if(indexing != self._indexing or in_index != self._in_index):
                    self._callback(in_index, indexing)

                self._in_index = in_index
                self._indexing = indexing

        finally:
            if self._enabled:
                Timer(.5, RcStatus._get, args=[self, True]).start()

    def set_filename(self, filename):
        self._filename = filename

