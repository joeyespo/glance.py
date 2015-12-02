from __future__ import print_function

import os
import signal
import sys
from Queue import Queue, Empty
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep


def _reader(stream, io_queue):
    for line in iter(stream.readline, ''):
        if line.endswith('\n'):
            line = line[:-1]
        io_queue.put(line)
    if not stream.closed:
        stream.close()


def _output_generator(io_queue, checker_thread):
    while True:
        try:
            yield io_queue.get_nowait()
        except Empty:
            if not checker_thread.is_alive():
                break
            sleep(0.3)


def _printer(io_queue, checker_thread, postprocessor):
    generator = _output_generator(io_queue, checker_thread)
    if postprocessor:
        generator = postprocessor(generator)
    for line in generator:
        print(line)


def _checker(process):
    while True:
        if process.poll() is not None:
            break
        sleep(0.5)


def run(args, cwd=None, postprocessor=None):
    io_queue = Queue()

    # Set environment, disabling Python buffering of the subprocess
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = 'True'

    # Set platform-specific arguments
    kwargs = {}
    if sys.platform == 'win32':
        from subprocess import CREATE_NEW_PROCESS_GROUP
        # Use a new process group
        kwargs['creationflags'] = CREATE_NEW_PROCESS_GROUP
        # Prevent "Terminate batch job (Y/N)?"
        kwargs['stdin'] = open(os.devnull, 'r')

    # Run process
    process = Popen(
        args, env=env, shell=True, stdout=PIPE, stderr=PIPE, **kwargs)

    # Create and start all listening threads
    stdout_thread = Thread(target=_reader, args=[process.stdout, io_queue])
    stdin_thread = Thread(target=_reader, args=[process.stderr, io_queue])
    checker_thread = Thread(target=_checker, args=[process])
    printer_thread = Thread(target=_printer,
                            args=[io_queue, checker_thread, postprocessor])
    stdout_thread.start()
    stdin_thread.start()
    checker_thread.start()
    printer_thread.start()

    # Wait for keyboard interrupt
    while checker_thread.is_alive():
        try:
            sleep(0.5)
        except KeyboardInterrupt:
            break

    # Gracefully terminate and show output from cleanup
    term_signal = (
        signal.CTRL_BREAK_EVENT if sys.platform == 'win32' else signal.SIGTERM)
    while True:
        try:
            process.send_signal(term_signal)
            printer_thread.join()
            break
        except KeyboardInterrupt:
            continue
