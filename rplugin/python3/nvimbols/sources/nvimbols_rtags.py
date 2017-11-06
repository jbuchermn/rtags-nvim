import json
from subprocess import Popen, PIPE

from rtags.util import log
from nvimbols.source.base import Base
from nvimbols.symbol import Symbol, SymbolLocation
from rtags.nvimbols.rtags_symbol import RTagsSymbol


def rc_get_symbol_info(location):
    command = "rc --absolute-path --json --symbol-info %s:%i:%i" % (location._filename, location._start_line, location._start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None

    try:
        return json.loads(stdout_data)
    except Exception:
        return None


def rc_get_referenced_symbol_location(location):
    command = "rc --absolute-path --follow-location %s:%i:%i" % (location._filename, location._start_line, location._start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None

    location = stdout_data.split(' ')[0]
    tmp = location.split(':')
    filename = tmp[0]
    line = int(tmp[1])
    col = int(tmp[2])

    return SymbolLocation(filename, line, col)


def rc_get_referenced_by_symbol_locations(location):
    command = "rc --absolute-path --max 100 --references %s:%i:%i" % (location._filename, location._start_line, location._start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None

    result = []
    for line in stdout_data.splitlines():
        if line.strip() == "":
                continue

        location = line.split(' ')[0]
        tmp = location.split(':')
        filename = tmp[0]
        line = int(tmp[1])
        col = int(tmp[2])

        result += [SymbolLocation(filename, line, col)]

    if(len(result) == 100):
        del result[99]
        # TODO: Add some ... in output

    return result


class Source(Base):

    def supported_filetypes(self):
        return ['c', 'cpp']

    def _find_references(self, symbol):

        def try_find_ref(symbol):
            referenced_location = rc_get_referenced_symbol_location(symbol._location)
            if(referenced_location is not None):
                return RTagsSymbol(rc_get_symbol_info(referenced_location))
            else:
                return None

        refs = []
        cur = symbol
        for i in range(10):
            ref = try_find_ref(cur)
            if ref is None:
                break

            cur = ref

            loop = False
            for r in [symbol] + refs:
                if(r._location == ref._location):
                    loop = True
                    break
            if loop:
                break
            else:
                refs += [ref]

        return refs

    def _find_referenced_by(self, symbol):
        referenced_by_locations = rc_get_referenced_by_symbol_locations(symbol._location)
        if(referenced_by_locations is None):
            return []

        result = []
        for location in referenced_by_locations:
            referenced_by_symbol = RTagsSymbol(rc_get_symbol_info(location))
            if referenced_by_symbol._location == symbol._location:
                continue

            result += [referenced_by_symbol]

        return result

    def symbol_at_location(self, location):
        symbol = rc_get_symbol_info(location)

        if(symbol is None):
            return None

        symbol = RTagsSymbol(symbol)

        symbol._references = self._find_references(symbol)
        symbol._referenced_by = self._find_referenced_by(symbol)

        return symbol















