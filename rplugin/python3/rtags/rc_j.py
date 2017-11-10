import os
import tempfile
import shutil
from subprocess import Popen, PIPE
from abc import abstractmethod
from rtags.rc import rc_current_project, rc_j
from rtags.util import vim_log


def find_file(directory, filename):
    """
    Utility: Find files traversing the filesystem upwards
    """
    tmp = directory
    while not os.path.samefile(tmp, os.path.dirname(tmp)):
        if(os.path.isfile(os.path.join(tmp, filename))):
            yield os.path.join(tmp, filename)

        tmp = os.path.dirname(tmp)


class RcJTask:
    def __init__(self, rtags_project, filename, vim_directory):
        self._rtags_project = rtags_project
        self._filename = filename
        self._vim_directory = vim_directory

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def string(self):
        pass

    @abstractmethod
    def action(self, vim):
        pass


class ExistingCompileCommands(RcJTask):
    def validate(self):
        compile_commands = None
        if self._rtags_project is not None:
            if os.path.isfile(os.path.join(self._rtags_project, "compile_commands.json")):
                compile_commands = os.path.join(self._rtags_project, "compile_commands")

        if compile_commands is None and self._filename is not None:
            for f in find_file(os.path.dirname(self._filename), "compile_commands.json"):
                compile_commands = f
                break

        if compile_commands is None and self._vim_directory is not None:
            if os.path.isfile(os.path.join(self._vim_directory, "compile_commands.json")):
                compile_commands = os.path.join(self._vim_directory, "compile_commands")

        if compile_commands is None:
            return False
        else:
            self._compile_commands = compile_commands
            return True

    def string(self):
        return "Use existing %s" % self._compile_commands

    def action(self, vim):
        vim_log(vim, "Executing rc -J in %s.." % os.path.dirname(self._compile_commands))
        vim_log(vim, rc_j(os.path.dirname(self._compile_commands)))


class CMakeProject(RcJTask):
    def is_toplevel_cmakelists(self, filename):
        """
        Recognises a CMakeLists.txt as root if it contains a "project(...)" line
        (I don't know if this is the correct way to do this...)
        """
        with open(filename, 'r') as f:
            for line in f:
                if(line.strip().lower().startswith("project")):
                    return True
        return False

    def validate(self):
        cmakelists = None

        if(self._rtags_project and os.path.isfile(os.path.join(self._rtags_project, "CMakeLists.txt"))):
            if(self.is_toplevel_cmakelists(os.path.join(self._rtags_project, "CMakeLists.txt"))):
                cmakelists = os.path.join(self._rtags_project, "CMakeLists.txt")

        if(cmakelists is None and self._filename is not None):
            for f in find_file(os.path.dirname(self._filename), "CMakeLists.txt"):
                if(self.is_toplevel_cmakelists(f)):
                    cmakelists = f
                    break

        if(cmakelists is None and os.path.isfile(os.path.join(self._vim_directory, "CMakeLists.txt"))):
            if(self.is_toplevel_cmakelists(os.path.join(self._vim_directory, "CMakeLists.txt"))):
                cmakelists = os.path.join(self._vim_directory, "CMakeLists.txt")

        if(cmakelists is None):
            return False
        else:
            self._cmakelists = cmakelists
            return True

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

            keep = vim.call("input", "Keep compile_commands.json (y/N)? ")
            vim.command("echo(\"...\")")
            if keep.strip() == "" or keep.strip() == "n" or keep.strip() == "N":
                os.remove(os.path.join(os.path.dirname(self._cmakelists), "compile_commands.json"))
        elif os.path.isfile(os.path.join(os.path.dirname(self._cmakelists), "compile_commands.json")):
            vim_log(vim, "No compile_commands.json in temporary directory... Assuming in-tree build")

            vim_log(vim, "Executing rc -J in %s..." % os.path.dirname(self._cmakelists))
            vim_log(vim, rc_j(os.path.dirname(self._cmakelists)))

        else:
            vim_log(vim, "CMake failed to create compile_commands.json")

        shutil.rmtree(tempdir)


class BearMakeProject(RcJTask):
    def validate(self):
        """
        Check if bear is in the $PATH
        """
        p = Popen("which bear".split(" "), stdout=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate()
        if(stdout_data.decode("utf-8").strip() == ""):
            return False

        makefile = None

        if(self._rtags_project and os.path.isfile(os.path.join(self._rtags_project, "Makefile"))):
            makefile = os.path.join(self._rtags_project, "Makefile")

        if(makefile is None and self._filename is not None):
            for f in find_file(os.path.dirname(self._filename), "Makefile"):
                makefile = f
                break

        if(makefile is None and os.path.isfile(os.path.join(self._vim_directory, "Makefile"))):
            makefile = os.path.join(self._vim_directory, "Makefile")

        if(makefile is None):
            return False
        else:
            self._makefile = makefile
            return True

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
            
            keep = vim.call("input", "Keep compile_commands.json (y/N)? ")
            vim.command("echo(\"...\")")
            if keep.strip() == "" or keep.strip() == "n" or keep.strip() == "N":
                os.remove(os.path.join(os.path.dirname(self._makefile), "compile_commands.json"))

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
        tasks = [
            ExistingCompileCommands(self._rtags_project, self._filename, self._vim_directory),
            CMakeProject(self._rtags_project, self._filename, self._vim_directory),
            BearMakeProject(self._rtags_project, self._filename, self._vim_directory),
        ]

        tasks = [task for task in tasks if task.validate()]
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
















