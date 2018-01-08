import sys
from . import defs
from . import board
from . import evaluator
from . import book_manager

class _Move(defs.Point):
    def __init__(self, _x = 0, _y = 0, _eval_value = 0):
        super(_Move, self).__init__(_x, _y)
        self.eval_value = _eval_value

class AI(object):
    def __init__(self):
        self.presearch_depth = 3
        self.normal_depth = 5
        self.wld_depth = 15 # 15
        self.perfect_depth = self.wld_depth - 2 # 13
        self.nodes = 0
        self.leaves = 0
        self.current_evaluator = None
        self.evaluators = [None] * evaluator.EVALUATOR_COUNT
        self.evaluators[evaluator.EVALUATOR_WLD] = evaluator.WLDEvaluator()
        self.evaluators[evaluator.EVALUATOR_PERFECT] = evaluator.PerfectEvaluator()
        self.evaluators[evaluator.EVALUATOR_MID] = evaluator.MidEvaluator()

    def move(self, board):
        pass

class AlphaBetaAI(AI):
    def move(self, board):
        _mvs = None
        if defs.CONFIG_USE_BOOKMANAGER:
            bm = book_manager.BookManager()
            bm.read()
            _mvs = bm.find(board)
        else:
            _mvs = board.get_movable_pos()

        movables = []
        for m in _mvs:
            movables.append(defs.Point(m.x, m.y))

        movables_count = len(movables)

        if movables_count == 0:
            board.pass_move()
            return

        if movables_count == 1:
            board.exec_move(movables[0])
            return

        limit = 0

        self.current_evaluator = self.evaluators[evaluator.EVALUATOR_MID]

        if defs.CONFIG_USE_SORTING:
            self.__sort(board, movables, self.presearch_depth)

        if defs.MAX_TURNS - board.get_turns() <= self.wld_depth:
            limit = sys.maxsize
            if defs.MAX_TURNS - board.get_turns() <= self.perfect_depth:
                self.current_evaluator = self.evaluators[evaluator.EVALUATOR_PERFECT]
            else:
                self.current_evaluator = self.evaluators[evaluator.EVALUATOR_WLD]
        else:
            limit = self.normal_depth

        eval_value = 0
        alpha = -sys.maxsize
        beta = sys.maxsize
        p = None # defs.Point()

        for m in movables:
            board.exec_move(m)
            eval_value = -self.__nega_max(board, limit - 1, -beta, -alpha)
            board.undo_move()

            if eval_value > alpha:
                alpha = eval_value
                p = m

        self.current_evaluator = None

        board.exec_move(p)

    def __sort(self, board, movables, limit):
        moves = [] # array of _Move
        for m in movables:
            board.exec_move(m)
            eval_value = -self.__nega_max(board, limit - 1, -sys.maxsize, sys.maxsize)
            board.undo_move()

            move = _Move(m.x, m.y, eval_value)
            moves.append(move)

        moves.sort(key = lambda x: x.eval_value, reverse = True)

        movables.clear()
        for mv in moves:
            movables.append(defs.Point(mv.x, mv.y))

    def __nega_max(self, board, limit, alpha, beta):
        if limit == 0 or board.is_game_over():
            self.leaves += 1
            return self.current_evaluator.evaluate(board)

        self.nodes += 1

        score = 0
        movables = board.get_movable_pos()
        movables_count = len(movables)
        if movables_count == 0:
            board.pass_move()
            score = -self.__nega_max(board, limit, -beta, -alpha)
            board.undo_move()
            return score

        for m in movables:
            board.exec_move(m)
            score = -self.__nega_max(board, limit - 1, -beta, -alpha)
            board.undo_move()

            if score >= beta:
                return score

            alpha = max(alpha, score)

        return alpha
