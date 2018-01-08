import sys

import Reversi

class UndoException(Exception):
    def __init__(self):
        pass

class ExitException(Exception):
    def __init__(self):
        pass

class GameOverException(Exception):
    def __init__(self):
        pass


class Player(object):
    def __init__(self):
        pass

    def on_turn(self, board):
        pass

class HumanPlayer(Player):
    def on_turn(self, board):
        movables = board.get_movable_pos()
        if len(movables) == 0:
            print("You must pass this turn.")
            board.pass_move()
            return

        while True:
            user_input = input("Input your next move: ")
            if user_input == "u":
                raise UndoException()
            if user_input == "x":
                raise ExitException()

            p = Reversi.defs.Point()
            try:
                parsed_point = Reversi.defs.Point.from_coord_string(user_input)
                p = parsed_point
            except TypeError:
                print("Error: Your move must be given as a coord-string (c4, d3, etc.) .")
                continue

            if board.exec_move(p) == False:
                print("Error: You can't put there now.")
                continue

            if board.is_game_over():
                raise GameOverException()

            break


class AIPlayer(Player):
    def __init__(self):
        self.ai = Reversi.ai.AlphaBetaAI()

    def on_turn(self, board):
        print("Thinking...->", end = '')
        self.ai.move(board)
        print("Done.")
        if board.is_game_over():
            raise GameOverException()


class ConsoleBoard(Reversi.board.Board):
    def print_board(self):
        row_str = ["a ", "b ", "c ", "d ", "e ", "f ", "g ", "h "]
        print("  ", end = '')
        for x in range(0, Reversi.defs.BOARD_SIZE):
            print(row_str[x], end = '')
        print("")

        col_str = ["1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 "]
        for y in range(1, Reversi.defs.BOARD_SIZE + 1):
            print("{}".format(col_str[y - 1]), end = '')
            for x in range(1, Reversi.defs.BOARD_SIZE + 1):
                c = self.get_color(Reversi.defs.Point(x, y))
                if c == Reversi.defs.BLACK:
                    print("● ", end = '') # U+25cf
                elif c == Reversi.defs.WHITE:
                    print("○ ", end = '') # U+25cb
                else:
                    print("  ", end = '')
            print("")

if __name__ == '__main__':
    player = []
    current_player = 0
    board = ConsoleBoard()
    reverse = False

    if reverse:
        player.append(HumanPlayer())
        player.append(AIPlayer())
    else:
        player.append(AIPlayer())
        player.append(HumanPlayer())

    try:
        while True:
            board.print_board()
            print("Black {}  White {}  Empty {}".format(board.count_disc(Reversi.defs.BLACK), board.count_disc(Reversi.defs.WHITE), board.count_disc(Reversi.defs.EMPTY)))
            print("Turn : {} (#Turns={})".format("Black" if board.get_current_color() == Reversi.defs.BLACK else "White", board.get_turns()))
            movables = board.get_movable_pos()
            for m in movables:
                print("{} ".format(m.coord_string()), end = '')
            print("")
            try:
                player[current_player].on_turn(board)
            except UndoException:
                while True:
                    board.undo_move()
                    board.undo_move()
                    movables = board.get_movable_pos()
                    if len(movables) != 0:
                        break
            except ExitException:
                exit()
            except GameOverException:
                print("----------------Game Over-----------------")
                board.print_board()
                print("Black {}  White {}  Empty {}".format(board.count_disc(Reversi.defs.BLACK), board.count_disc(Reversi.defs.WHITE), board.count_disc(Reversi.defs.EMPTY)))
                exit()

            current_player += 1
            current_player %= 2
    except (KeyboardInterrupt, EOFError):
        print("\n\n---------------Shutting Down--------------\n")
    finally:
        pass
