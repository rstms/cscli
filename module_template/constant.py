import enum

class Constant(enum.IntEnum):

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

class Status(Constant):
    pass

status = Status('status', 'OK ERROR')
