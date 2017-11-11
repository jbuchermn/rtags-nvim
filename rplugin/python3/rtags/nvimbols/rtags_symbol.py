from nvimbols.symbol import Symbol, SymbolLocation
from nvimbols.util import log
from nvimbols.reference import ParentRef


class RTagsSymbol(Symbol):
    def __init__(self, symbol):

        location = symbol['location']
        length = symbol['symbolLength']

        tmp = location.split(':')
        filename = tmp[0]
        start_line = int(tmp[1])
        start_col = int(tmp[2])

        location = SymbolLocation(filename, start_line, start_col, start_line, start_col + length)

        Symbol.__init__(self, location)

        self.name = symbol['symbolName']
        self.data['Kind'] = symbol['kind']
        self.data['Type'] = symbol['type'] if 'type' in symbol else None

        if 'parent' in symbol:
            self.source_of[ParentRef.name] = [RTagsSymbol(symbol['parent'])]
