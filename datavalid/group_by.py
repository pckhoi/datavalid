class GroupBy(object):
    def __init__(self, columns: str or list) -> None:
        if type(columns) is list:
            self._columns = columns
        else:
            self._columns = [columns]
