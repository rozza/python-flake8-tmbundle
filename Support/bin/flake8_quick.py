"""
Implementation of the command-line I{pyflakes} tool.
"""
import _ast
import sys
import subprocess
from cStringIO import StringIO
from functools import wraps

from flake8 import pep8
from flake8 import pyflakes
from flake8 import mccabe


def check_all(code_string, filename):
    cleanup_whitespace(filename)
    pyflakes_check(code_string)
    pep8_check(filename)
    mccabe_check(filename)
    return


def cleanup_whitespace(filename):

    f = open(filename)
    lines = f.readlines()
    f.close()

    changed = False
    for linenum in xrange(len(lines) - 1):
        this_line = lines[linenum]
        replacement = this_line.rstrip() + "\n"
        if this_line != replacement:
            changed = True
            lines[linenum] = replacement

    if not changed:
        return

    f = open(filename, "w")
    f.writelines(lines)
    f.close()

    command = """
        osascript -e 'tell app "SystemUIServer" to activate'
                  -e 'tell application "TextMate" to activate'
    """.strip().replace("                  ", ' ').replace("'", "\'").replace("\n", "")
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE);

def capture(warning):
    def captured(fn):
        def wrapped(*args, **kwargs):
                # setup the environment
                backup = sys.stdout

                try:
                    sys.stdout = StringIO()      # capture output
                    fn(*args, **kwargs)
                    out = sys.stdout.getvalue()  # release output
                finally:
                    sys.stdout.close()   # close the stream
                    sys.stdout = backup  # restore original stdout

                out  # captured output wrapped in a string
                if out:
                    print "*" * 72
                    print warning.center(72, " ")
                    print "*" * 72
                    print out
        return wraps(fn)(wrapped)
    return captured


class _PEP8Options(object):
    exclude = select = []
    show_pep8 = show_source = quiet = verbose = testsuite = False
    no_repeat = False
    counters = {}
    messages = {}
    ignore = pep8.DEFAULT_IGNORE


@capture('PyFlakes Errors')
def pyflakes_check(code_string):
    pyflakes.check(code_string, '')


@capture('PEP 8 Errors')
def pep8_check(filename):
    # default pep8 setup
    pep8.options = _PEP8Options()
    pep8.options.physical_checks = pep8.find_checks('physical_line')
    pep8.options.logical_checks = pep8.find_checks('logical_line')
    pep8.args = []

    pep8.input_file(filename)


@capture('Code Complexity')
def mccabe_check(filename):
    mccabe.get_module_complexity(filename, 10)

def main():
    code_string = open(sys.argv[-1], 'r').read()
    filename = sys.argv[-1]

    try:
        compile(code_string.rstrip(), filename, 'exec', _ast.PyCF_ONLY_AST)
    except (SyntaxError, IndentationError):
        value = sys.exc_info()[1]
        try:
            (lineno, offset, line) = value[1][1:]
        except IndexError:
            print >> sys.stderr, 'could not compile %r' % (filename,)
            raise SystemExit
        if line.endswith("\n"):
            line = line[:-1]
        print >> sys.stderr, '%s:%d: could not compile' % (filename, lineno)
        print >> sys.stderr, line
        print >> sys.stderr, " " * (offset - 2), "^"
        raise SystemExit
    else:
        check_all(code_string, filename)


if __name__ == '__main__':
    main()
