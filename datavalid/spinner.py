import sys
import time
import threading


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏':
                yield cursor

    def __init__(self, text: str, delay=None, indent=0):
        self._spinner_generator = self.spinning_cursor()
        self._text = text
        self._indent = indent
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            if self._indent > 0:
                sys.stdout.write(" "*self._indent)
            sys.stdout.write(next(self._spinner_generator))
            sys.stdout.write(" %s" % self._text)
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\r%s\r' % ' '*(self._indent+len(self._text)+2))
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False
