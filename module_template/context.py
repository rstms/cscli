#!/usr/bin/env python3

from pathlib import Path
import sys

class Context():

    entrypoint = Path(__file__).parent.stem

    def __init__(self, quiet, verbose, debug, handler):
        self.quiet = quiet
        self.verbose = verbose
        self.debug = debug

        def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
            if debug:
                debug_hook(exception_type, exception, traceback)
            else:
                if verbose:
                    message = str(exception)
                else:
                    message = str(exception).split('\n')[0]
                handler(f"{exception_type}.{message}")
            sys.exit(-1)
        sys.excepthook = exception_handler

