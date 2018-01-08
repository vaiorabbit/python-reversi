import copy
from . import defs
from . import board

EVALUATOR_WLD = 0
EVALUATOR_PERFECT = 1
EVALUATOR_MID = 2
EVALUATOR_COUNT = 3

class Evaluator(object):
    def evaluate(self, board):
        pass

class WLDEvaluator(Evaluator):
    WIN = 1
    DRAW = 0
    LOSE = -1

    def evaluate(self, board):
        disc_diff = board.get_current_color() * (board.count_disc(defs.BLACK) - board.count_disc(defs.WHITE))
        if disc_diff > 0:
            return WLDEvaluator.WIN
        elif disc_diff < 0:
            return WLDEvaluator.LOSE
        else:
            return WLDEvaluator.DRAW

class PerfectEvaluator(Evaluator):

    def evaluate(self, board):
        disc_diff = board.get_current_color() * (board.count_disc(defs.BLACK) - board.count_disc(defs.WHITE))
        return disc_diff


class _EdgeParam(object):
    def __init__(self):
        self.stable = 0
        self.wing = 0
        self.mountain = 0
        self.c_move = 0

    def __iadd__(self, other):
        if isinstance(self, other.__class__) == False:
            raise TypeError

        self.stable += other.stable
        self.wing += other.wing
        self.mountain += other.mountain
        self.c_move += other.c_move

        return self

class _CornerParam(object):
    def __init__(self):
        self.corner = 0
        self.x_move = 0

class _Weight(object):
    def __init__(self):
        self.mobility_w = 67
        self.liberty_w = -13
        self.stable_w = 101
        self.wing_w = -308
        self.x_move_w = -449
        self.c_move_w = -552

