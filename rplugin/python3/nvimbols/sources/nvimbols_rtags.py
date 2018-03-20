from rtags.util import log
from nvimbols.source.base import Base
from nvimbols.location import Location
from nvimbols.loadable_state import LoadableState
from nvimbols.symbol import Symbol
from nvimbols.reference import (ParentReference,
                                TargetReference,
                                InheritanceReference)
from nvimbols.request import (LoadSymbolRequest,
                              LoadReferencesRequest,
                              LoadSubGraphFileRequest)
from rtags.rc import (rc_reindex,
                      rc_is_indexing,
                      rc_get_referenced_symbol_location,
                      rc_get_symbol_info,
                      rc_get_referenced_by_symbol_locations,
                      rc_get_class_hierarchy,
                      rc_symbol_locations_in_file)


def get_location(data):
    location = data['location']
    length = data['symbolLength']

    tmp = location.split(':')
    filename = tmp[0]
    start_line = int(tmp[1])
    start_col = int(tmp[2])

    return Location(filename, start_line, start_col, start_line, start_col + length)


class RTagsSymbol(Symbol):
    def set(self, data):
        self.name = data['symbolName']
        self.kind = data['kind']
        self.type = data['type'] if 'type' in data else None
        self.fulfill()


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = "RTags"
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']

    def _find_references(self, location, preview=False):
        def try_find_ref(location):
            referenced_location = rc_get_referenced_symbol_location(location)
            if referenced_location is not None:
                return Location(*referenced_location)

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
            ref = Location(*loc)

            if(ref == location or location.contains(ref) or ref.contains(location)):
                continue

            res += [ref]

        return res, full

    def request(self, req):
        if rc_is_indexing():
            return

        if isinstance(req, LoadSymbolRequest):
            data = rc_get_symbol_info(req.location)

            if data is None:
                req.graph.empty(req.location)
                return False
            else:
                location = get_location(data)
                symbol = req.graph.symbol(location, RTagsSymbol)
                symbol.set(data)

                if 'parent' in data:
                    location = get_location(data['parent'])
                    parent = req.graph.symbol(location, RTagsSymbol)
                    parent.set(data['parent'])
                    symbol.reference_to(ParentReference(), parent)
                    symbol.fulfill_source_of(ParentReference, LoadableState.FULL)

                return True

        elif isinstance(req, LoadReferencesRequest):
            if req.source_of:
                if req.reference_class == TargetReference:
                    res, full = self._find_references(req.symbol.location, req.requested_state < LoadableState.FULL)
                    for loc in res:
                        symbol = req.graph.symbol(loc, RTagsSymbol)
                        req.symbol.reference_to(TargetReference(), symbol)
                    req.symbol.fulfill_source_of(TargetReference,
                                                 LoadableState.FULL if full else LoadableState.PREVIEW)
                    return False

                elif req.reference_class == InheritanceReference:
                    supers, subs = rc_get_class_hierarchy(req.symbol.location)
                    for loc in supers:
                        location = Location(*loc)
                        symbol = req.graph.symbol(location, RTagsSymbol)
                        req.symbol.reference_to(InheritanceReference(), symbol)
                    req.symbol.fulfill_source_of(InheritanceReference,
                                                 LoadableState.FULL)
                    return False

                elif req.reference_class == ParentReference:
                    data = rc_get_symbol_info(req.symbol.location)

                    if 'parent' in data:
                        location = get_location(data['parent'])
                        parent = req.graph.symbol(location, RTagsSymbol)
                        parent.set(data['parent'])
                        req.symbol.reference_to(ParentReference(), parent)
                    req.symbol.fulfill_source_of(ParentReference,
                                                 LoadableState.FULL)
                    return False

            else:
                if req.reference_class == TargetReference:
                    res, full = self._find_referenced_by(req.symbol.location, req.requested_state < LoadableState.FULL)
                    for loc in res:
                        symbol = req.graph.symbol(loc, RTagsSymbol)
                        req.symbol.reference_from(TargetReference(), symbol)
                    req.symbol.fulfill_target_of(TargetReference,
                                                 LoadableState.FULL if full else LoadableState.PREVIEW)
                    return False

                elif req.reference_class == InheritanceReference:
                    supers, subs = rc_get_class_hierarchy(req.symbol.location)
                    for loc in subs:
                        location = Location(*loc)
                        symbol = req.graph.symbol(location, RTagsSymbol)
                        req.symbol.reference_from(InheritanceReference(), symbol)
                    req.symbol.fulfill_target_of(InheritanceReference,
                                                 LoadableState.FULL)
                    return False

                elif req.reference_class == ParentReference:
                    """
                    TODO!
                    """
                    return True

        elif isinstance(req, LoadSubGraphFileRequest):
            locations = rc_symbol_locations_in_file(req.sub_graph.filename)
            for l in locations:
                loc = Location(*l)
                """
                TODO! Some symbols don't have symbol_information, like 1:1:1:2
                """
                if loc.start_line == loc.start_col == loc.end_line == loc.end_col - 1 == 1:
                    continue

                req.graph.symbol(loc, RTagsSymbol)

            return True

    def on_file_invalidate(self, filename, text):
        rc_reindex(filename, text)
