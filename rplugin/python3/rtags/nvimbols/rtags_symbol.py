from nvimbols.symbol import Symbol, SymbolLocation
from nvimbols.util import log


class RTagsSymbol(Symbol):
    def __init__(self, symbol):

        location = symbol['location']
        length = symbol['symbolLength']

        tmp = location.split(':')
        filename = tmp[0]
        start_line = int(tmp[1])
        start_col = int(tmp[2])

        location = SymbolLocation(filename, start_line, start_col, start_line, start_col + length)

        Symbol.__init__(self, symbol['symbolName'], symbol['kind'], symbol['type'], location)