class MidEvaluator(Evaluator):

    TABLE_SIZE = 3 ** 8

    def __init__(self):
        line = [0] * defs.BOARD_SIZE
        self.__edge_table = [defs.ColorStorage(_EdgeParam)] * MidEvaluator.TABLE_SIZE
        self.__generate_edge(line, 0)
        for i in range(0, MidEvaluator.TABLE_SIZE):
            t = self.__edge_table[i][defs.BLACK]
            t = self.__edge_table[i][defs.WHITE]

        self.__eval_weight = _Weight()

    def evaluate(self, board):
        edge_stat  = copy.deepcopy(self.__edge_table[self.__idx_top(board)])
        edge_stat += self.__edge_table[self.__idx_bottom(board)]
        edge_stat += self.__edge_table[self.__idx_right(board)]
        edge_stat += self.__edge_table[self.__idx_left(board)]

        corner_stat = self.__eval_corner(board)

        edge_stat[defs.BLACK].stable -= corner_stat[defs.BLACK].corner
        edge_stat[defs.WHITE].stable -= corner_stat[defs.WHITE].corner

        result = \
                   edge_stat[defs.BLACK].stable * self.__eval_weight.stable_w \
                 - edge_stat[defs.WHITE].stable * self.__eval_weight.stable_w \
                 + edge_stat[defs.BLACK].wing * self.__eval_weight.wing_w \
                 - edge_stat[defs.WHITE].wing * self.__eval_weight.wing_w \
                 + corner_stat[defs.BLACK].x_move * self.__eval_weight.x_move_w \
                 - corner_stat[defs.WHITE].x_move * self.__eval_weight.x_move_w \
                 + edge_stat[defs.BLACK].c_move * self.__eval_weight.c_move_w \
                 - edge_stat[defs.WHITE].c_move * self.__eval_weight.c_move_w

        if self.__eval_weight.liberty_w != 0:
            liberty = self.__count_liberty(board)
            result += liberty[defs.BLACK] * self.__eval_weight.liberty_w
            result -= liberty[defs.WHITE] * self.__eval_weight.liberty_w


        result += board.get_current_color() * len(board.get_movable_pos()) * self.__eval_weight.mobility_w

        ret = board.get_current_color() * result

        return ret

    def __generate_edge(self, edge, count):
        if count == defs.BOARD_SIZE:
            stat = defs.ColorStorage(_EdgeParam)
            idx = self.__idx_line(edge)
            stat[defs.BLACK] = self.__eval_edge(edge, defs.BLACK)
            stat[defs.WHITE] = self.__eval_edge(edge, defs.WHITE)
            self.__edge_table[idx] = stat

            return

        edge[count] = defs.EMPTY
        self.__generate_edge(edge, count + 1)

        edge[count] = defs.BLACK
        self.__generate_edge(edge, count + 1)

        edge[count] = defs.WHITE
        self.__generate_edge(edge, count + 1)

    def __eval_edge(self, line, color):
        edge_param = _EdgeParam()
        x = 0

        if line[0] == defs.EMPTY and line[7] == defs.EMPTY:
            x = 2
            while x <= 5:
                if line[x] != color:
                    break;
                x += 1
            if x == 6:
                if line[1] == color and line[6] == defs.EMPTY:
                    edge_param.wing = 1
                elif line[1] == defs.EMPTY and line[6] == color:
                    edge_param.wing = 1
                elif line[1] == color and line[6] == color:
                    edge_param.mountain = 1
            else:
                if line[1] == color:
                    edge_param.c_move += 1
                if line[6] == color:
                    edge_param.c_move += 1

        for i in range(0, 8):
            if line[i] != color:
                break
            edge_param.stable += 1

        if edge_param.stable < 8:
            for i in range(7, 0, -1):
                if line[i] != color:
                    break
                edge_param.stable += 1

        return edge_param

    def __eval_corner(self, board):
        corner_stat = defs.ColorStorage(_CornerParam)
        corner_stat[defs.BLACK].corner = 0
        corner_stat[defs.BLACK].x_move = 0
        corner_stat[defs.WHITE].corner = 0
        corner_stat[defs.WHITE].x_move = 0

        c = board.get_color(defs.Point(1, 1))
        corner_stat[c].corner += 1
        if c == defs.EMPTY:
            corner_stat[board.get_color(defs.Point(2, 2))].x_move += 1

        c = board.get_color(defs.Point(1, 8))
        corner_stat[c].corner += 1
        if c == defs.EMPTY:
            corner_stat[board.get_color(defs.Point(2, 7))].x_move += 1

        c = board.get_color(defs.Point(8, 8))
        corner_stat[c].corner += 1
        if c == defs.EMPTY:
            corner_stat[board.get_color(defs.Point(7, 7))].x_move += 1

        c = board.get_color(defs.Point(8, 1))
        corner_stat[c].corner += 1
        if c == defs.EMPTY:
            corner_stat[board.get_color(defs.Point(7, 2))].x_move += 1

        return corner_stat

    def __idx_top(self, board):
        index = 0
        for i in range(1, defs.BOARD_SIZE + 1):
            index += (3 ** (defs.BOARD_SIZE - i)) * (board.get_color(defs.Point(i, 1)) + 1)
        return index

    def __idx_bottom(self, board):
        index = 0
        for i in range(1, defs.BOARD_SIZE + 1):
            index += (3 ** (defs.BOARD_SIZE - i)) * (board.get_color(defs.Point(i, 8)) + 1)
        return index

    def __idx_right(self, board):
        index = 0
        for i in range(1, defs.BOARD_SIZE + 1):
            index += (3 ** (defs.BOARD_SIZE - i)) * (board.get_color(defs.Point(8, i)) + 1)
        return index

    def __idx_left(self, board):
        index = 0
        for i in range(1, defs.BOARD_SIZE + 1):
            index += (3 ** (defs.BOARD_SIZE - i)) * (board.get_color(defs.Point(1, i)) + 1)
        return index

    def __count_liberty(self, board):
        liberty = defs.ColorStorage(int)
        liberty[defs.BLACK] = 0
        liberty[defs.WHITE] = 0
        liberty[defs.EMPTY] = 0
        for x in range(1, defs.BOARD_SIZE + 1):
            for y in range(1, defs.BOARD_SIZE + 1):
                p = defs.Point(x, y)
                liberty[board.get_color(p)] += board.get_liberty(p)

        return liberty

    def __idx_line(self, l):
        idx = 0
        for i in range(0, 8):
            idx = 3 * idx + (l[i] + 1)
        return idx
