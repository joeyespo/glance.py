import os
import re
import sys

from colorama import Fore, Style, init


LOCATION_PATTERN = 'File "{}", line {}, in {}'
LOCATION_RE = re.compile(LOCATION_PATTERN.format(
    r'(.*)', r'(\d+)', r'(.*)'))


EXAMPLE = """
..Some output text.
..Traceback (most recent call last):
..  File "C:\Users\Joe\Development\Repositories\glance\glanceback.py", line 12, in <module>
..    highlight_traceback()
..TypeError: highlight_traceback() takes exactly 1 argument (0 given)
"""


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    init()

    # Read input
    if args and args[0] == '--':
        s = ' '.join(args[1:])
    elif args:
        # TODO: system call
        pass
    else:
        s = sys.stdin.read()

    # Highlight output
    print(highlight_traceback(s))


def highlight(s, style='', start=0, end=None, bright=True, reset=None):
    # TODO: Background highlighting spanning the terminal length?
    if bright:
        style = Style.BRIGHT + style
    if end is None:
        end = len(s)
    if reset is None:
        reset = Style.RESET_ALL
    return s[:start] + style + s[start:end] + reset + s[end:]


def highlight_traceback(s, cwd=None):
    if cwd is None:
        cwd = os.getcwd()

    # Find traceback string
    index = s.find('Traceback (most recent call last):')
    if index == -1:
        return s

    # Remove left column
    lastnewline = s.rfind('\n', 0, index)
    linestart = index - lastnewline - 1 if lastnewline != -1 else 0
    tracebackstart = index - linestart

    pre = s[:tracebackstart - 1]
    lines = s[tracebackstart:].split('\n')

    # Highlight header
    header = lines.pop(0)
    header = header[:linestart] + highlight(header[linestart:], Fore.RED)

    # Highlight frames
    frames = []
    iterlines = iter(lines[:-1])
    try:
        while True:
            line = iterlines.next()
            column, text = line[:linestart], line[linestart:]
            match = LOCATION_RE.search(text)
            if not match:
                break

            path, ln, module = match.group(1), match.group(2), match.group(3)

            included = path.startswith(cwd)
            if included:
                if path.startswith(cwd):
                    pathindex = len(cwd)
                    if path[pathindex] == os.path.sep:
                        pathindex += 1
                else:
                    pathindex = len(path)
                lo, hi, br = (Style.BRIGHT + Fore.BLACK,
                              Style.DIM + Fore.WHITE,
                              Style.BRIGHT + Fore.WHITE)
                lopath, hipath = path[:pathindex], path[pathindex:]
                # Highlight text
                text = LOCATION_PATTERN.format(
                    lopath + br + hipath + lo,      # Path
                    br + ln + lo,                   # Line number
                    module)                         # Module name
                frames.append(column + lo + text + Style.RESET_ALL)
                # Highlight following line too
                line = iterlines.next()
                column, text = line[:linestart], line[linestart:]
                frames.append(column + hi + text + Style.RESET_ALL)
            else:
                # Lowlight text
                frames.append(column + highlight(text, Fore.RED, bright=False))
                # Lowlight following line too
                line = iterlines.next()
                column, text = line[:linestart], line[linestart:]
                frames.append(column + highlight(text, Fore.RED, bright=False))
    except StopIteration:
        pass

    # Highlight error message
    column, text = lines[-1][:linestart], lines[-1][linestart:]
    #footer = column + highlight(text, Fore.MAGENTA)
    # TODO: Split the colors on the last line?
    footer = column + highlight(text, Fore.MAGENTA)
    if ':' in footer:
        footer = highlight(footer, Fore.WHITE, footer.find(':') + 1)

    # TODO: Look for color escape codes in 'pre' and restore to them
    post = ''

    return '\n'.join([pre, header] + frames + [footer, post])


if __name__ == '__main__':
    main(['--', EXAMPLE.strip()])
