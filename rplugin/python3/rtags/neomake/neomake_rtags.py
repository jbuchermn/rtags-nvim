from rtags.util import log
from rtags.rc import rc_get_diagnostics


class NeomakeRTags:
    def __init__(self, vim):
        self._vim = vim

    def get_list_entries(self, filename):
        try:
            errors_json = rc_get_diagnostics(filename)['checkStyle'][filename]
        except Exception:
            return []

        errors = []
        for e in errors_json:
            errors.append({
                'filename': filename,
                'lnum': e['line'],
                'col': e['column'],
                'length': e['length'] if 'length' in e else None,
                'type': 'E' if e['type'] == 'error' else 'W',
                'text': e['message'] if 'message' in e else ''
            })

        return errors
