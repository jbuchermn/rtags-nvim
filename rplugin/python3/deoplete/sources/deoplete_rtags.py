import re

from rtags.util import log
from rtags.rc import rc_get_autocompletions
from deoplete.source.base import Base


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'rtags'
        self.mark = '[rtags]'
        self.filetypes = ['c', 'cpp', 'objc', 'objcpp']
        self.rank = 1000
        self.is_bytepos = True
        self.min_pattern_length = 1
        self.input_pattern = (r'[^. \t0-9]\.\w*|'
                              r'[^. \t0-9]->\w*|'
                              r'[a-zA-Z_]\w*::\w*')

    def get_complete_position(self, context):
        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def gather_candidates(self, context):
        line = context['position'][1]
        col = (context['complete_position'] + 1)
        buf = self.vim.current.buffer
        filename = buf.name
        
        log("Getting completions at %s:%i:%i..." % (filename, line, col))

        text = "\n".join(buf)

        completions_json = rc_get_autocompletions(filename, line, col, text)
        if(completions_json is None or 'completions' not in completions_json):
            log("...empty")
            return []

        completions = []
        for raw_completion in completions_json['completions']:
            completion = {'dup': 1}
            completion['word'] = raw_completion['completion']
            completion['menu'] = raw_completion['signature']
            completion['kind'] = raw_completion['kind']
            completions.append(completion)

        log("...done: %i" % len(completions))
        return completions

