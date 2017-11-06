import traceback


def error(vim, expr):
    vim.command("echom(\"[rtags] %s \")" % str(expr).replace("\"", "\\\""))
    log("[error] %s" % str(expr))


def on_error(vim, err):
    for line in traceback.format_exc().splitlines():
        error(vim, str(line))
    error(vim, '%s.  Use :messages for error details.' % str(err))


def log(msg):
    with open('/tmp/pylog', 'a') as f:
        f.write(str(msg) + "\n")
