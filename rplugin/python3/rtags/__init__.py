import neovim
import json
from subprocess import Popen, PIPE


def on_error(err):
    with open('/tmp/pylog', 'w') as log:
        log.write(str(err))
    raise err


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim


    @neovim.function('_rtags_reindex_unsaved')
    def reindex_unsaved(self, args):
        buf = self.vim.current.buffer
        filename = buf.name
        text = "\n".join(buf)

        command = "rc --absolute-path --reindex %s --unsaved-file=%s:%i" % (filename, filename, len(text))

        p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout_data, stderr_data = p.communicate(input=text.encode("utf-8"))


    @neovim.function('_rtags_neomake_get_list_entries', sync=True)
    def get_list_entries(self, args):
        try:
            if(len(args) < 1):
                return []
            jobinfo = args[0]

            buf = self.vim.current.buffer
            filename = buf.name

            command = "rc --json --absolute-path --synchronous-diagnostics --diagnose %s" % filename

            p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
            stdout_data, stderr_data = p.communicate()

            stdout_data = stdout_data.decode("utf-8")

            if(stdout_data == ""):
                return []
            errors_json = json.loads(stdout_data)            

            if('checkStyle' not in errors_json):
                return []
            errors_json = errors_json['checkStyle']

            if(filename not in errors_json):
                return []
            errors_json = errors_json[filename]

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

        except Exception as err:
            on_error(err)








