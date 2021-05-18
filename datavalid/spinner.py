import sys
import time
import threading


class Spinner:
    """Displays a spinner at an indentation with some text to the terminal

    Example:
        >>> with Spinner("processing..."):
        ...     # do stuffs
    """
    _busy = False
    _delay = 0.1

    @staticmethod
    def _spinning_cursor():
        while 1:
            for cursor in '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏':
                yield cursor

    def __init__(self, text: str, delay=None, indent=0):
        """Creates a new instance of Spinner

        Args:
            text (str):
                the text to display next to spinner
            delay (float):
                duration in seconds before the spinning cursor should
                change to the next frame. Defaults to 0.1
            indent (int):
                number of spaces before the spinning cursor. Defaults
                to 0

        Returns:
            no value
        """
        self._spinner_generator = self._spinning_cursor()
        self._text = text
        self._indent = indent
        if delay and float(delay):
            self._delay = delay

    def _spinner_task(self):
        while self._busy:
            if self._indent > 0:
                sys.stdout.write(" "*self._indent)
            sys.stdout.write(next(self._spinner_generator))
            sys.stdout.write(" %s" % self._text)
            sys.stdout.flush()
            time.sleep(self._delay)
            sys.stdout.write('\r%s\r' % ' '*(self._indent+len(self._text)+2))
            sys.stdout.flush()

    def __enter__(self):
        self._busy = True
        threading.Thread(target=self._spinner_task).start()

    def __exit__(self, exception, value, tb):
        self._busy = False
        time.sleep(self._delay)
        if exception is not None:
            return False
