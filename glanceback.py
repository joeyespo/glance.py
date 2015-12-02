from __future__ import print_function

import os
import re
import sys
from io import StringIO

from colorama import Fore, Style, init

from runner import run


LOCATION_PATTERN = '  File "{}", line {}, in {}'
LOCATION_RE = re.compile(LOCATION_PATTERN.format(
    r'(.*)', r'(\d+)', r'(.*)'))


EXAMPLE = """
..Some output text.
..Traceback (most recent call last):
..  File "C:\Users\Joe\Development\Repositories\glance\glanceback.py", line 12, in <module>
..    highlight_tracebacks()
..TypeError: highlight_tracebacks() takes exactly 1 argument (0 given)
"""


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Initialize colors
    init()

    # Highlight subprocess output
    if args and args[0] != '--':
        run(args, postprocessor=highlight_traceback_lines)
        return

    # Highlight from args or stdin
    if args:
        s = ' '.join(args[1:])
    else:
        s = sys.stdin.read()
    print('\n'.join(highlight_tracebacks(s)))


def highlight(s, style='', start=0, end=None, bright=True, reset=None):
    # TODO: Background highlighting spanning the terminal length?
    if bright:
        style = Style.BRIGHT + style
    if end is None:
        end = len(s)
    if reset is None:
        reset = Style.RESET_ALL
    return s[:start] + style + s[start:end] + reset + s[end:]


def highlight_tracebacks(stream_or_string, cwd=None, encoding='utf-8'):
    if isinstance(stream_or_string, basestring):
        string = stream_or_string
        if isinstance(string, str):
            string = string.decode(encoding)
        stream = StringIO(string)
    else:
        stream = stream_or_string

    # Iterate lines
    lines = iter(stream.readline, '')

    # Strip trailing newline characters
    lines = iter(line[:-1] if line.endswith('\n') else line for line in lines)

    # Highlight line-by-line
    return highlight_traceback_lines(lines)


def highlight_traceback_lines(iterable, cwd=None):
    if cwd is None:
        cwd = os.getcwd()

    # Highlight line-by-line
    lines = iter(iterable)

    # Traceback highlight state machine
    while True:
        textstart = 0

        # Find and highlight header
        while True:
            line = lines.next()
            textstart = line.find('Traceback (most recent call last):')
            if textstart != -1:
                yield line[:textstart] + highlight(line[textstart:], Fore.RED)
                break
            yield line

        # Highlight each frame
        while True:
            line = lines.next()
            column, text = line[:textstart], line[textstart:]
            match = LOCATION_RE.search(text)
            if not match:
                break

            path, lineno, func = match.group(1), match.group(2), match.group(3)

            included = path.startswith(cwd)
            if included:
                pathindex = len(cwd)
                if path[pathindex] == os.path.sep:
                    pathindex += 1
            else:
                pathindex = len(path)

            if included and 'site-packages' in path[pathindex:]:
                included = False

            if included:
                lo, hi, br = (Style.DIM + Fore.RED,
                              Style.DIM + Fore.WHITE,
                              Style.BRIGHT + Fore.RED)
                lopath, hipath = path[:pathindex], path[pathindex:]
                # Highlight text
                text = LOCATION_PATTERN.format(
                    lopath + br + hipath + lo,      # Path
                    br + lineno + lo,               # Line number
                    func)                         # Module name
                yield column + lo + text + Style.RESET_ALL
                # Highlight following line too
                line = lines.next()
                column, text = line[:textstart], line[textstart:]
                yield column + hi + text + Style.RESET_ALL
            else:
                # Lowlight text
                yield column + highlight(text, Fore.RED, bright=False)
                # Lowlight following line too
                line = lines.next()
                column, text = line[:textstart], line[textstart:]
                yield column + highlight(text, Fore.RED, bright=False)

        # Highlight footer
        text = column + highlight(text, Fore.MAGENTA)
        #if ':' in text:
        #    text = highlight(text, Fore.WHITE, text.find(':') + 1)
        yield text


if __name__ == '__main__':
    main(['--', EXAMPLE.strip()])
