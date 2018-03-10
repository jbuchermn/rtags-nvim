import neovim
import os
from rtags.util import log, on_error
from rtags.neomake.neomake_rtags import NeomakeRTags
from rtags.rc import rc_reindex
from rtags.rc_j import RcJ
from rtags.rc_status import RcStatus
from rtags.rdm import Rdm


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self._vim = vim
        self._rdm = Rdm(vim)
        self._neomake_rtags = NeomakeRTags(vim)
        self._rcstatus = RcStatus(lambda in_index, indexing: self._status(in_index, indexing))
        self._enabled = False
        self._filename = ""

    def _status(self, in_index, indexing):
        if not self._enabled:
            return

        try:
            self._vim.session.threadsafe_call(lambda: self._vim.call("rtags#on_status_change", in_index, indexing))

            if in_index and not indexing:
                list_entries = self._neomake_rtags.get_list_entries(self._filename)
            else:
                list_entries = []

            self._vim.session.threadsafe_call(lambda: self._vim.call("rtags#on_list_entries_change", list_entries))
        except Exception as err:
            on_error(self._vim, err)

    """
    Asynchronous API
    """
    @neovim.function('_rtags_enable')
    def enable(self, args):
        try:
            self._enabled = (args[0] != 0)

            if self._enabled:
                self._filename = self._vim.current.buffer.name
                self._rcstatus.set_filename(self._filename)
                self._rdm.ensure_running()

            self._rcstatus.enable(self._enabled)

        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_reindex')
    def reindex(self, args):
        try:
            buf = self._vim.current.buffer
            filename = buf.name
            text = "\n".join(buf)

            rc_reindex(filename, text)
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_vimleave')
    def vimleave(self, args):
        try:
            self._rcstatus.enable(False)
            self._rdm.finish()
        except Exception as err:
            on_error(self._vim, err)

    """
    Synchronous API
    """
    @neovim.function('_rtags_J', sync=True)
    def rtags_J(self, args):
        try:
            RcJ(self._vim).start()
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_logfile', sync=True)
    def rtags_logfile(self, args):
        try:
            self._rdm.show_log()
        except Exception as err:
            on_error(self._vim, err)









