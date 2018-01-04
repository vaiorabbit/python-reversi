import sys

import Reversi

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
    board = ConsoleBoard()
    try:
        while True:
            board.print_board()
            print("Black {}  White {}  Empty {}".format(board.count_disc(Reversi.defs.BLACK), board.count_disc(Reversi.defs.WHITE), board.count_disc(Reversi.defs.EMPTY)))
            movables = board.get_movable_pos()
            for m in movables:
                print("{} ".format(m.coord_string()), end = '')
            print("")

            # Should be "e3, d2, ..", "p" (pass) or "u" (undo).
            user_input = input("Input your next move: ")
            p = Reversi.defs.Point()

            if user_input == "p": # Pass
                if not board.pass_move():
                    print("Error: You can't pass now.", file=sys.stderr)
                    continue

            if user_input == "u": # Undo
                board.undo_move()
                continue

            try:
                parsed_point = Reversi.defs.Point.from_coord_string(user_input)
                p = parsed_point
            except TypeError:
                print("Error: Your move must be given as a coord-string (c4, d3, etc.) .", file=sys.stderr)
                continue

            if board.exec_move(p) == False:
                print("Error: You can't put there now.", file=sys.stderr)
                continue

            if board.is_game_over():
                print("----------------Game Over-----------------")

    except KeyboardInterrupt:
        print("\n---------------Shutting Down--------------\n")
