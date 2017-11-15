import os
import tempfile
import shutil
from subprocess import Popen, PIPE
from abc import abstractmethod
from rtags.rc import rc_current_project, rc_j
from rtags.util import vim_log
from itertools import filterfalse

def unique(iterable):
    seen = set()
    seen_add = seen.add
    for element in filterfalse(seen.__contains__, iterable):
        seen_add(element)
        yield element

def find_file(directory, filename):
    """
    Utility: Find files traversing the filesystem upwards
    """
    tmp = directory
    while not os.path.samefile(tmp, os.path.dirname(tmp)):
        if(os.path.isfile(os.path.join(tmp, filename))):
            yield os.path.join(tmp, filename)

        tmp = os.path.dirname(tmp)


def find_compile_commands(filename, rtags_project, vim_directory):
    if filename is not None:
        yield from find_file(os.path.dirname(filename), "compile_commands.json")

    if vim_directory is not None:
        if os.path.isfile(os.path.join(vim_directory, "compile_commands.json")):
            yield os.path.join(vim_directory, "compile_commands.json")

    if rtags_project is not None:
        if os.path.isfile(os.path.join(rtags_project, "compile_commands.json")):
            yield os.path.join(rtags_project, "compile_commands.json")


def find_makefiles(filename, rtags_project, vim_directory):
    if filename is not None:
        yield from find_file(os.path.dirname(filename), "Makefile")

    if vim_directory is not None:
        if(os.path.isfile(os.path.join(vim_directory, "Makefile"))):
            yield os.path.join(vim_directory, "Makefile")

    if rtags_project is not None:
        if(os.path.isfile(os.path.join(rtags_project, "Makefile"))):
            yield os.path.join(rtags_project, "Makefile")


def is_toplevel_cmakelists(filename):
    """
    Recognises a CMakeLists.txt as root if it contains a "project(...)" line
    (I don't know if this is the correct way to do this...)
    """
    with open(filename, 'r') as f:
        for line in f:
            if(line.strip().lower().startswith("project")):
                return True
    return False


def find_cmakelists(filename, rtags_project, vim_directory):
        if filename is not None:
            for f in find_file(os.path.dirname(filename), "CMakeLists.txt"):
                if(is_toplevel_cmakelists(f)):
                    yield f

        if vim_directory is not None:
            if(os.path.isfile(os.path.join(vim_directory, "CMakeLists.txt")) and is_toplevel_cmakelists(os.path.join(vim_directory, "CMakeLists.txt"))):
                yield os.path.join(vim_directory, "CMakeLists.txt")

        if rtags_project is not None:
            if(os.path.isfile(os.path.join(rtags_project, "CMakeLists.txt")) and is_toplevel_cmakelists(os.path.join(rtags_project, "CMakeLists.txt"))):
                yield os.path.join(rtags_project, "CMakeLists.txt")


class RcJTask:
    @abstractmethod
    def string(self):
        pass

    @abstractmethod
    def action(self, vim):
        pass


class ExistingCompileCommands(RcJTask):
    def __init__(self, compile_commands):
        self._compile_commands = compile_commands

    def string(self):
        return "Use existing %s" % self._compile_commands

    def action(self, vim):
        vim_log(vim, "Executing rc -J in %s.." % os.path.dirname(self._compile_commands))
        vim_log(vim, rc_j(os.path.dirname(self._compile_commands)))


