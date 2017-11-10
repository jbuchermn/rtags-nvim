import traceback


def error(vim, expr):
    vim_log(vim, expr)
    log("[error] %s" % str(expr))


def vim_log(vim, expr):
    expr = str(expr)
    for line in expr.splitlines():
        vim.command("echom(\"[rtags] %s \")" % line.replace("\"", "''"))  # replace("\"", "\\\"") does not work


def on_error(vim, err):
    for line in traceback.format_exc().splitlines():
        error(vim, str(line))
    error(vim, '%s. See :messages' % str(err))


def log(msg):
    with open('/tmp/pylog', 'a') as f:
        f.write(str(msg) + "\n")
