import json
from subprocess import Popen, PIPE
from rtags.util import log


def rc_get_diagnostics(filename):
    command = "rc --json --absolute-path --synchronous-diagnostics --diagnose %s" % filename

    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()

    stdout_data = stdout_data.decode("utf-8")
    try:
        return json.loads(stdout_data)
    except Exception:
        return None


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
                'text': e['message']
            })

        return errors
