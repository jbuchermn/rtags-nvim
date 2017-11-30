import json
import re
from subprocess import Popen, PIPE
from rtags.util import log

LOCATION_PATTERN = re.compile(r'[^\s]+:[0-9]+:[0-9]+')


def _extract_location(loc):
    tmp = loc.split(':')
    filename = tmp[0]
    line = int(tmp[1])
    col = int(tmp[2])

    return (filename, line, col)


def rc_current_project():
    command = "rc --current-project"

    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    return stdout_data.decode("utf-8").strip()


def rc_j(directory):
    command = "rc -J"

    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE, cwd=directory)
    stdout_data, stderr_data = p.communicate()
    return stdout_data.decode("utf-8").strip()


def rc_reindex(filename, text):
    command = "rc --absolute-path --reindex %s --unsaved-file=%s:%i" % (filename, filename, len(text))

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))


def rc_is_indexing():
    command = "rc --is-indexing"

    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    return stdout_data.decode("utf-8").strip() != "0"


def rc_in_index(filename):
    command = "rc --absolute-path --is-indexed %s" % filename

    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    return stdout_data.decode("utf-8").strip() == "indexed"


def rc_get_diagnostics(filename):
    command = "rc --json --absolute-path --synchronous-diagnostics --diagnose %s" % filename

    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()

    stdout_data = stdout_data.decode("utf-8")
    try:
        return json.loads(stdout_data)
    except Exception:
        return None


def rc_get_symbol_info(location):
    command = "rc --absolute-path --json --symbol-info-include-parents --symbol-info %s:%i:%i" % (location.filename, location.start_line, location.start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None

    try:
        return json.loads(stdout_data)
    except Exception:
        return None


def rc_get_class_hierarchy(location):
    command = "rc --absolute-path --class-hierarchy %s:%i:%i" % (location.filename, location.start_line, location.start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")

    if(stdout_data == ""):
        return [], []

    data = stdout_data.split("\n")
    super_idx = -1
    sub_idx = -1
    for i in range(len(data)):
        if(data[i].strip() == "Superclasses:"):
            super_idx = i
        elif(data[i].strip() == "Subclasses:"):
            sub_idx = i

    super_data = []
    sub_data = []
    if super_idx != -1:
        if sub_idx > super_idx:
            super_data = data[super_idx + 1:sub_idx]
        else:
            super_data = data[super_idx + 1:]
    if sub_idx != -1:
        if super_idx > sub_idx:
            sub_data = data[sub_idx + 1:super_idx]
        else:
            sub_data = data[sub_idx + 1:]

    def parse(d):
        if d.strip() == "":
            return None

        indent = 0
        while(d[indent] == ' '):
            indent += 1

        loc = LOCATION_PATTERN.search(d)
        if loc is None:
            return None
        loc = loc.group()

        return (indent, loc)

    sub_data = [parse(d) for d in sub_data if parse(d) is not None]
    super_data = [parse(d) for d in super_data if parse(d) is not None]

    """
    Only return immediate sub- and superclasses as querying this information is not performance critical
    """
    sub_data = [loc for (i, loc) in sub_data if i == 4]
    super_data = [loc for (i, loc) in super_data if i == 4]

    return [_extract_location(loc) for loc in super_data], [_extract_location(loc) for loc in sub_data]


def rc_get_referenced_symbol_location(location):
    command = "rc --absolute-path --follow-location %s:%i:%i" % (location.filename, location.start_line, location.start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None

    location = stdout_data.split(' ')[0]
    return _extract_location(location)


def rc_get_referenced_by_symbol_locations(location, preview=False):
    if preview:
        command = "rc --absolute-path --max 100 --references %s:%i:%i" % (location.filename, location.start_line, location.start_col)
    else:
        command = "rc --absolute-path --references %s:%i:%i" % (location.filename, location.start_line, location.start_col)

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None, False

    result = []
    for line in stdout_data.splitlines():
        if line.strip() == "":
                continue

        location = line.split(' ')[0]
        tmp = location.split(':')
        filename = tmp[0]
        line = int(tmp[1])
        col = int(tmp[2])

        result += [(filename, line, col)]

    full = True
    if(preview and len(result) == 100):
        del result[99]
        full = False

    return result, full


def rc_get_autocompletions(filename, line, col, text):
    command = "rc --json --absolute-path --synchronous-completions -l %s:%i:%i --unsaved-file=%s:%i" % (filename, line, col, filename, len(text))

    p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))
    stdout_data = stdout_data.decode("utf-8")
    if(stdout_data == ""):
        return None

    try:
        return json.loads(stdout_data)
    except Exception:
        return None










