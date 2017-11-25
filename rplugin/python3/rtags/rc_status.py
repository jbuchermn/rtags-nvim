from threading import Timer
from rtags.rc import rc_is_indexing, rc_in_index
from rtags.util import log


class RcStatus:
    def __init__(self, callback):
        self._filename = None
        self._callback = callback
        self._in_index = False
        self._indexing = True

        self._get(True)

    def _get(self, auto=False):
        try:
            if(self._filename is not None):
                in_index = rc_in_index(self._filename)
                indexing = rc_is_indexing()

                if(indexing != self._indexing or in_index != self._in_index):
                    self._callback(in_index, indexing)

                self._in_index = in_index
                self._indexing = indexing

        finally:
            if auto:
                Timer(.5, RcStatus._get, args=[self, True]).start()

    def set_filename(self, filename):
        self._filename = filename

