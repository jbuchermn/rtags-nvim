import neovim
import os
from rtags.util import log, on_error
from rtags.neomake.neomake_rtags import NeomakeRTags
from rtags.rc import rc_reindex
from rtags.rc_j import RcJ
from rtags.rc_status import RcStatus
from rtags.rdm_log import RdmLog


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self._vim = vim
        self._neomake_rtags = NeomakeRTags(vim)

        def callback(*args):
            self._status(*args)

        self._rcstatus = RcStatus(callback)

    @neovim.function('_rtags_reindex_unsaved')
    def reindex_unsaved(self, args):
        try:
            buf = self._vim.current.buffer
            filename = buf.name
            text = "\n".join(buf)

            rc_reindex(filename, text)
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_filename_update')
    def filename_update(self, args):
        try:
            buf = self._vim.current.buffer
            filename = buf.name
            self._rcstatus.set_filename(filename)
        except Exception as err:
            on_error(self._vim, err)

    def _status(self, in_index, indexing):
        try:
            if indexing:
                status = "..."
            elif in_index:
                status = "INDEXED"
            else:
                status = "NOT IN INDEX"


            self._vim.session.threadsafe_call(lambda: self._vim.call("airline#extensions#rtags#set_status", status))
            if(not indexing):
                self._vim.session.threadsafe_call(lambda: self._vim.call("rtags#indexing_finished"))
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_J', sync=True)
    def rtags_J(self, args):
        try:
            rcj = RcJ(self._vim)
            rcj.start()
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_logfile', sync=True)
    def rtags_logfile(self, args):
        try:
            rdmlog = RdmLog(self._vim)
            rdmlog.show()
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_rtags_neomake_get_list_entries', sync=True)
    def neomake_get_list_entries(self, args):
        log("[GET_LIST_ENTRIES]")

        try:
            if(len(args) < 1):
                return []

            jobinfo = args[0]
            filename = self._vim.current.buffer.name

            list_entries = self._neomake_rtags.get_list_entries(filename)

            log("[GET_LIST_ENTRIES FINISHED]")
            return list_entries

        except Exception as err:
            on_error(self._vim, err)








