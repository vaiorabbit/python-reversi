from pathlib import Path
import random

from . import defs
from . import board

class CoordinatesTransformer(object):
    def __init__(self, first):
        self.__rotate = 0
        self.__mirror = False

        if first == defs.Point.from_coord_string("d3"):
            self.__rotate = 1
            self.__mirror = True
        elif first == defs.Point.from_coord_string("c4"):
            self.__rotate = 2
        elif first == defs.Point.from_coord_string("e6"):
            self.__rotate = -1
            self.__mirror = True

    def normalize(self, p):
        new_p = self.__rotate_point(p, self.__rotate)
        if self.__mirror:
            new_p = self.__mirror_point(new_p)
        return new_p

    def denormalize(self, p):
        new_p = defs.Point(p.x, p.y)
        if self.__mirror:
            new_p = self.__mirror_point(new_p)
        new_p = self.__rotate_point(new_p, -self.__rotate)
        return new_p

    def __rotate_point(self, old_point, rotate):
        rotate %= 4
        if rotate < 0:
            rotate += 4

        new_point = defs.Point()

        if rotate == 1:
            new_point.x = old_point.y
            new_point.y = defs.BOARD_SIZE - old_point.x + 1
        elif rotate == 2:
            new_point.x = defs.BOARD_SIZE - old_point.x + 1
            new_point.y = defs.BOARD_SIZE - old_point.y + 1
        elif rotate == 3:
            new_point.x = defs.BOARD_SIZE - old_point.y + 1
            new_point.y = old_point.x
        else: # == 0
            new_point.x = old_point.x
            new_point.y = old_point.y

        return new_point

    def __mirror_point(self, point):
        new_point = defs.Point()

        new_point.x = defs.BOARD_SIZE - point.x + 1
        new_point.y = point.y

        return new_point


class _Node(object):
    def __init__(self):
        self.child = None
        self.sibling = None
        self.point = defs.Point()

class BookManager(object):
    def __init__(self):
        self.reset_root()

    def reset_root(self):
        self.__root = _Node()
        self.__root.point = defs.Point.from_coord_string("f5")

    def read(self, book_filename = "reversi.book"):
        book_file = Path(book_filename)
        if not book_file.exists():
            return -1

        book_count = 0
        with book_file.open() as f:
            book = []
            for line in f:
                for i in range(0, len(line), 2):
                    p = defs.Point()
                    try:
                        mv = line[i:i + 2]
                        p = defs.Point.from_coord_string(mv)
                    except TypeError:
                        break
                    book.append(p)
                    book_count += 1

            self.__add(book)

        return book_count

    def find(self, board):
        node = self.__root
        history = board.get_history()
        if len(history) == 0:
            return board.get_movable_pos()

        first = history[0]
        transformer = CoordinatesTransformer(first)

        normalized = []
        for p in history:
            p = transformer.normalize(p)
            normalized.append(p)

        for i in range(1, len(normalized)):
            p = normalized[i]
            node = node.child
            while node != None:
                if node.point == p:
                    break
                node = node.sibling
            if node == None:
                return board.get_movable_pos()

        if node.child == None:
            return board.get_movable_pos()

        next_move = self.__get_next_move(node)
        next_move = transformer.denormalize(next_move)

        return [next_move]

    def __add(self, book):
        node = self.__root
        for i in range(1, len(book)):
            p = book[i]
            if node.child == None:
                node.child = _Node()
                node = node.child
                node.point.x = p.x
                node.point.y = p.y
            else:
                node = node.child
                while True:
                    if node.point == p:
                        break
                    if node.sibling == None:
                        node.sibling = _Node()
                        node = node.sibling
                        node.point.x = p.x
                        node.point.y = p.y
                        break
                    node = node.sibling

    def __get_next_move(self, node):
        candidates = []
        p = node.child
        while p != None:
            candidates.append(defs.Point(p.point.x, p.point.y))
            p = p.sibling

        index = 0
        if defs.CONFIG_USE_RANDOMIZATION:
            index = random.randint(0, len(candidates) - 1)
        return candidates[index]
