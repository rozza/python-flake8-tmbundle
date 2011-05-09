"""
Implementation of the command-line I{pyflakes} tool.
"""
from flake8 import *
import _ast
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

check_all = __import__('flake8.textmate').textmate.check_all


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
