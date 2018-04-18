Glance
======

Highlight stack traces so you can glance at logs or the terminal
to quickly get to the root of an issue.


Usage
-----

Pipe output through `glance` to colorize tracebacks from `stdin`:

```console
$ python examples/example.py 2>&1 | glance
```

Or read from a log file:

```console
$ glance < examples/example.log
```


Example
-------

![Screenshot](artwork/screenshot.png)
