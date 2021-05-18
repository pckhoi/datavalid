class BadConfigError(Exception):
    """Raised when config object (a dictionary) has error

    This error also records the `path` of where in the object the error
    has occured.

    Attributes
        path (list[str or int]):
            path of the offending field
        msg (str):
            the error message at `path`
    """
    path: list[str or int]
    msg: str

    def __init__(self, path: list[str or int], msg: str) -> None:
        """Creates a new instance of BadConfigError

        Args:
            path (list[str or int]):
                path of offending field. Path may be an empty list if
                the error message is not nested deep inside the config
                object.
            msg (str):
                the error message at `path`.

        Returns:
            no value
        """
        super().__init__(path, msg)
        self.path = path
        self.msg = msg

    def __str__(self) -> str:
        if len(self.path) == 0:
            return self.msg
        sl = list()
        for key in self.path:
            if type(key) is int:
                sl.append('[%d]' % key)
            elif ' ' in str(key):
                sl.append('."%s"' % key)
            else:
                sl.append('.%s' % key)
        return 'error at %s: %s' % (''.join(sl), self.msg)
