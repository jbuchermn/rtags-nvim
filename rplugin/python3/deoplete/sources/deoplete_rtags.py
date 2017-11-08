import re

from rtags.rc import rc_get_autocompletions
from deoplete.source.base import Base

current = __file__


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
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
        text = "\n".join(buf)

        completions_json = rc_get_autocompletions(filename, line, col, text)
        if(completions_json is None or 'completions' not in completions_json):
            return []

        completions = []
        for raw_completion in completions_json['completions']:
            completion = {'dup': 1}
            if raw_completion['kind'] == "VarDecl":
                completion['abbr'] = "[V] " + raw_completion['completion']
                completion['word'] = raw_completion['completion']
                completion['kind'] = raw_completion['kind']
                completion['menu'] = raw_completion['brief_comment']
            elif raw_completion['kind'] == "ParmDecl":
                completion['kind'] = " ".join(raw_completion['signature'].split(" ")[:-1])
                completion['word'] = raw_completion['completion']
                completion['abbr'] = "[P] " + raw_completion['completion']
                completion['menu'] = raw_completion['brief_comment']
            elif raw_completion['kind'] == "FieldDecl":
                completion['kind'] = " ".join(raw_completion['signature'].split(" ")[:-1])
                completion['word'] = raw_completion['completion']
                completion['abbr'] = "[S] " + raw_completion['completion']
                completion['menu'] = raw_completion['brief_comment']
            elif raw_completion['kind'] == "FunctionDecl":
                completion['kind'] = raw_completion['signature']
                completion['word'] = raw_completion['completion'] + "("
                completion['abbr'] = "[F] " + raw_completion['completion'] + "("
                completion['menu'] = raw_completion['brief_comment']
            elif raw_completion['kind'] == "CXXMethod":
                completion['kind'] = raw_completion['signature']
                completion['word'] = raw_completion['completion'] + "("
                completion['abbr'] = "[M] " + raw_completion['completion'] + "("
                completion['menu'] = raw_completion['brief_comment']
            elif raw_completion['kind'] == "NotImplemented":
                completion['word'] = raw_completion['completion']
                completion['abbr'] = "[K] " + raw_completion['completion']
            else:
                completion['word'] = raw_completion['completion']
                completion['menu'] = raw_completion['brief_comment']
                completion['kind'] = raw_completion['kind']
            completions.append(completion)

        return completions

