class BadConfigError(Exception):
    path: list[str or int]
    msg: str

    def __init__(self, path: list[str or int], msg: str) -> None:
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
