import json
from subprocess import Popen, PIPE


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
    
    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE, cwd=directory)
    stdout_data, stderr_data = p.communicate()
    stdout_data.decode("utf-8").strip() != "0"

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


def rc_get_referenced_symbol_location(location):
    command = "rc --absolute-path --follow-location %s:%i:%i" % (location.filename, location.start_line, location.start_col)

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

    return (filename, line, col)


def rc_get_referenced_by_symbol_locations(location):
    command = "rc --absolute-path --max 100 --references %s:%i:%i" % (location.filename, location.start_line, location.start_col)

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

    incomplete = False
    if(len(result) == 100):
        del result[99]
        incomplete = True

    return result, incomplete


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










