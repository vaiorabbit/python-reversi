CONFIG_USE_RANDOMIZATION = False
CONFIG_USE_BOOKMANAGER = False
CONFIG_USE_SORTING = True

####################################################################################################

BOARD_SIZE = 8
MAX_TURNS = 60

EMPTY = 0
WHITE = -1
BLACK = 1
WALL  = 2

class Point(object):
    def __init__(self, _x = 0, _y = 0.0):
        self.x = _x
        self.y = _y

    @classmethod
    def from_coord_string(cls, coordstr):
        if len(coordstr) != 2:
            raise TypeError

        x = ord(coordstr[0]) - ord('a') + 1
        y = ord(coordstr[1]) - ord('1') + 1
        if x <= 0 or x > BOARD_SIZE or y <= 0 or y > BOARD_SIZE:
            raise TypeError

        return cls(x, y)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            if self.x != other.x:
                return False
            if self.y != other.y:
                return False
            return True
        else:
            return False

    def coord_string(self):
        coordstr = "{}{}".format(chr(ord('a') + self.x - 1), chr(ord('1') + self.y - 1))
        return coordstr


class Disc(Point):
    def __init__(self, _x = 0, _y = 0, _color = EMPTY):
        super(Disc, self).__init__(_x, _y)
        self.color = _color


class ColorStorage(object):
    def __init__(self, _storage_type):
        self.srorage_type = _storage_type
        self.data = [_storage_type(), _storage_type(), _storage_type()]

    def __getitem__(self, color):
        return self.data[color + 1]

    def __setitem__(self, color, item):
        self.data[color + 1] = item

    def __iadd__(self, other):
        if isinstance(self, other.__class__) == False:
            raise TypeError

        self.data[0] += other.data[0]
        self.data[1] += other.data[1]
        self.data[2] += other.data[2]

        return self