class CMakeProject(RcJTask):
    def __init__(self, cmakelists):
        self._cmakelists = cmakelists

    def string(self):
        return "CMake: Generate compile_commands.json from %s" % self._cmakelists

    def action(self, vim):
        tempdir = tempfile.mkdtemp()
        args = vim.call("input", "CMake command line arguments? ")
        vim.command("echo(\"...\")")

        vim_log(vim, "Calling CMake in %s..." % tempdir)
        p = Popen(("cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 %s %s" % (args, os.path.dirname(self._cmakelists))).split(" "), stdout=PIPE, stderr=PIPE, cwd=tempdir)
        stdout_data, stderr_data = p.communicate()
        vim_log(vim, "%s\n%s" % (stdout_data.decode("utf-8").replace("\"", "\\\""), stderr_data.decode("utf-8").replace("\"", "\\\"")))

        if os.path.isfile(os.path.join(tempdir, "compile_commands.json")):
            # copy overwrites file
            shutil.copy(os.path.join(tempdir, "compile_commands.json"), os.path.join(os.path.dirname(self._cmakelists), "compile_commands.json"))

            vim_log(vim, "Executing rc -J in %s..." % os.path.dirname(self._cmakelists))
            vim_log(vim, rc_j(os.path.dirname(self._cmakelists)))

        elif os.path.isfile(os.path.join(os.path.dirname(self._cmakelists), "compile_commands.json")):
            vim_log(vim, "No compile_commands.json in temporary directory... Assuming in-tree build")

            vim_log(vim, "Executing rc -J in %s..." % os.path.dirname(self._cmakelists))
            vim_log(vim, rc_j(os.path.dirname(self._cmakelists)))

        else:
            vim_log(vim, "CMake failed to create compile_commands.json")

        shutil.rmtree(tempdir)


class BearMakeProject(RcJTask):
    def __init__(self, makefile):
        self._makefile = makefile

    def string(self):
        return "Bear: Generate compile_commands.json from %s" % self._makefile

    def action(self, vim):
        args = vim.call("input", "make target and command line arguments? (You probably should include \"clean\") ")
        vim.command("echo(\"...\")")

        vim_log(vim, "Calling make in %s..." % os.path.dirname(self._makefile))
        p = Popen(("bear make %s" % args).split(" "), stdout=PIPE, stderr=PIPE, cwd=os.path.dirname(self._makefile))
        stdout_data, stderr_data = p.communicate()
        vim_log(vim, "%s\n%s" % (stdout_data.decode("utf-8").replace("\"", "\\\""), stderr_data.decode("utf-8").replace("\"", "\\\"")))

        if os.path.isfile(os.path.join(os.path.dirname(self._makefile), "compile_commands.json")):
            vim_log(vim, "Executing rc -J in %s..." % os.path.dirname(self._makefile))
            vim_log(vim, rc_j(os.path.dirname(self._makefile)))
        else:
            vim_log(vim, "Bear failed to create compile_commands.json")


class RcJ:
    def __init__(self, vim):
        self._vim = vim
        self._rtags_project = os.path.normpath(rc_current_project())
        if not os.path.isdir(self._rtags_project):
            self._rtags_project = None

        self._filename = os.path.normpath(self._vim.current.buffer.name)
        if not os.path.isfile(self._filename):
            self._filename = None

        self._vim_directory = os.path.normpath(self._vim.eval('getcwd()'))

        """
        Validate rtags_project: This only gets updated, when rc
        is called, so it may be pointing to an old project.

        Specifically, if we want to index a new project, we need to check this.
        """
        if(self._rtags_project is not None and self._filename is not None):
            if(not self._filename.startswith(self._rtags_project)):
                self._rtags_project = None

        elif(self._rtags_project is not None):
            if(not self._vim_directory.startswith(self._rtags_project)):
                self._rtags_project = None

    def start(self):
        p = Popen("which bear".split(" "), stdout=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate()
        bear_installed = stdout_data.decode("utf-8").strip() != ""

        tasks = [ExistingCompileCommands(compile_commands) for compile_commands in unique(find_compile_commands(self._filename, self._rtags_project, self._vim_directory))]
        tasks+= [CMakeProject(cmakelists)                  for cmakelists       in unique(find_cmakelists      (self._filename, self._rtags_project, self._vim_directory))]
        tasks+= [BearMakeProject(makefile)                 for makefile         in unique(find_makefiles       (self._filename, self._rtags_project, self._vim_directory))] if bear_installed else []

        if(len(tasks) == 0):
            self._vim.command("echo(\"Could not find a strategy to call rc -J automatically\")")
            return

        selection = 0
        if(len(tasks) > 1):
            inp_list = ["(%i) %s" % (i + 1, task.string()) for i, task in enumerate(tasks)]
            selection = self._vim.call("inputlist", inp_list) - 1
            self._vim.command("echo(\"...\")")
            if(selection >= len(inp_list) or selection < 0):
                self._vim.command("echo(\"Invalid value\")")
                return
        tasks[selection].action(self._vim)
















