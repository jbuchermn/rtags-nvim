from rtags.util import log
from nvimbols.source.base import Base
from nvimbols.graph import SYMBOL, SYMBOL_FILE
from nvimbols.symbol import Symbol, SymbolLocation
from nvimbols.loadable import LOADABLE_FULL, LOADABLE_PREVIEW
from nvimbols.reference import TargetRef, ParentRef, InheritanceRef
from rtags.rc import rc_get_referenced_symbol_location, rc_get_symbol_info, rc_get_referenced_by_symbol_locations, rc_get_class_hierarchy, rc_get_symbol_locations_in_file


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
        name = symbol['symbolName']
        kind = symbol['kind']

        super().__init__(name, kind)
        self.data['Type'] = symbol['type'] if 'type' in symbol else None


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = "RTags"
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']

        self._cache = {}

    def reset(self):
        self._cache = {}

    def _find_references(self, location, preview=False):

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

        return refs, True

    def _find_referenced_by(self, location, preview=False):
        referenced_by_locations, full = rc_get_referenced_by_symbol_locations(location, preview)
        if(referenced_by_locations is None):
            return [], True

        res = []
        for loc in referenced_by_locations:
            ref = SymbolLocation(*loc)

            if(ref == location or location.contains(ref) or ref.contains(location)):
                continue

            res += [ref]

        return res, full

    def load_symbol(self, params):
        wrapper = params['wrapper']

        symbol = rc_get_symbol_info(wrapper.location)

        if(symbol is None):
            wrapper.symbol.set(None)
        else:
            filename, start_line, start_col, end_line, end_col = get_location(symbol)

            wrapper.location.filename = filename
            wrapper.location.start_line = start_line
            wrapper.location.start_col = start_col
            wrapper.location.end_line = end_line
            wrapper.location.end_col = end_col

            wrapper.symbol.set(RTagsSymbol(symbol))
            if 'parent' in symbol:
                parent_location = SymbolLocation(*get_location(symbol['parent']))
                wrapper.source_of[ParentRef.name].set([self._graph.create_wrapper(parent_location)])

    def load_source_of(self, params):
        wrapper = params['wrapper']
        reference = params['reference']

        if wrapper.type == SYMBOL:
            if(reference == TargetRef):
                res, full = self._find_references(wrapper.location, params['requested_level'] == LOADABLE_PREVIEW)
                res = [self._graph.create_wrapper(loc) for loc in res]

                wrapper.source_of[reference.name].set(res, LOADABLE_FULL if full else LOADABLE_PREVIEW)

            elif(reference == InheritanceRef):
                supers, subs = rc_get_class_hierarchy(wrapper.location)
                res = [self._graph.create_wrapper(SymbolLocation(*s)) for s in supers]

                wrapper.source_of[reference.name].set(res)

            elif(reference == ParentRef):
                """
                TODO: A bit hacky
                """
                wrapper.source_of[ParentRef.name].set([])
                self.load_symbol(params)

            else:
                wrapper.source_of[reference.name].set([])

    def load_target_of(self, params):
        wrapper = params['wrapper']
        reference = params['reference']

        def set_all_in_file(target, filename):
            if filename not in self._cache:
                self._cache[filename] = rc_get_symbol_locations_in_file(filename)
            target.set([self._graph.create_wrapper(SymbolLocation(*loc)) for loc in self._cache[filename]])

        if wrapper.type == SYMBOL:
            if(reference == TargetRef):
                res, full = self._find_referenced_by(wrapper.location, params['requested_level'] == LOADABLE_PREVIEW)
                res = [self._graph.create_wrapper(loc) for loc in res]

                wrapper.target_of[reference.name].set(res, LOADABLE_FULL if full else LOADABLE_PREVIEW)

            elif(reference == InheritanceRef):
                supers, subs = rc_get_class_hierarchy(wrapper.location)
                res = [self._graph.create_wrapper(SymbolLocation(*s)) for s in subs]

                wrapper.target_of[reference.name].set(res)

            elif(reference == ParentRef):
                set_all_in_file(wrapper.target_of[ParentRef.name], wrapper.location.filename)

            else:
                wrapper.target_of[reference.name].set([])

        elif wrapper.type == SYMBOL_FILE and reference == ParentRef:
            set_all_in_file(wrapper.target_of[ParentRef.name], wrapper.location.filename)
        










