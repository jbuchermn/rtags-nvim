from rtags.util import log
from nvimbols.source.base import Base
from nvimbols.symbol import Symbol, SymbolLocation
from nvimbols.reference import TargetRef, ParentRef, InheritanceRef
from rtags.rc import rc_get_referenced_symbol_location, rc_get_symbol_info, rc_get_referenced_by_symbol_locations, rc_get_class_hierarchy


def get_location(data):
    location = data['location']
    length = data['symbolLength']

    tmp = location.split(':')
    filename = tmp[0]
    start_line = int(tmp[1])
    start_col = int(tmp[2])

    return filename, start_line, start_col, start_line, start_col + length


class RTagsSymbol(Symbol):
    def __init__(self, symbol):
        Symbol.__init__(self)

        self.name = symbol['symbolName']
        self.data['Kind'] = symbol['kind']
        self.data['Type'] = symbol['type'] if 'type' in symbol else None

        if 'parent' in symbol:
            parents = self.get_source_of(ParentRef)
            parent_location = SymbolLocation(*get_location(symbol['parent']))
            parents.reset()
            parents += [parent_location]
            parents.loaded()


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "RTags"
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']

    def _find_references(self, location):

        def try_find_ref(location):
            referenced_location = rc_get_referenced_symbol_location(location)
            if(referenced_location is not None):
                return SymbolLocation(*referenced_location)

        cur = location
        refs = []
        for i in range(10):
            ref = try_find_ref(cur)
            if ref is None:
                break

            cur = ref

            loop = False
            for r in [location] + refs:
                if(r == ref or ref.contains(r) or r.contains(ref)):
                    loop = True
                    break
            if loop:
                break
            else:
                refs += [ref]

        return refs, False

    def _find_referenced_by(self, location):
        referenced_by_locations, incomplete = rc_get_referenced_by_symbol_locations(location)
        if(referenced_by_locations is None):
            return [], False

        res = []
        for loc in referenced_by_locations:
            ref = SymbolLocation(*loc)

            if(ref == location or location.contains(ref) or ref.contains(location)):
                continue

            res += [ref]

        return res, incomplete

    def load_symbol(self, location):
        symbol = rc_get_symbol_info(location)

        if(symbol is None):
            location.symbol.set(None)
        else:
            filename, start_line, start_col, end_line, end_col = get_location(symbol)

            location.filename = filename
            location.start_line = start_line
            location.start_col = start_col
            location.end_line = end_line
            location.end_col = end_col

            location.symbol.set(RTagsSymbol(symbol))

    def load_source_of(self, symbol, reference):
        res = symbol.get_source_of(reference)

        if(reference == TargetRef):
            refs, incomplete = self._find_references(symbol.location)

            res.reset()
            for location in refs:
                res += [location]
            res.loaded(incomplete)
        
        elif(reference == InheritanceRef):
            supers, subs = rc_get_class_hierarchy(symbol.location)
            for s in supers:
                res += [SymbolLocation(*s)]

            res.loaded()
        else:
            res.loaded(True)

    def load_target_of(self, symbol, reference):
        res = symbol.get_target_of(reference)

        if(reference == TargetRef):
            refs, incomplete = self._find_referenced_by(symbol.location)

            res.reset()
            for location in refs:
                res += [location]
            res.loaded(incomplete)
        
        elif(reference == InheritanceRef):
            supers, subs = rc_get_class_hierarchy(symbol.location)
            for s in subs:
                res += [SymbolLocation(*s)]

            res.loaded()

        else:
            res.loaded(True)












