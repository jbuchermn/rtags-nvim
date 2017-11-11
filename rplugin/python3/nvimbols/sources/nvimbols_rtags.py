from rtags.util import log
from nvimbols.source.base import Base
from nvimbols.symbol import Symbol, SymbolLocation
from nvimbols.reference import TargetRef
from rtags.nvimbols.rtags_symbol import RTagsSymbol
from rtags.rc import rc_get_referenced_symbol_location, rc_get_symbol_info, rc_get_referenced_by_symbol_locations



class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "RTags"
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']

    def _find_references(self, symbol):

        def try_find_ref(symbol):
            referenced_location = rc_get_referenced_symbol_location(symbol.location)
            if(referenced_location is not None):
                symbol = rc_get_symbol_info(SymbolLocation(*referenced_location))
                return RTagsSymbol(symbol) if symbol is not None else None
            else:
                return None

        cur = symbol
        refs = []
        for i in range(10):
            ref = try_find_ref(cur)
            if ref is None:
                break

            cur = ref

            loop = False
            for r in [symbol] + refs:
                if(r.location == ref.location):
                    loop = True
                    break
            if loop:
                break
            else:
                refs += [ref]
                yield ref


    def _find_referenced_by(self, symbol):
        # TODO! Do sth useful with incomplete
        referenced_by_locations, incomplete = rc_get_referenced_by_symbol_locations(symbol.location)
        if(referenced_by_locations is None):
            return []

        for location in referenced_by_locations:
            referenced_by_symbol = rc_get_symbol_info(SymbolLocation(*location))
            if referenced_by_symbol is None:
                continue
            referenced_by_symbol = RTagsSymbol(referenced_by_symbol)

            if referenced_by_symbol.location == symbol.location:
                continue

            yield referenced_by_symbol

    def symbol_at_location(self, location):
        symbol = rc_get_symbol_info(location)

        if(symbol is None):
            return None

        symbol = RTagsSymbol(symbol)

        return symbol

    def load_source_of(self, symbol, reference):
        if(reference == TargetRef):
            return self._find_references(symbol)
        else:
            return []

    def load_target_of(self, symbol, reference):
        if(reference == TargetRef):
            return self._find_referenced_by(symbol)
        else:
            return []













